#!/usr/bin/env python3

import json, os

temp_interval=1.2

pump_min=16
pump_max=30

ir_device = "/dev/ttyACM0"
ir_codefile = "mitsubishi_codes.json"

def readjson(filename):
    f = open(filename, "r")
    j = json.load(f)
    f.close()
    return j

def writejson(data, filename):
    f = open(filename, "w")
    json.dump(data, f, sort_keys=True,indent=2, separators=(',', ': '))

def send_switch(name, state):
	from tellcore.telldus import TelldusCore, Device
	
	core=TelldusCore()
	for device in core.devices():
		if device.name!=name:
			continue
		
		if(bool(state)):
			print("Setting %s to on" % name)
			device.turn_on()
		else:
			print("Setting %s to off" % name)
			device.turn_off()

directory = os.path.dirname(os.path.realpath(__file__))

			
def send_ir(command):
	import serial
	from irtoy import IrToy
	
	f = open(os.path.join(directory,ir_codefile), "r")
	ir_codes = json.load(f)
	if not command in ir_codes:
		print("Command '%s' not found." % command)
		return
		
	serial_device = serial.Serial(ir_device)
	irtoy = IrToy(serial_device)
	irtoy.transmit(ir_codes[command])
	serial_device.close()
	
state=readjson(os.path.join(directory, "state.json"))
setpoints=readjson(os.path.join(directory, "setpoints.json"))
values=readjson(os.path.join(directory, "values.json"))

statechange=False
pumpchange=False

temperature=float(values["temperature"])

#Electric radiators
radstate=bool(state["radiator"])
radset=float(setpoints["radiator"])

if (not radstate) and temperature<(radset-temp_interval/2):
    print("Turning on radiator")
    radstate=True
    state["radiator"]=radstate
    statechange=True
elif radstate and temperature>(radset+temp_interval/2):
    print("Turning off radiator")
    radstate=False
    state["radiator"]=radstate
    statechange=True

#Heat pump
pumpstate=int(state["heatpump"])
pumpset=float(setpoints["heatpump"])
pumpset_int=int(round(pumpset))

#If at or above minimum setting on heatpump, just set it
if pumpset_int>=pump_min:

    #Limit upper value
    if pumpset_int>pump_max:
        pumpset_int=pump_max

    if pumpset_int != pumpstate:
        state["heatpump"] = pumpset_int
        statechange=True
        pumpchange=True

#Run it like a plain heater
elif (pumpstate==0) and temperature<(pumpset-temp_interval/2):
    print("Turning on heatpump")
    pumpstate=pump_min
    state["heatpump"] = pumpstate
    statechange=True
    pumpchange=True
elif (pumpstate>0) and temperature>(pumpset+temp_interval/2):
    print("Turning off heatpump")
    pumpstate=0
    state["heatpump"] = pumpstate
    statechange=true
    pumpchange=true


if statechange:
    print("Saving new state")
    writejson(state,"state.json")


if pumpchange:
    pumpstate=int(state["heatpump"])
    if pumpstate>pump_max:
        pumpcommand=str(int(pump_max))
    elif pumpstate<pump_min and pumpstate>0:
        pumpcommand=str(int(pump_min))
    elif pumpstate<=0:
        pumpcommand="off"
    else:
        pumpcommand=str(pumpstate)

    print("Setting heatpump to %s" % (pumpcommand))
    send_ir(pumpcommand)

#Send radiator state no matter what, since "no change" doesn't do anything
send_switch("radiator", state["radiator"])
