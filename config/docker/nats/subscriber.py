import asyncio
import signal
import nats
import json
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError


async def subscribe(server, port, subject):
    nc = None
    try:
        nc = await nats.connect(f'nats://{server}:{port}')
    except Exception as ex:
        print(ex)

    print(f"Listening on [{subject}]")

    def signal_handler():
        if nc.is_closed:
            return
        asyncio.create_task(nc.drain())

    for sig in ("SIGINT", "SIGTERM"):
        asyncio.get_running_loop().add_signal_handler(
            getattr(signal, sig), signal_handler
        )

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = json.loads(msg.data.decode())
        print(f"received a message on {subject} {reply}: {data}")

    sub = await nc.subscribe(subject, cb=message_handler)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(subscribe(server="localhost", port=4222, subject="metrics.hello"))
    try:
        loop.run_forever()
    finally:
        loop.close()
