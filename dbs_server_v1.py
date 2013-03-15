# -*- coding: utf-8 -*-
import argparse
import random
import os

import json
import cherrypy

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage

def doc(rid):
    "Generate DBS document"
    return dict(dataset="/a/b/c%s" % rid,
            size=random.randint(0, 100),
            files=random.randint(0, 100))

class DBSWebSocketHandler(WebSocket):
    def received_message(self, msg):
        cherrypy.engine.publish('websocket-broadcast', msg)
        if  msg.is_text: # msg is a TextMessage type
            ndatasets = int(str(msg)) # here client send msg which means # of datasets
            for rid in range(0, ndatasets):
                self.send(json.dumps(doc(rid)))

    def closed(self, code, reason="A client left the room without a proper explanation."):
        cherrypy.engine.publish('websocket-broadcast', TextMessage(reason))

class Root(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    @cherrypy.expose
    def index(self):
        return "TEST"

    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))

if __name__  == '__main__':
    parser = argparse.ArgumentParser(description='Echo CherryPy Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9000, type=int)
    args = parser.parse_args()

    cherrypy.config.update({'server.socket_host': args.host,
                            'server.socket_port': args.port,
                            'log.screen': True,
                            'server.environment': 'production',
                            'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))})

    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.quickstart(Root(args.host, args.port), '', config={
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': DBSWebSocketHandler
            },
        '/js': {
              'tools.staticdir.on': True,
              'tools.staticdir.dir': 'js'
            }
        }
    )
