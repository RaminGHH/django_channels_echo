import asyncio
from channels_redis.core import RedisChannelLayer

async def main():
    layer = RedisChannelLayer(hosts=[("127.0.0.1", 6380)])
    await layer.group_add("chat", "specific.test")
    await layer.group_send("chat", {"type": "chat.message", "message": "hi"})
    print(await asyncio.wait_for(layer.receive("specific.test"), 5))

asyncio.run(main())