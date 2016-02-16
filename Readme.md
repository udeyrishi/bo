###Notes:
1. Domain names restricted by node names, so as to prevent Bo to start crawling everything on the web!
   Drawback: some websites use different domain names, and some might be filtered out.
             e.g.: www.ipcc-wg2.gov will be blocked when www.ipcc.org was in the domains

             You might want to visit the external page (it's a externally cited page),
             but it will be blocked out.

             Design your CSV appropriately.

###Dependencies
1. Python 2 and pip (Built and tested on Python 2.7)
2. [PyMongo](https://api.mongodb.org/python/current/installation.html)

    ```sh
    $ python -m pip install pymongo
    ```
3. [Scrapy](http://scrapy.org/)

    ```sh
    $ python -m pip install scrapy
    ```
4. [Requests](http://docs.python-requests.org/en/latest/user/install/)

    ```sh
    $ python -m pip install requests
    ```
5. [Alchemy Python SDK](http://www.alchemyapi.com/developers/getting-started-guide/using-alchemyapi-with-python)
    -included as a git submodule

    ```sh
    # If not cloned yet:
    $ git clone --recursive https://github.com/udeyrishi/Bo

    # If already cloned:
    $ cd Bo
    $ git submodule init && git submodule update
    ```

6. [Pause](https://pypi.python.org/pypi/pause/0.1.2)

    ```sh
    python -m pip install pause
    ```

###Running
```sh
$ scrapy crawl bo
```

###IntelliJ Idea/PyCharm support

Use [this](http://stackoverflow.com/questions/21788939/how-to-use-pycharm-to-debug-scrapy-projects) to setup the run configuration to get debugging in the IDE with some modifications:

1. Set the script parameters as:

    ```
    crawl bo
    ```

2. Set working directory to the path to the repo

###Filtering ideas:
1. Extract named entities/proper nouns such as places, people, organizations, etc. and match them against a predefined set of keywords. If the number of matched elements >= N, proceed with the analysis. If yes, what keywords should be used, and do you have an initial value of N?
2. Extract keywords and do the same, but these keywords can be anything (not just named entities). Most likely, this is a superset of above.
3. Look for matching concepts (text) that the Watson computer thinks relate to a particular page, even if these concepts didn’t necessarily appear in the page. Pick only the concepts with relevance >= threshold F. Match these concepts like 1.

###Processing ideas:
Applies only the filtered pages:
1. The keywords + entity filters already should have sentiments attached for these words.
Pass them along. Then find a sentiment for the entire page.
Targetted sentiments are not useful, as the keyword + entity search in filtering stage should give the corresponding sentiments.

=> Combine the keyword, entity, page sentiments into 1 score 0-1. Put individual ones in the DTO, and use the global score.
2. [CREATE MONGO DTO] Extract author. Check for return status to be 'ERROR'
3. [CREATE MONGO DTO] Extract category
