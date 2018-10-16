import argparse
import feedparser
import logging
from flow import ORMSessionSQLAlchemy
from flow.plot import ActionsPlotter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import time
from .model import Base
from .workflow import feed_extractor


logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s (%(name)s) [%(levelname)s]: '
                    '%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('rss parser')


def parse_args():
    default_rss = [
        'https://www.reddit.com/r/news/.rss',
        'https://habr.com/rss/hubs/all/',
    ]
    parser = argparse.ArgumentParser(description='periodically parse rss feeds to database',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--db', type=str, default='sqlite:///db.sqlite', help='db url')
    parser.add_argument('-p', '--period', type=int, default=1, help='fequency of fetching new feeds, in munutes')
    parser.add_argument('--rss', type=str, default=default_rss, action='append', help='rss urls to parse')
    parser.add_argument('-g', '--graph', type=str, default='', help='path where to save flow graph')
    return parser.parse_args()


def complete_args(settings):
    if settings.graph.endswith('.pdf'):
        settings.graph = settings.graph[:-4]


def validate_args(settings):
    if settings.period < 1:
        raise ValueError('period should be > 0 (got: {})'.format(settings.period))
    if not settings.rss:
        raise ValueError('rss list is empty')
    if not settings.db:
        raise ValueError('db url is empty')


def print_args(settings):
    logger.info('Parameters:')
    logger.info('\tdb: {}'.format(settings.db))
    logger.info('\tperiod: {} minutes'.format(settings.period))
    logger.info('\trss:')
    for url in settings.rss:
        logger.info('\t - {}'.format(url))
    logger.info('\tgraph: {}'.format(settings.graph if settings.graph else 'no set'))


def parse_rss(url, session):
    logger.info("Parse '{}'".format(url))
    rss_document = feedparser.parse(url)
    with ORMSessionSQLAlchemy(session):
        feed_extractor(rss_document)


def main():
    settings = parse_args()
    complete_args(settings)
    print_args(settings)
    validate_args(settings)

    if settings.graph:
        logger.info("Dumping graph to '{}.pdf'".format(settings.graph))
        ActionsPlotter().plot(feed_extractor, settings.graph)

    logger.info("Open database from '{}'".format(settings.db))
    engine = create_engine(settings.db)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    logger.info('Start loop')
    last_parse_timestamp = 0
    while True:
        try:
            current_time = int(time.time())
            if last_parse_timestamp + settings.period * 60 < current_time:
                session = Session()
                for url in settings.rss:
                    parse_rss(url, session)
                last_parse_timestamp = current_time
            time.sleep(1)
        except (SystemExit, KeyboardInterrupt):
            break
        except Exception:
            logger.exception('error:')
            time.sleep(10)
    logger.info('Stop loop')


if __name__ == '__main__':
    main()
