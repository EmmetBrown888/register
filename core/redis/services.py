"""Services module."""

from aioredis import Redis


class Service:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def process(self, key: str, value: str) -> None:
        """
        Adding code to the Redis database by user id

        :param key: str
        :param value: str
        :return: None
        """
        await self._redis.set(key, value, expire=600)

    async def get_value(self, key: str) -> str:
        """
        Getting value from Redis database by user id

        :param key: str
        :return: str
        """
        return await self._redis.get(int(key), encoding='utf-8')

    async def remove_key(self, key: str) -> int:
        """
        Removing code from the Redis database by user id

        :param key: str
        :return: int
        """
        return await self._redis.delete(key)
