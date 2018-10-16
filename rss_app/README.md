## Overview

`rss_app` is a standalone program dedicated to parse rss feeds and store posts, users and tags data into database

## Requirements

1. Python >=3.5
2. Additional packages (see [setup.py](setup.py))


## Install

```bash
[>] python setup.py install
[>] python setup.py test
```


## Usage

Command line options:

```bash
[>] rss_app -h
usage: rss_app [-h] [--db DB] [-p PERIOD] [--rss RSS] [-g GRAPH]

periodically parse rss feeds to database

optional arguments:
  -h, --help            show this help message and exit
  --db DB               db url (default: sqlite:///db.sqlite)
  -p PERIOD, --period PERIOD
                        fequency of fetching new feeds, in munutes (default:
                        1)
  --rss RSS             rss urls to parse (default:
                        ['https://www.reddit.com/r/news/.rss',
                        'https://habr.com/rss/hubs/all/'])
  -g GRAPH, --graph GRAPH
                        path where to save flow graph (default: )
```

Run:

```bash
[>] rss_app
2018-10-16 08:24:30 (rss parser) [INFO]: Parameters:
2018-10-16 08:24:30 (rss parser) [INFO]: 	db: sqlite:///db.sqlite
2018-10-16 08:24:30 (rss parser) [INFO]: 	period: 1 minutes
2018-10-16 08:24:30 (rss parser) [INFO]: 	rss:
2018-10-16 08:24:30 (rss parser) [INFO]: 	 - https://www.reddit.com/r/news/.rss
2018-10-16 08:24:30 (rss parser) [INFO]: 	 - https://habr.com/rss/hubs/all/
2018-10-16 08:24:30 (rss parser) [INFO]: 	graph: no set
2018-10-16 08:24:30 (rss parser) [INFO]: Open database from 'sqlite:///db.sqlite'
2018-10-16 08:24:30 (rss parser) [INFO]: Start loop
2018-10-16 08:24:30 (rss parser) [INFO]: Parse 'https://www.reddit.com/r/news/.rss'
2018-10-16 08:24:31 (rss parser) [INFO]: Parse 'https://habr.com/rss/hubs/all/'
...
```


## DB scheme

SQLAlchemy framework used. One can find database scheme used in [rss_app/model.py](rss_app/model.py).


## Workflow

`feedparser` package is used to parse rss feed into in-memory hierarchical document. Then `flow`
package is used to map this document into SQL models, see [rss_app/workflow.py](rss_app/workflow.py)
for details. One can plot workflow graph by using `--graph` command line argument. The workflow used in
`rss_app` can be found here: [etc/workflow.pdf](etc/workflow.pdf)
