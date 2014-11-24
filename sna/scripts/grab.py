#!/usr/bin/python

import httplib, time, os

path = os.path.dirname(os.path.realpath(__file__))

headers = {'User-Agent': 
           'Mozilla/5.0(Windows; u; windows NT 6.1;en-US) AppleWebKit/533.4 " \
           "(KHTML, like Gecko) Chrome//5.0.375.126 Safari//5.33.4'}

maxpage = 15041

def grab(page):
  conn = httplib.HTTPSConnection("ifttt.com")
  uri = "/recipes/hot" 
  if page > 1:
    uri += ("?page=%d" % page)
  print uri
  conn.request("GET", uri, None, headers)
  r = conn.getresponse()
  if r.status == 200: 
    data = r.read()
    f = open('%s/data/ifttt_%05d.html' % (path, page),'w')
    f.write(data)
    f.close()
  conn.close()


for x in range(1, maxpage):
  if not os.path.isfile('%s/data/ifttt_%05d.html' % (path, x)):
    grab(x)


