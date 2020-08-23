import asyncio
import os
import signal
from time import sleep


async def run_jupyter_shell(port, token, ebala):
    script = f"""
    export JUPYTER_TOKEN={token};
    PORT={port};
    jupyter notebook --no-browser --port=$PORT
    """
    process = await asyncio.create_subprocess_shell(script)
    ebala.append(process.pid + 1)


def start_jupyter_server(port=8814, token="token"):
    ebala = []
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_jupyter_shell(port, token, ebala))
    loop.close()
    return ebala[0]


if __name__ == '__main__':
    os.setpgrp()
    start_jupyter_server()
    sleep(1000)
