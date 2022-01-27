#!/usr/bin/env python3

import psutil
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
from datetime import datetime
import json
import collections
import threading

PORT = 9000
HISTORY_LENGTH = 60
INTERVAL = 5

def collect():
    while True:
        memory_use = psutil.virtual_memory()
        with lock:
            history.append({
                't': (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds(),
                'm': memory_use.percent,
                'c': psutil.cpu_percent(interval=None)
            })
        time.sleep(INTERVAL)

class ProgressServer(BaseHTTPRequestHandler):
    """Class to handle all HTTP requests to our little server."""

    def do_GET(self):
        # We'll only ever respond with JSON and anything goes
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        try:
            path_components = self.path.split('/')
            if path_components[1] == '' or path_components[1] == 'now':
                with lock:
                    jsondata = json.dumps(history[-1], separators=(',', ':')).encode('utf-8')
                self.wfile.write(jsondata)
            elif path_components[1] == 'all':
                with lock:
                    # history_as_list = list(history)
                    # keys = history_as_list[0].keys() if len(history_as_list) > 0 else []
                    # vals = zip(*map(lambda x: x.values(), history_as_list))
                    # transposed = dict(zip(keys, vals))
                    # jsondata = json.dumps(transposed).encode('utf-8')
                    jsondata = json.dumps(list(history), separators=(',', ':')).encode('utf-8')
                self.wfile.write(jsondata)
                #self.wfile.write(json.dumps(list(history)).encode('utf-8'))
            else:
                self.wfile.write(b'{}')
        except:
            self.wfile.write(b'[]')

if __name__ == "__main__":
    history = collections.deque(maxlen=HISTORY_LENGTH)
    lock = threading.Lock()

    x = threading.Thread(target=collect, daemon=True)
    x.start()

    server = HTTPServer(("0.0.0.0", PORT), ProgressServer)
    server.serve_forever()
