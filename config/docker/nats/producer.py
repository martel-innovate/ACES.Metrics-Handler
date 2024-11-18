import asyncio
import json

import nats


async def producer(server, port, subject, data):
    nc = None
    try:
        nc = await nats.connect(f'nats://{server}:{port}')
    except Exception as ex:
        print(ex)

    await nc.publish(subject, data.encode())
    print(f"Published [{subject}] : '{data}'")
    await nc.flush()
    await nc.drain()


if __name__ == '__main__':
    data = json.dumps({"msg": "hello sir"})
    asyncio.run(producer(server="localhost", port=4222, subject="metrics.hello", data=data))
