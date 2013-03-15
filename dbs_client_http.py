#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
"""
File       : dbs_client_http.py
Author     : Valentin Kuznetsov <vkuznet@gmail.com>
Description: 
"""

# system modules
import os
import sys
import json
import urllib2, urllib
import time, types

def client(ndatasets):
    "Main function"
    url    = 'http://localhost:9000/dbs/datasets'
    params = {'ndatasets': ndatasets}
    url    = url + '?' + urllib.urlencode(params)
    req    = urllib2.Request(url)
    data   = urllib2.urlopen(req)
    print data.read()

def main():
    "Main function"
    time0 = time.time()
    ntimes = 10
    for _ in range(0, ntimes):
        client(2)
    print "elapsed time:", (time.time()-time0)

if __name__ == '__main__':
    main()


