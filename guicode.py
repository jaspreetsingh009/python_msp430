#!/usr/bin/python

import os
import sys
import serial
import Tkinter
import threading
import numpy as np
import matplotlib.pyplot as plt
import tkMessageBox
from collections import deque

var = 0

class acc_gui(Tkinter.Tk):
	
	accX_Var = ""    #accX Data
	accY_Var = ""    #accY Data
	accZ_Var = ""    #accZ Data
	
	def __init__(self, parent):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent  #reference
		self.initialize()
		
	def __del__(self):
		print "Tkinter instance deleted"
		
	def initialize(self):  #initialize function
		self.grid()
		self.accX_Var = Tkinter.StringVar()
		self.accY_Var = Tkinter.StringVar()
		self.accZ_Var = Tkinter.StringVar()
		
		#Textboxes
		self.entry1 = Tkinter.Entry(self, textvariable = self.accX_Var, width = 11)
		self.entry1.grid(column=1, row=0)
		self.entry2 = Tkinter.Entry(self, textvariable = self.accY_Var, width = 11)
		self.entry2.grid(column=1, row=1)
		self.entry3 = Tkinter.Entry(self, textvariable = self.accZ_Var, width = 11)
		self.entry3.grid(column=1, row=2)
		
		#labels
		label1 = Tkinter.Label(self, text = "Acc X:")
		label1.grid(column = 0, row = 0)
		label2 = Tkinter.Label(self, text = "Acc Y:")
		label2.grid(column = 0, row = 1)
		label3 = Tkinter.Label(self, text = "Acc Z:")
		label3.grid(column = 0, row = 2)
		
		#buttons
		button1 = Tkinter.Button(self, text = "Connect", command = self.OnButtonClick1)
		button1.grid(column = 0, row = 4)
		button2 = Tkinter.Button(self, text = "Disconnect", command = self.OnButtonClick2)
		button2.grid(column = 1, row = 4)
			
		self.grid_columnconfigure(0, weight = 10)
		self.resizable(False, False)	
		
	def accX_Update(self, accX):   #Update accX Data
		self.accX_Var.set(accX)
		
	def accY_Update(self, accY):   #Update accY Data
		self.accY_Var.set(accY)
		
	def accZ_Update(self, accZ):   #Update accZ Data
		self.accZ_Var.set(accZ)
		
	def OnButtonClick1(self):
		print "You Clicked the Connect button"
		global var
		if(var == 0 or var == 2):
			var = 1
			print 'plotting data...'
			SerialThread().start()  #Start Serial Data Thread
	
	def OnButtonClick2(self):
		print "You Clicked the Disconnect button"
		global var	
		var = 2

class SerialData:
	
	def __init__(self, maxLen):  # Class Constructor
	    # Empty deque(list) of maxLen element
		self.ax = deque([0.0]*maxLen)
		self.ay = deque([0.0]*maxLen)
		self.az = deque([0.0]*maxLen)
		self.maxLen = maxLen
		
		print "SerialData instance created"
		
	def __del__(self):
		print "SerialData Instance Deleted"
		
	def addToBuf(self, buf, val):  # append data to buffer
		if (len(buf) < self.maxLen):
			buf.append(val)
		else:
			buf.pop() 
			buf.appendleft(val)
			
	def addx(self, data1):  # append data to ax buffer (deque)
		self.addToBuf(self.ax, data1)
	def addy(self, data2):
		self.addToBuf(self.ay, data2)
	def addz(self, data3):
		self.addToBuf(self.az, data3)
	
class SerialPlot:
	
	def __init__ (self, serialData):
		
		print "SerialPlot instance created"
		
		plt.ion()
		
		plot1 = plt.subplot(311)
		plt.ylabel("Acc X Data")
		self.axline, = plot1.plot(serialData.ax)
		plt.ylim([-255, 255])
		
		plot2 = plt.subplot(312)
		plt.ylabel("Acc Y Data")
		self.ayline, = plot2.plot(serialData.ay)
		plt.ylim([-255, 255])
		
		plot3 = plt.subplot(313)
		plt.ylabel("Acc Z Data")
		self.azline, = plot3.plot(serialData.az)
		plt.ylim([-255, 255]) 
	
	def __del__(self):
		print "SerialPlot Instance Deleted"
		
	def updateX(self, serialData):
		self.axline.set_ydata(serialData.ax)
		plt.draw()
		
	def updateY(self, serialData):
		self.ayline.set_ydata(serialData.ay)
		plt.draw()
	
	def updateZ(self, serialData):
		self.azline.set_ydata(serialData.az)
		plt.draw()

class SerialThread(threading.Thread):
	def run(self):
		try:
			ser = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=1)
		except serial.SerialException as e:
			print("Could not open port '{}': {}".format(com_port, e))
			os._exit("Cannot Open Serial Port...")
			
		serialData = SerialData(100) # maxLen = 100
		serialPlot = SerialPlot(serialData)
		
		while var == 1:
			try:
				line = ser.readline()
				if(line != "" and len(line) == 6):
					if(line[4] == 'I'):
						if(line[0] == '-'):
							line = (float)(line[1:4])
							line = -line
						else:
							line = line[1:4]
							
						serialData.addx(line)
						serialPlot.updateX(serialData)
						app.accX_Update(line)
					
					elif(line[4] == 'J'):
						if(line[0] == '-'):
							line = (float)(line[1:4])
							line = -line
						else:
							line = line[1:4]
							
						serialData.addy(line)
						serialPlot.updateY(serialData)
						app.accY_Update(line)
					
					elif(line[4] == 'K'):
						if(line[0] == '-'):
							line = (float)(line[1:4])
							line = -line
						else:
							line = line[1:4]
						serialData.addz(line)
						serialPlot.updateZ(serialData)
						app.accZ_Update(line)
				else:
					print "Null or invalid data"
					
			except KeyboardInterrupt:
				print 'exiting'
				break
		else:
			ser.flushInput()
			ser.close()
			plt.savefig('testplot.png')
			print "Graph saved at", os.getcwd()
			plt.close('all')
			del serialData
			del serialPlot
			print "Serial Terminal Closed"
			print "Matplotlib plot closed"

def callback():
	
	if(var == 1):
		tkMessageBox.askokcancel("Disconnect", "Please Disconnect the application first")
	
	elif tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
		print "Exiting Program..."
		os._exit(1)

# main
if __name__ == "__main__":
	app = acc_gui(None)  #No parent since it's THE first GUI Element
	app.title('Acc GUI')
	app.protocol("WM_DELETE_WINDOW", callback)
	app.mainloop()  #Loop indefinitely and wait for events
