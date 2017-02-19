import argparse
import redis

from .roles import consumer
from .roles import producer


class Application(object):
    def __init__(self):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

    def start(self):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--getErrors', help='collect errors from Redis',
                        action='store_true')
    args = parser.parse_args()
    app = Application()
    if args.getErrors:
        app.collect_errors()
    else:
        app.start()


if __name__ == "__main__":
    main()
