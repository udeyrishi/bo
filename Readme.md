#Bo
Bo is a sentiment analysis web crawler that crawls all the webpages that it can find starting at the configured root URLs, and then analyses the sentiments on these pages. The bundled sentiment and tag info can then be further stored/processed for downstream actions.

Bo stays on the same domains as the root URLs, so as to get the results only from the specified websites. This prevents Bo from wandering off into unwanted locations on the web.

##Dependencies
Bo is built using Python 2 (tested on 2.7.11), and uses [Scrapy](http://scrapy.org/) for web crawling. The NLP is done using [Alchemy API](http://www.alchemyapi.com/developers/getting-started-guide/using-alchemyapi-with-python). To see all the dependencies, see /requirements.txt. Install dependecies like this:

```sh
# Install all pip requirements
$ pip install -r requirements.txt

# Install Python Alchemy API (submodule)
$ git submodule init && git submodule update
```

##Running
Ensure that you've configured bo/bo/settings.py properly (see 'Configuration' below), and then start Bo as a scrapy crawler like this:

```sh
# Run Bo from the source directory 'bo'
$ cd bo
$ scrapy crawl bo
```

If you use IntelliJ based IDEs, and want to debug Bo using it, see this [StackOverflow guide](http://stackoverflow.com/questions/21788939/how-to-use-pycharm-to-debug-scrapy-projects).

##Configuring
Bo allows you to specify some settings in bo/bo/settings.py. Here's what they mean:

* START\_URLS\_FILE: Path to the CSV file (Excel format) that contains the start URLs and the allowed domains. The first row contains the column titles. It should contain either 'Node' or 'URL' columns, or both (at least). If both are present, then the Node is used as an allowed domain name, and the URL as a root URL. If just Node is present, then it is used as both a root URL and an allowed domain. Else if just URL is present, then it is added as a root URL, and no addition is made to the list of allowed domains (i.e., this URL might get ignored if the corresponding domain was not previously added). All other fields, if any, will be bundled as the 'metadata' field in the final processed item sent downstream to the storage stages (See 'Outputs' section below). See [sample CSV](https://github.com/udeyrishi/bo/blob/master/sample-config-files/urls.csv).
* TAGS\_FILE: The file containing all the tags that should be matched with the tags in the webpage. One tag per line. See [sample](https://github.com/udeyrishi/bo/blob/master/sample-config-files/keywords.txt).
* ALCHEMY\_API\_KEY: The Alchemy API key. Registere [here](http://www.alchemyapi.com/api/register.html).
* TAG\_MATCH\_THRESHOLD: The minimum number of tags (keywords + entities + concepts) to be matched (completely or partially), else the webpage will be dropped.
* RELEVANCE\_THRESHOLD: The tags with relevance less than this value will be dropped, and will not be used for TAG\_MATCH\_THRESHOLD verification, and will also not be bundled in the final storage object.
* MONGO\_DATABASE: The MongoDB name, if MongoStorageStage is being used.
* MONGO\_URI: The MongoDB URI, if MongoStorageStage is being used.
* MONGO\_COLLECTION\_NAME: The MongoDB collection, if MongoStorageStage is being used.
* OUTPUT_FILE: The path to the output file, if JsonFileWriterStage is being used.
* ALCHEMY\_API\_RETRY\_DELAY\_MINUTES: The duration (in minutes) for which Bo will be suspended before retrying if Alchemy API's daily transaction limit is reached.

##Outputs
Bo is built using the Scrapy [pipeline](https://github.com/udeyrishi/bo/blob/master/sample-config-files/keywords.txt) model, where it goes through a sequence of processing stages and ultimately reaches the PackagingStage (see 'ITEM_PIPELINES' in settings.py). This packaging stage packs up the info gathered so far into a useful data transfer object, which is sent down to the next stage--usually a data storage stage (JsonFileWriterStage, MongoStorageStage, or potentially others). This DTO (BoPackagedItem) is essentially Bo's output for a web page, given that it wasn't dropped based on the way Bo was configured (see 'Configuration' above). A sample output BoPackagedItem would look like this:

```
{
	'url': 'http://www.myawesomesite.com/mypage',
	'language': 'english',
	'category': 'technology',
	'metadata': {
		'my_csv_extra_field1': 'val1',
		'my_csv_extra_field2': 'val2'
	},
	'doc_sentiment': {
		'mixed': false,
		'score': 0.923,
		'type': 'positive'
	},
	'tags': {
		'tag1': {
			'count': 3,
			'relevance': 0.671,
			'sentiment': 0.9,
			'mixed': false,
			'matched': 'yes'
		},
		'tag2': {
			'count': 1,
			'relevance': 0.921,
			'sentiment': -0.9,
			'mixed': false,
			'matched': 'no'
		},
		'tag3': {
			'count': 7,
			'relevance': 0.981,
			'sentiment': 0,
			'mixed': true,
			'matched': 'partial'
		}
	}
}
```
Here, 'metadata' contains values of all the extra columns that were put in the START\_URLS\_FILE. The doc\_sentiment field corresponds to the corresponding [Alchemy API](http://www.alchemyapi.com/api/sentiment/urls.html). The tags field contains all the keywords, entities, or concepts that were found in the page that had a relevance score of at least RELEVANCE\_THRESHOLD. A complete matching with a tag in the TAGS_FILE implies a matched 'yes', else a 'no'. Bo also tries to split all the multi-word tags in the TAGS\_FILE and the found tags into individual words, and then tries to match them. If a match happens this way, it's called a 'partial' match.

##Licence
Bo is licensed under the Apache License, v2.0. See [this](https://github.com/udeyrishi/bo/blob/master/LICENSE) for details.