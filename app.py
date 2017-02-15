import uuid
import argparse
import time
import string
import random
import redis


class Application(object):
    def __init__(self):
        self.redis = redis.Redis()

    def _generator_exists(self):
        clients = self.redis.client_list()
        for client in clients:
            if client['name'] == 'generator':
                return True
        return False

    def _generate_answer(self):
        s = string.letters + ' '
        length = random.randint(10, 50)
        return ''.join(random.choice(s) for i in range(length))

    def _check_error(self):
        if random.randint(0, 19) == 0:
            return True

    def become_generator(self):
        self.redis.client_setname('generator')
        i = 0
        while True:
            msg = self._generate_answer()
            self.redis.rpush('queue', msg)
            i += 1
            time.sleep(0.5)

    def become_worker(self):
        while True:
            if not self._generator_exists():
                break
            name = 'consumer-{}'.format(uuid.uuid4().hex)
            self.redis.client_setname(name)
            msg = self.redis.blpop('queue')[1]
            if self._check_error():
                self.redis.sadd('errors', msg)
                print('Message: {} contains error'.format(msg))
            else:
                print('Consuming {}'.format(msg))
            time.sleep(0.25)
        self.become_generator()

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
        if not self._generator_exists():
            self.become_generator()
        else:
            self.become_worker()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--getErrors', help='collect errors from Redis')
    args = parser.parse_args()
    app = Application()
    if args.getErrors:
        app.collect_errors()
    else:
        app.start()


if __name__ == "__main__":
    main()
