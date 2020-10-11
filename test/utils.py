import asyncio
import os
from time import sleep

import jupytext


async def run_jupyter_shell(port, token, pids):
    script = f"""
    export JUPYTER_TOKEN={token};
    PORT={port};
    jupyter notebook --no-browser --port=$PORT
    """
    process = await asyncio.create_subprocess_shell(script)
    pids.append(process.pid + 1)


def start_jupyter_server(port=8009, token="token"):
    pids = []
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.get_event_loop().run_until_complete(run_jupyter_shell(port, token, pids))
    asyncio.get_event_loop().close()
    return pids[0]


def modify_ipynb_file(path):
    notebook = jupytext.read(path)
    first_cell = notebook.cells[0]
    first_cell['source'] = first_cell['source'][:-1] + 'a"'
    if len(first_cell['source']) > 10:
        first_cell['source'] = '"a"'
    jupytext.write(notebook, path)


def modify_py_file(path):
    with open(path) as f:
        data = f.read()
    line_1 = '"some_old_code"'
    line_2 = '"some_new_code"'

    if line_1 in data:
        data = data.replace(line_1, line_2)
    elif line_2 in data:
        data = data.replace(line_2, line_1)
    else:
        data = data + "\n" + line_1
    with open(path, "w") as f:
        print(data, file=f, flush=True, end='')


if __name__ == '__main__':
    os.setpgrp()
    start_jupyter_server()
    sleep(1000)
