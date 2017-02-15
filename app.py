import uuid
import time
import redis


class Application(object):
    def __init__(self):
        self.redis = redis.Redis()

    def generator_exists(self):
        clients = self.redis.client_list()
        for client in clients:
            if client['name'] == 'generator':
                return True
        return False

    def become_generator(self):
        self.redis.client_setname('generator')
        i = 0
        while True:
            self.redis.rpush('queue', 'Message number {}'.format(i))
            i += 1
            # time.sleep(0.5)

    def become_worker(self):
        while True:
            name = 'consumer-{}'.format(uuid.uuid4().hex)
            self.redis.client_setname(name)
            value = self.redis.blpop('queue')
            print('Consuming {}'.format(value))
            time.sleep(0.25)
            if not self.generator_exists():
                break
        self.become_generator()

    def start(self):
        if not self.generator_exists():
            self.become_generator()
        else:
            self.become_worker()


def main():
    app = Application()
    app.start()


if __name__ == "__main__":
    main()
