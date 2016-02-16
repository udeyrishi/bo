#Bo
Bo is a sentiment analysis web crawler that crawls all the webpages that it can find starting at the configured root URLs, and then analyses the sentiments on these pages. The bundled sentiment and tag info can then be stored/processed for further downstream actions.

Bo stays on the same domains as the root URLs, so as to get the results only from the specified websites. This prevents Bo from wandering off into unwanted locations on the web.

##Dependecies
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
$ scrapy crawl bo
```

If you use IntelliJ based IDEs, and want to debug Bo using it, see this [StackOverflow guide](http://stackoverflow.com/questions/21788939/how-to-use-pycharm-to-debug-scrapy-projects).

##Configuring
Bo allows you to specify some settings in bo/bo/settings.py. Here's what they mean:

* START\_URLS\_FILE: Path to the CSV file (Excel format) that contains the start URLs and the allowed domains. The first row contains the column titles. It should contain either 'Node' or 'URL' columns, or both (at least). If both are present, the Node is used as the allowed domain name, URL as a root URL. If just Node is present, then it is used as both root URL and domain. Else if just URL is present, the URL is added as a root URL, and no addition is made to the allowed domains (i.e., this URL might get ignored if the corresponding domain was not previously added). All other fields, if any, will be bundled as the 'metadata' field in the final processed item sent downstream to the storage stages.
* TAGS\_FILE: The file containing all the tags that need to be matched with the tags in the webpage. One tag per line.
* ALCHEMY\_API\_KEY: The Alchemy API key. Registere [here](http://www.alchemyapi.com/api/register.html).
* TAG\_MATCH\_THRESHOLD: The minimum number of tags (keywords + entities + concepts) to be matched (completely or partially), else the webpage will be dropped.
* RELEVANCE\_THRESHOLD: The tags with relevance less than this value will be dropped and will not be used for TAG\_MATCH\_THRESHOLD verification, and will also not be bundled in the final storage object.
* MONGO\_DATABASE: The MongoDB name, if MongoStorageStage is being used.
* MONGO\_URI: The MongoDB URI, if MongoStorageStage is being used.
* MONGO\_COLLECTION\_NAME: The MongoDB collection, if MongoStorageStage is being used.
* OUTPUT_FILE: The path to the output file, if JsonFileWriterStage is being used.
* ALCHEMY\_API\_RETRY\_DELAY\_MINUTES: The duration (in minutes) for which Bo will be suspended before retrying if Alchemy API's daily transaction limit is reached.
