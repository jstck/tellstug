#!/usr/bin/env python3

import http.client
import os

conn = http.client.HTTPConnection("www.stack.se")
conn.request("GET", "/john/setpoints.json")
r1 = conn.getresponse()

if r1.status==200:
	filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "setpoints.json")
	f = open(filename, "wb")
	f.write(r1.readall())
	f.close
	