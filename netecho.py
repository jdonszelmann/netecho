import cgi
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import argparse
import sys
from datetime import datetime

def get_data(obj):
    # It's a huge hack that mostly comes from python2 libraries
    # but sofar it's the easiest way I found to parse multipart
    # formdata.
    ctype, pdict = cgi.parse_header(obj.headers.get('content-type'))
    pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
    pdict['CONTENT-LENGTH'] = int(obj.headers.get('Content-length'))

    if ctype == 'multipart/form-data':
        data = "\n".join((
            " ".join(i) if isinstance(i, list) else str(i) for i in cgi.parse_multipart(obj.rfile, pdict).values()
        ))
    else:
        data = obj.rfile.read(int(obj.headers.get('Content-length')))

    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This program logs any request with any data it gets.");

    parser.add_argument("-d", "--dir", type=str, help="Directory to write requests to.", default="logs")
    parser.add_argument("-p", "--port", type=int, help="File to write data to.", default=8000)
    args = parser.parse_args(sys.argv[1:])

    if not os.path.exists(args.dir):
        os.mkdir(args.dir)

    symlinkpath = os.path.join(os.path.join(os.getcwd(), args.dir, "latest"))

    if os.path.exists(symlinkpath):
        os.unlink(symlinkpath)

    filepath = os.path.join(args.dir, f"{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}.log")
    logfile = open(filepath, "a", buffering=1)
    os.symlink(os.path.join(os.getcwd(), filepath), symlinkpath)


    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.send_response(200)
            self.end_headers()

            if self.path == "/" or self.path == "":
                print(get_data(self), file=logfile)
            elif self.path == "/stdout":
                print(get_data(self), file=sys.stdout)
            elif self.path == "/stderr":
                print(get_data(self), file=sys.stderr)

    print(f"running on port:{args.port} logging to {filepath}")

    with HTTPServer(('0.0.0.0', args.port), Handler) as httpd:
        httpd.serve_forever()
