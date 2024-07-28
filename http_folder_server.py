from http import server
from os import getcwd

class MainHandler(server.SimpleHTTPRequestHandler):
    def __init__(self, request, address, server, directory=None, logging=0):
        self.directory = directory or getcwd()
        self.logging = logging
        super().__init__(request, address, server, directory=directory)
    def log_message(self, *args, **kwargs) -> None:
        if self.logging>=2:
            super().log_message(*args, **kwargs)

class MainServer(server.ThreadingHTTPServer):
    def __init__(self, address=('0.0.0.0', 80), directory=None, logging=0):
        self.directory = directory
        self.logging = logging
        host = '::' if address[0] == '0.0.0.0' else address[0]
        url_host = f'[{host}]' if ':' in host else host
        port = address[1]
        if logging>=1:
            print('Serving HTTP on {host} port {port} (http://{url_host}:{port}/) ...'.format(host=host, url_host=url_host, port=port))
        super().__init__(address, self.handler)

    def handler(self, request, address, server):
        MainHandler(request, address, server, directory=self.directory, logging=self.logging)
    
    def start(self):
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            print('Keyboard interrupt received, exiting.') if self.logging else None

def main(address=('0.0.0.0', 80), directory=None, logging=False):
    _server = MainServer(address, directory, logging)
    _server.start()

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-b', '-a', '--bind', '--address', default='0.0.0.0', metavar='ADDRESS', dest='address',
                        help='bind to this address '
                             '(default: all interfaces)')
    parser.add_argument('port', default=80, type=int, nargs='?',
                        help='bind to this port '
                             '(default: %(default)s)')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='verbose '
                             '(default: %(default)s)')
    parser.add_argument('-d', '--directory', default=getcwd(), dest='directory',
                        help='serve this directory '
                             '(default: current directory)')
    args = parser.parse_args()
    main((args.address, args.port), args.directory, args.verbose)