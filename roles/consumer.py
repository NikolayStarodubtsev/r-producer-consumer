import uuid
import random


class Worker(object):
    def __init__(self, redis):
        self.redis = redis
        self.name = 'worker-{}'.format(uuid.uuid4().hex())
        self.redis.client_setname(self.name)
        self.heartbeat_listener = self.redis.pubsub()
        self.heartbeat_listener.subscribe('heartbeat')
        self.vote_listener = self.redis.pubsub()
        self.vote_listener.subscribe('vote')

    def _check_error(self):
        if random.randint(0, 19) == 0:
            return True

    async def consume_message(self):
        msg = self.redis.blpop('main-queue')[1]
        if self._check_error():
            self.redis.sadd('errors', msg)
            print('Message: {} contains error'.format(msg))
        else:
            print('Consuming {}'.format(msg))

    async def handle_heartbeat(self):
        if self.heartbeat_listener.get_message():
            yield True
        else:
            yield False

    def _check_vote_stack(self):
        return self.redis.zrevrange('votes', 0, -1)

    def handle_vote(self):
        result = self._check_vote_stack()
        if result:
            self.redis.zincrby('votes', result[0])
        else:
            self.redis.publish('vote', self.name)
            r.zadd('votes', 1, self.name)
