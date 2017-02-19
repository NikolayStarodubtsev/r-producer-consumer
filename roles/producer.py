import string
import time
import random


class Generator(object):
    def __init__(self, redis):
        self.redis = redis
        self.redis.client_setname('generator')

    def _generate_answer(self):
        s = string.letters + ' '
        length = random.randint(10, 50)
        return ''.join(random.choice(s) for i in range(length))

    async def produce_call(self):
        msg = self._generate_answer()
        self.redis.rpush('main-queue', msg)
        time.sleep(0.5)

    async def produce_heartbeat(self):
        self.redis.publish('heartbeat', "PING")
        time.sleep(0.01)

    def empty_vote_stack(self):
        self.zremrangebyrank('votes', 0, -1)
