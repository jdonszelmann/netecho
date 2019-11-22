import asyncio
import os
import argparse
import sys
from datetime import datetime
from quart import Quart, request, stream_with_context, websocket
import uuid

async def get_data(obj):
    files = await obj.form

    if files:
        data = "\n".join((
            " ".join(i) if isinstance(i, list) else str(i) for i in files.values()
        ))
    else:
        data = await obj.get_data()

    return data


class PubSub:
    def __init__(self):
        self.buffer = []
        self.subscribers = {}

    def push(self, data):
        self.buffer.append(data)

    async def get(self):
        identifier = uuid.uuid4()
        self.subscribers[identifier] = len(self.buffer)

        while True:
            while len(self.buffer) != self.subscribers[identifier]:
                yield self.buffer[self.subscribers[identifier]]
                self.subscribers[identifier] += 1
            await asyncio.sleep(0.1)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="This program logs any request with any data it gets.");

    parser.add_argument("-d", "--dir", type=str, help="Directory to write requests to. Can alternatively be set with "
                                                      "NETECHO_DIR in envvars.", default="logs")
    parser.add_argument("-p", "--port", type=int, help="File to write data to. Can alternatively be set with "
                                                       "NETECHO_PORT in envvars.", default=8000)
    parser.add_argument("-u", "--url", type=str, help="url netecho runs on, for websockets. Can alternatively be set "
                                                      "with NETECHO_URL in envvars.", default="ws://localhost:8000")


    args = parser.parse_args(sys.argv[1:])

    args.port = int(os.environ.get('NETECHO_PORT', args.port))
    args.dir = os.environ.get('NETECHO_DIR', args.dir)
    args.url = os.environ.get('NETECHO_URL', args.url)

    app = Quart(__name__)

    if not os.path.exists(args.dir):
        os.mkdir(args.dir)

    symlinkpath = os.path.join(args.dir, "latest")

    try:
        os.unlink(symlinkpath)
    except:
        pass

    filename = f"{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}.log"
    filepath = os.path.join(args.dir, filename)
    logfile = open(filepath, "a", buffering=1)
    os.symlink(filename, symlinkpath)

    buffer = PubSub()


    @app.route('/', methods=['POST'])
    async def log():
        print(await get_data(request), file=logfile)
        return '', 200


    @app.route('/stdout', methods=['POST'])
    async def logstdout():
        print(await get_data(request), file=sys.stdout)
        return '', 200


    @app.route('/stderr', methods=['POST'])
    async def logstderr():
        print(await get_data(request), file=sys.stderr)
        return '', 200


    @app.route('/public', methods=['POST'])
    async def logpublic():
        buffer.push((await get_data(request)).replace("<", "&lt;"))
        return '', 200


    @app.route('/', methods=['GET'])
    async def public():
        return f"""
        <pre> </pre>
        
        <script>
            
            let backoff = 1;
            
            function create_ws() {{
                let ws = new WebSocket("{args.url}/ws");
                ws.onmessage = (event) => {{
                    let pres = document.getElementsByTagName("pre");
                    pres[pres.length-1].innerHTML += (event.data + "</pre><hr><pre>");
                }}
                
                ws.onclose = () => {{
                    backoff *= 2;
                    setTimeout(create_ws, backoff * 1000);
                }}
            }}
            
            create_ws()
            
        </script>
        
        """

    @app.websocket('/ws')
    async def ws():
        async for i in buffer.get():
            await websocket.send(i)

    print(f"running on port:{args.port} logging to {filepath}")
    print(f"running on port:{args.port} logging to {filepath}", file=logfile)

    app.run(
        host='0.0.0.0',
        port=args.port,
    )
