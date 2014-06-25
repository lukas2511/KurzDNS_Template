#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json, os, hmac, hashlib

DEBUG = False
ENV_SECRET = os.getenv('SECRET','YO DAWG I HEARD YOU LIKE SECRETS SO I PUT A SECRET INTO YOUR $SECRET')

class GitAutoDeploy(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            self.handleStuff()
        except:
            pass

    def log_message(self, format, *args):
        return

    def handleStuff(self):
        try:
            sig_received = self.headers.getheader('X-Hub-Signature')[5:]
            length = int(self.headers.getheader('content-length'))
            body = self.rfile.read(length)
            print sig_received
            sig_calculated = hmac.new(ENV_SECRET, msg=body, digestmod=hashlib.sha1).hexdigest()
            print sig_calculated
            if DEBUG:
                data = json.loads(body)
                print(json.dumps(data, sort_keys = False, indent = 4))
            if sig_calculated == sig_received:
                os.system("cd /etc/kurzdns; git pull")
                os.system("/etc/init.d/bind9 reload > /dev/null")
                retval=200
            else:
                retval=403
        except:
            retval=500

        self.send_response(retval)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('OHAI! STATUS: %d' % retval)

def main():
    try:
        server = None
        print('Kurzdns Github Autodeploy Service v1.0.1-ultrastable started')
        server = HTTPServer(('', 8001), GitAutoDeploy)
        server.serve_forever()
    except(KeyboardInterrupt, SystemExit) as e:
        if server:
            server.socket.close()
        print "Goodbye."

if __name__ == '__main__':
    main()
