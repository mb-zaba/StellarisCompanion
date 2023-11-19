# main.py
from logReader import LogReader
#from dataParser import DataParser
from multiprocessing import Process,Queue,Pipe
import time
import dash
from dash.dependencies import Output, Input
from dash import dcc, html
import plotly
import plotly.graph_objs as go


class DataDisplay:
	def __init__(self):
		self.dataDict
	def showData(self, dataQueue):
		print('Starting display...')
		while True:
			time.sleep(0.1)
			self.dataDict = dataQueue.get()
			print(self.dataDict)

if __name__ == '__main__':
	reader = LogReader()
	display = DataDisplay()

	# Reader to main.py communication
	logQueue = Queue()

	# start s2 as another process
	s2 = Process(target=display.showData, args=(logQueue,))
	s2.daemon = True
	s2.start()     # Launch the stage2 process

	reader.dataSender(logQueue) # start sending stuff from s1 to s2
	
	#s2.join() # wait till s2 daemon finishes
