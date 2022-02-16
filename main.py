import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer


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
parser.add_argument("-vv", dest="more_verbose_flag", action="store_true",
                    help="Set verbose level to 2. (debug)")

args = parser.parse_args()


class Notifier:
    def __init__(self, *, verbose):
        # self.webhook_url = webhook_url
        self.verbose = int(verbose)
        self.verbose_table = {
            0: "[error] Only Error message",
            1: "[info] Info level messages",
            2: "[debug] Verbose messages"
        }

    def requests_post(self, message):
        print(f"{message}")
        # requests.post(self.webhook_url, json={"text": f"{message}"})

    def error(self, message):
        if 0 <= self.verbose:
            self.requests_post(f"[ERROR]: {message}")
            # sys.exit(f"[ERROR]: {message}")

    def info(self, message):
        if 1 <= self.verbose:
            self.requests_post(f"[INFO ]: {message}")

    def debug(self, message):
        if 2 <= self.verbose:
            self.requests_post(f"[DEBUG]: {message}")


# Set Notifier (logger)
verbose_level = 0
if args.verbose_flag:
    verbose_level = 1
if args.more_verbose_flag:
    verbose_level = 2
notify = Notifier(verbose=verbose_level)


class LookupWorker:
    def __init__(self):
        pass

    def by_dict(self, input_dict):
        pass


# Setup http server,  Modified from https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7
class ReHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        notify.debug(f"GET request,\n"
                    f"Path: {str(self.path)}\n"
                    f"Headers:\n"
                    f"{str(self.headers)}\n"
                    )
        self.send_response(301)
        self.send_header('Location', 'https://www.google.com')
        self.end_headers()


server_address = (args.hosting_address, args.port)
httpd = HTTPServer(server_address, ReHandler)
notify.info(f"Starting HTTP server on: {args.hosting_address}:{args.port}")
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    notify.error("KeyboardInterrupt")
httpd.server_close()
notify.info('Stopping HTTP server...\n')
