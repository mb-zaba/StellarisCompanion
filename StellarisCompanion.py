import os
#import logging
from multiprocessing import Process,Queue
import time
import re
import dash
from dash import Dash, dcc, html, Input, Output, callback
import plotly
from plotly.subplots import make_subplots
from collections import deque

global LOG_FILE_PATH
LOG_FILE_PATH = os.environ['USERPROFILE'] + "\\Documents\\Paradox Interactive\\Stellaris\\logs\\game.log"

app = Dash(__name__,)
app.layout = html.Div(
	html.Div([
		html.H4('Stellaris Live Data'),
		dcc.Graph(id='live-update-graph'),
		dcc.Interval(
			id='interval-component',
			interval=500,
			n_intervals=0
		)
	])
)
DEQUE_MAX_LEN = 24
data = { # DAYS_PASSED will be X, others will be Y
		'EMPIRE_NAME': '',
		'DAYS_PASSED': deque(maxlen=DEQUE_MAX_LEN),
		'MINERAL_PRICE': deque(maxlen=DEQUE_MAX_LEN),
		'FOOD_PRICE': deque(maxlen=DEQUE_MAX_LEN),
		'CONSUMER_GOODS_PRICE': deque(maxlen=DEQUE_MAX_LEN),
		'ALLOY_PRICE': deque(maxlen=DEQUE_MAX_LEN),
		'MOTES_PRICE': deque(maxlen=DEQUE_MAX_LEN),
		'CRYSTALS_PRICE': deque(maxlen=DEQUE_MAX_LEN),
		'GAS_PRICE': deque(maxlen=DEQUE_MAX_LEN),
		'DARK_MATTER_PRICE': deque(maxlen=DEQUE_MAX_LEN),
		'ZRO_PRICE': deque(maxlen=DEQUE_MAX_LEN),
		'LIVING_METAL_PRICE': deque(maxlen=DEQUE_MAX_LEN),
	}
def readQueue(queue):
	return queue.get()

@callback(Output('live-update-graph', 'figure'),
		  Input('interval-component', 'n_intervals'))
def update_graph_live(n):
	for i in range(1):
		#print(readQueue(queue))
		dataList = readQueue(queue)
		data['EMPIRE_NAME'] = dataList[0]
		data['DAYS_PASSED'].append(int(dataList[1]))
		data['MINERAL_PRICE'].append(float(dataList[2]))
		data['FOOD_PRICE'].append(float(dataList[3]))
		data['CONSUMER_GOODS_PRICE'].append(float(dataList[4]))
		data['ALLOY_PRICE'].append(float(dataList[5]))
		data['MOTES_PRICE'].append(float(dataList[6]))
		data['CRYSTALS_PRICE'].append(float(dataList[7]))
		data['GAS_PRICE'].append(float(dataList[8]))
		data['DARK_MATTER_PRICE'].append(float(dataList[9]))
		data['ZRO_PRICE'].append(float(dataList[10]))
		data['LIVING_METAL_PRICE'].append(float(dataList[11]))
	
	print(data)
	fig = make_subplots(rows=2, cols=1)
	fig['layout']['margin'] = {
		'l': 30, 'r': 10, 'b': 30, 't': 10
	}
	fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor':'left'}
	fig.append_trace({
		'x': list(data['DAYS_PASSED']),
		'y': list(data['MINERAL_PRICE']),
		'name': 'Minerals',
		'mode': 'lines+markers',
		'type': 'scatter'
	}, 1, 1)
	fig.append_trace({
		'x': list(data['DAYS_PASSED']),
		'y': list(data['FOOD_PRICE']),
		'name': 'Food',
		'mode': 'lines+markers',
		'type': 'scatter'
	}, 2, 1)

	return fig

class StellarisCompanion:
	def __init__(self):
		self.regex = re.compile('\$(.*)\$', re.MULTILINE)
	
	# Reads the log file
	def follow(self):
		with open(LOG_FILE_PATH, 'r') as gameLogFile:
			gameLogFile.seek(0)
			while True:
				line = gameLogFile.readline()
				if not line:
					time.sleep(0.1)
					continue
				yield line

	def parseLine(self, queue):
		loglines = self.follow()
		for line in loglines:
			parsed = re.findall(self.regex, line)
			if len(parsed) > 0:
				queue.put(parsed[0].split(';'))
			

if __name__ == '__main__':
	#logging.basicConfig(filename='app.log', encoding='utf-8', level=logging.DEBUG)

	sc = StellarisCompanion()

	queue = Queue()

	# This process follows the log file and parses each line
	sc = Process(target = sc.parseLine, args=(queue,))
	sc.start()
	app.run(debug=True)
