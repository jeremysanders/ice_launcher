from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import logging
import threading

from . import sources

class LauncherHTTPServer(HTTPServer):
    def __init__(self, config, *args, **argsv):
        HTTPServer.__init__(self, *args, **argsv)
        self.config = config

        # locks for each mount
        self.mount_locks = {
            n: threading.Lock() for n in config.mounts
        }

        # this keeps track of which clients are using each mount
        self.mount_clients = {m: set() for m in config.mounts}
        # this maps mounts to Popen processes
        self.mount_processes = {}

class HTTPHandler(BaseHTTPRequestHandler):

    def send_positive_response(self):
        self.send_response(200)
        self.send_header('icecast-auth-user', '1')
        self.end_headers()

    def send_negative_response(self):
        self.send_response(200)
        self.send_header('icecast-auth-user', '0')
        self.end_headers()

    def start_source(self, mount):
        """Start source for mount given."""
        popen = sources.start_source(mount, self.server.config)
        self.server.mount_processes[mount] = popen

    def stop_source(self, mount):
        """Stop the mount source by killing the ffmpeg process."""
        popen = self.server.mount_processes[mount]
        del self.server.mount_processes[mount]
        popen.terminate()
        popen.wait()
        logging.info(" successfully stopped ffmpeg for mount " + mount)

    def listener_add(self, params):
        logging.info("listener_add " + str(params))
        mount = params['mount'].lstrip('/')
        if mount in self.server.config.mounts:
            with self.server.mount_locks[mount]:
                if not self.server.mount_clients[mount]:
                    logging.info(' need to start mount ' + mount)
                    self.start_source(mount)
                client = params['client']
                self.server.mount_clients[mount].add(client)
                print('clients', self.server.mount_clients[mount])
        else:
            logging.info(' unknown mount "%s" for listener_add, so ignoring' % mount)

    def listener_remove(self, params):
        logging.info("listener_remove " + str(params))
        mount = params['mount'].lstrip('/')
        if mount in self.server.config.mounts:
            with self.server.mount_locks[mount]:
                client = params['client']
                print('clients', self.server.mount_clients[mount])
                if client in self.server.mount_clients[mount]:
                    self.server.mount_clients[mount].remove(client)
                    if not self.server.mount_clients[mount]:
                        logging.info(' no more clients left - stopping source')
                        self.stop_source(mount)
                    else:
                        logging.info(' clients remaining: '+str(self.server.mount_clients[mount]))
        else:
            logging.info(' unknown mount "%s" for listener_remove, so ignoring' % mount)

    def do_POST(self):
        # get data from POST
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length).decode('utf-8')

        # logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
        #         str(self.path), str(self.headers), data)

        # convert POST data to a dictionary
        params = urllib.parse.parse_qs(data)
        # keep only first parameters
        params = {k: v[0] for k, v in params.items()}

        if params['action'] == 'listener_add':
            self.listener_add(params)
        elif params['action'] == 'listener_remove':
            self.listener_remove(params)
        else:
            logging.info("Unknown action: %s (%s)" % (
                params['action'], str(params)))

        self.send_positive_response()

    def do_GET(self):
        """Handle GET request.

        This is not needed by icecast.
        """
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Error 404: Not found')

def run_server(config):
    """Start HTTP server and process requests."""

    server_address = (
        config.main['listen_address'],
        config.main['listen_port'],
    )

    httpd = LauncherHTTPServer(config, server_address, HTTPHandler)
    logging.info('Starting icecast auth server\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping icecast auth server\n')
