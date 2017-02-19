import uuid
import time
import argparse
import string
import sys
import random
import redis


class Application(object):
    def __init__(self):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.name = 'instance-{}'.format(uuid.uuid4().hex)

    # Worker operations.
    def _check_privilege(self):
        print("Checking privilege")
        if self.redis.zscore('messages', 'generated') > 100000:
            print("Cap reached, no need in generator")
            return False
        if self.redis.setnx('generator', self.name):
            self.redis.expire('generator', 1)
            print("i'm a generator")
            return True
        else:
            print("Not my turn")
            return False

    def _check_error(self):
        if random.randint(0, 19) == 0:
            return True

    def become_worker(self):
        while True:
            if self._check_privilege():
                break
            msg = self.redis.blpop('queue', timeout=1)
            if msg:
                if self._check_error():
                    self.redis.sadd('errors', msg[1])
                    print('Message: {} contains error'.format(msg[1]))
                else:
                    print('Consuming {}, number {}'.format(
                        msg[1], self.redis.zscore('messages', 'consumed')))
            if self.redis.zincrby('messages', 'consumed') > 100000:
                sys.exit()
        self.become_generator()

    # Generator operations.
    def _generate_answer(self):
        s = string.letters + ' '
        length = random.randint(10, 50)
        return ''.join(random.choice(s) for i in range(length))

    def become_generator(self):
        while True:
            if self.redis.get('generator') != self.name:
                if not self.redis.setnx('generator', self.name):
                    break
            self.redis.expire('generator', 1)
            msg = self._generate_answer()
            self.redis.rpush('queue', msg)
            if self.redis.zincrby('messages', 'generated') > 100000:
                sys.exit()
            print "Generate {}, number {}".format(msg, self.redis.zscore('messages', 'generated'))
            if random.randint(0, 20) == 0:
                time.sleep(2)
        self.become_worker()

    # Common operations.
    def collect_errors(self):
        print("This messages contains errors:")
        i = 1
        while True:
            msg = self.redis.spop('errors')
            if msg:
                print("{}. {}".format(i, msg))
                i += 1
            else:
                break

    def start(self):
        if self._check_privilege():
            self.become_generator()
        else:
            self.become_worker()


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
