from http import server
from os import getcwd

def parse_logs_file(logs_file:str, default_value:str):
    if isinstance(logs_file, str):
        if logs_file.strip().lower() in ["true", "1", "activate", "on"]:
            return default_value
        elif logs_file.strip().lower() in ["false", "0", "deactivate", "off"]:
            return False
        else:
            return logs_file
    else:
        return default_value if logs_file else logs_file

class MainHandler(server.SimpleHTTPRequestHandler):
    def __init__(self, request, address, server, directory=None, logs_file=None):
        self.directory = directory or getcwd()
        self.logs_file = logs_file
        super().__init__(request, address, server, directory=directory)
    def log_message(self, *args, **kwargs) -> None:
        message = args[0] % args[1:]
        msg = "%s - - [%s] %s" %(
            self.address_string(),
            self.log_date_time_string(),
            message.translate(self._control_char_table)
            )
        self.server.logf(msg)

class MainServer(server.ThreadingHTTPServer):
    def __init__(self, address=("0.0.0.0", 80), directory=None):
        self.directory = directory
        self.logs_file = None
        self.logf = print
        host = "::" if address[0] == "0.0.0.0" else address[0]
        url_host = f"[{host}]" if ":" in host else host
        port = address[1]
        print("Serving HTTP on {host} port {port} (http://{url_host}:{port}/) ...".format(host=host, url_host=url_host, port=port))
        super().__init__(address, self.handler)

    def handler(self, request, address, server):
        MainHandler(request, address, server, directory=self.directory, logs_file=self.logs_file)

    def start(self):
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            print("Keyboard interrupt received, exiting.")

    def log_dumper(self, data):
        print(data)
        self.logs_file.write(data.encode() + b"\n")
        self.logs_file.flush()

    def set_logs_file(self, logs_file:str):
        try:
            self.logs_file = open(logs_file, "wb")
            self.logf = self.log_dumper
        except:
            print("error: failed to open the log file")

    def __del__(self):
        if self.logs_file:
            self.logs_file.close()

def main(address=("0.0.0.0", 80), directory=None, logs_file=None):
    _server = MainServer(address, directory)
    if logs_file:
        _server.set_logs_file(logs_file)
    _server.start()

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    default_logs_file = "shttp_server.log"
    parser.add_argument("-b", "-a", "--bind", "--address", default="0.0.0.0", metavar="ADDRESS", dest="address",
                        help="bind to this address "
                             "(default: all interfaces)")
    parser.add_argument("port", default=80, type=int, nargs="?",
                        help="bind to this port "
                             "(default: %(default)s)")
    parser.add_argument("-d", "--directory", default=getcwd(), dest="directory",
                        help="serve this directory "
                             "(default: current directory)")
    parser.add_argument("--logs-file", default=default_logs_file, dest="logs_file",
                        help="logs file "
                             "(default: %(default)s)")
    args = parser.parse_args()
    main((args.address, args.port), args.directory, parse_logs_file(args.logs_file, default_logs_file))
