# -*- coding: utf-8 -*-
import os
import json
import time
import random
from ws4py.client.threadedclient import WebSocketClient

class DBSClient(WebSocketClient):
    def opened(self):
        "Invoked when client establish connection with WebSocket server"
        # we can send something here, e.g. some negotiation token, self.send("hi")
        pass

    def closed(self, code, reason):
        "Invoked when client close connection with WebSocket server"
        print "Closed code=%s, reason=%s" % (code, reason)

    def received_message(self, msg):
        "Invoked when client receive new message from WebSocket server"
        print str(msg)

    def request(self, ndatasets):
        "Local class method, request data from the server"
        self.send(str(ndatasets))

def main():
    "Main function"
    try:
        time0 = time.time()
        ckey = os.path.join(os.environ['HOME'], '.globus/userkey.pem')
        cert = os.path.join(os.environ['HOME'], '.globus/usercert.pem')
#        ws = DBSClient('http://127.0.0.1:9000/websocket/ws', protocols=['http-only'])
#        ws = DBSClient('ws://localhost:9000/websocket/ws', protocols=['http-only'])
#        ws = DBSClient('wss://localhost/websocket/ws', protocols=['http-only'])
# work with nginx
#        ws = DBSClient('ws://localhost/websocket/ws', protocols=['http-only'])
#        ws = DBSClient('wss://localhost/websocket/ws', protocols=['http-only'])
# work with apache
        ws = DBSClient('wss://localhost/websocket/ws', protocols=['http-only', 'base64'])
# check CERN VM
#        ws = DBSClient('wss://dastest.cern.ch/websocket/ws')
        ws.daemon = False
        ws.connect(ckey, cert)
        print "server connection time:", (time.time()-time0)
        ntimes = 10
        time1 = time.time()
        for attempt in range(0, ntimes):
            ws.request(2)
        print "request elapsed time:", (time.time()-time1)
        ws.close(reason='bye')
        print "total elapsed time:", (time.time()-time0)
    except KeyboardInterrupt:
        ws.close()

if __name__ == '__main__':
    main()
