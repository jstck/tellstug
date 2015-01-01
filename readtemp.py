#!/usr/bin/env python3

import tellcore.telldus
from tellcore.telldus import TelldusCore, Device, Sensor, QueuedCallbackDispatcher
import json
import os

core=TelldusCore()

sensors=core.sensors()

#Find the one!
tempsensor_id = 135

for s in sensors:
	if s.id!=tempsensor_id:
		continue
		
	tval=s.value(tellcore.telldus.const.TELLSTICK_TEMPERATURE)
	temperature=float(tval.value)

	hval=s.value(tellcore.telldus.const.TELLSTICK_HUMIDITY)
	humidity=float(hval.value)
	
	timestamp=tval.timestamp
	
	print("%.1f°C %d%% @%d" % (temperature, humidity,timestamp))
	
	data={ "temperature": temperature, "humidity": humidity, "timestamp": timestamp }
	
	filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "values.json")
	f = open(filename, "w")
	json.dump(data, f, indent=2, separators=(',', ': '))
	f.write("\n")
	f.close()
	
	