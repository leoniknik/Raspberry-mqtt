# -*- coding: utf-8 -*-
"""
	example hardware
"""
__author__	= """Alexander Krause <alexander.krause@ed-solutions.de>"""
__date__ 		= "2016-01-11"
__version__	= "0.2.0"
__credits__	= """Copyright e-design, Alexander Krause <alexander.krause@ed-solutions.de>"""
__license__	= "MIT"


import sys
import os
sys.path.append(
	os.path.join(
		os.path.dirname(__file__),
		'..'
	)
)
	
TOKEN			= 'b4ca926c8a7a4b85a93159d56b53dd58'

import lib.hw as blynk_hw
import lib.client as blynk_client

class myHardware(blynk_hw.Hardware):
	def OnVirtualWrite(self,pin,val):
		print("aye")
		print('OnVirtualWrite',pin,val)

cConnection=blynk_client.TCP_Client()
if not cConnection.connect():
	print('Unable to connect')
	sys.exit(-1)

if not cConnection.auth(TOKEN):
	print('Unable to auth')
	
cHardware=myHardware(cConnection)

try:
	while True:
		cHardware.manage()
except KeyboardInterrupt:
	raise

