import asyncio
import os
from time import sleep

import jupytext


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
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.get_event_loop().run_until_complete(run_jupyter_shell(port, token, ebala))
    asyncio.get_event_loop().close()
    return ebala[0]


if __name__ == '__main__':
    os.setpgrp()
    start_jupyter_server()
    sleep(1000)


def modify_ipynb_file(path):
    notebook = jupytext.read(path)
    first_cell = notebook.cells[0]
    first_cell['source'] = first_cell['source'][:-1] + 'a"'
    if len(first_cell['source']) > 10:
        first_cell['source'] = '"a"'
    jupytext.write(notebook, path)