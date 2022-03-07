import argparse
import logging
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading


# setup arguments and help messages
example_text = '''
* Example Usages:
  
  python3 ./%(prog)s.py -p 8000

  python3 ./%(prog)s.py -H 192.168.1.1 -p 8000

 '''

parser = argparse.ArgumentParser(
    prog='main',
    description="AIM: Simple HTTP server to redirect requests after looked up.",
    epilog=example_text,
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument("-H", dest="hosting_address", action="store", default="127.0.0.1",
                    help="Specify the hosting address of this server. (default = 127.0.0.1)")
parser.add_argument("-p", dest="port", action="store", default=8000, type=int,
                    help="Specify the port for this server to listen. (default = 8000)")
parser.add_argument("-v", dest="verbose_flag", action="store_true",
                    help="Set verbose level to 1. (info)")
# parser.add_argument("-vv", dest="more_verbose_flag", action="store_true",
#                     help="Set verbose level to 2. (debug)")

args = parser.parse_args()


logging.basicConfig(level=logging.INFO)
if args.verbose_flag:
    logging.basicConfig(level=logging.WARNING)


use_https = False


class LookupWorker:
    def __init__(self):
        self.lookup_method = ""
        self.dict_book = {}
        self.default_url = "https://www.google.com"

    def lookup(self, key):
        if self.lookup_method == "dict":
            return self.dict_book.get(key, self.default_url)

    def update_dict(self, input_dict):
        self.dict_book = input_dict
        self.lookup_method = "dict"


w = LookupWorker()
w.update_dict({
    "/": 'https://www.google.com',
    "/test": "https://github.com/"
})


# Setup http server,  Modified from https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7
class ReHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.debug(
            f"GET request,\n"
            f"Path: {str(self.path)}\n"
            f"Headers:\n"
            f"{str(self.headers)}\n"
        )
        self.send_response(301)
        self.send_header('Location', w.lookup(self.path))
        self.end_headers()


# https://stackoverflow.com/questions/14088294/multithreaded-web-server-in-python
class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


def run():
    server = ThreadingSimpleServer((args.hosting_address, args.port), ReHandler)
    logging.info(f"Starting HTTP server on: {args.hosting_address}:{args.port}")
    if use_https:
        import ssl
        server.socket = ssl.wrap_socket(server.socket, keyfile='./key.pem', certfile='./cert.pem', server_side=True)
    server.serve_forever()


if __name__ == '__main__':
    run()


