# -*- coding: utf-8 -*-
import argparse
import random
import os

import json
import time
import cherrypy
import threading

from pprint import pformat
from cherrypy import config as cpconfig
from cherrypy import log, tree, engine
from cherrypy.process.plugins import PIDFile

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
        if  msg.is_text: # msg is a TextMessage type
            ndatasets = int(str(msg)) # here client send msg which means # of datasets
#            for rid in range(0, ndatasets):
#                self.send(json.dumps(doc(rid)))
            # version 2, similar to DBS, create a list and send it over
            data = []
            for rid in range(0, ndatasets):
                data.append(doc(rid))
            self.send(json.dumps(data))

    def closed(self, code, reason="Normal exit"):
        "Invoked when client close/lost connection, will broadcast"
        cherrypy.engine.publish('websocket-broadcast', TextMessage(reason))

class DataService(object):
    def __init__(self):
        self.data = 1

    @cherrypy.expose
    def index(self):
        return "TEST"

    @cherrypy.expose
    def datasets(self, ndatasets):
        data = []
        for rid in range(0, int(ndatasets)):
            data.append(doc(rid))
        return json.dumps(data)

class Root(object):
    def __init__(self, config):
        if  not isinstance(config, dict):
            raise Exception('Wrong config type')
        self.config = config
        self.pid    = None

    @cherrypy.expose
    def index(self):
        return "MyRoot service"

    @cherrypy.expose
    def test(self):
        return "TEST"
    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))

    def configure(self):
        """Configure server, CherryPy and the rest."""
        config = self.config['web_server']
        self.pid = config.get('pid', '/tmp/server.pid')
        cpconfig["engine.autoreload_on"] = False
        cpconfig["server.environment"] = config.get("environment", "production")
        cpconfig["server.thread_pool"] = int(config.get("thread_pool", 30))
        cpconfig["server.socket_port"] = int(config.get("port", 9000))
        cpconfig["server.socket_host"] = config.get("host", "0.0.0.0")
        cpconfig["server.socket_queue_size"] = \
                int(config.get("socket_queue_size", 100))
        cpconfig["tools.expires.secs"] = int(config.get("expires", 300))
        cpconfig["tools.staticdir.root"] = \
                os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
        cpconfig["log.screen"] = bool(config.get("log_screen", True))
        cpconfig["log.access_file"] = config.get("access_log_file", 'access.log')
        cpconfig["log.error_file"] = config.get("error_log_file", 'error.log')
        cpconfig['request.show_tracebacks'] = True

    def start(self, blocking=True):
        """Configure and start the server."""
        self.configure()
        config['engine'] = engine

        WebSocketPlugin(engine).subscribe()
        cherrypy.tools.websocket = WebSocketTool()
        
        base_url = config.get('ws_base_url', '/websocket')
        wsconfig = {'/ws' :{
                           'tools.websocket.on': True,
                           'tools.websocket.handler_cls': DBSWebSocketHandler
                           }}
        tree.mount(self, base_url, wsconfig) # mount WebSocket service
        obj = DataService()
        tree.mount(obj, '/dbs') # mount another data service
        print "Applications:", pformat(tree.apps)
        print "Configuration:", pformat(self.config)

        pid = PIDFile(engine, self.pid)
        pid.subscribe()

        engine.start()
        print "### number of threads with web engine %s" \
                % threading.active_count()
        if  blocking:
            engine.block()

if __name__  == '__main__':
    config = {'web_server':{}}
    root = Root(config)
    root.start()
