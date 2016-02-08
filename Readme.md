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