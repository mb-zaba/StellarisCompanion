import time
import psutil
from collections import deque
import re
from multiprocessing import Process,Pipe

class LogReader:
	def __init__(self):
		self.regex = re.compile('\$(.*)\$', re.MULTILINE)
		self.dataDict = { # DAYS_PASSED will be X, others will be Y
					'EMPIRE_NAME': '',
					'DAYS_PASSED': deque(maxlen=12),
					'MINERAL_PRICE': deque(maxlen=12),
					'FOOD_PRICE': deque(maxlen=12),
					'CONSUMER_GOODS_PRICE': deque(maxlen=12),
					'ALLOY_PRICE': deque(maxlen=12),
					'MOTES_PRICE': deque(maxlen=12),
					'CRYSTALS_PRICE': deque(maxlen=12),
					'GAS_PRICE': deque(maxlen=12),
					'DARK_MATTER_PRICE': deque(maxlen=12),
					'ZRO_PRICE': deque(maxlen=12),
					'LIVING_METAL_PRICE': deque(maxlen=12),
				}

	# Checks if Stellaris is open, if not, exit
	def stellarisIsOpen(self):
		isOpen = "stellaris.exe" in (i.name() for i in psutil.process_iter())
		if not isOpen:
			print(f'Stellaris is not started. You can visualize the latest data with displayer.py')
			exit(1)


	# Read in realtime the game.log file, where the Stellaris Companion will dump the data
	def reader(self):
		print('Starting reader...')
		logDir = "../../logs/"
		with open(f'{logDir}game.log', 'r') as stellarisLogs:
			while True:
				logData = stellarisLogs.readline()
				if not logData:
					time.sleep(0.1) # Sleep briefly
					continue
				yield logData

	# Sends data to main.py after parsing
	def dataSender(self, logQueue):
		#print("Reader")
		logLine = self.reader()
		for log in logLine:
			time.sleep(0.1)
			self.dataPresenter(log)
			logQueue.put(self.dataDict)

	def timeToDate(self, timestamp):
		year = 2200 + (timestamp // 360)
		month = ((timestamp % 360) // 30) + 1
		date = f"{str(year)}.{str(month).zfill(2)}.01"
		#print(date)
	
	def dataPresenter(self, dataLine):
		print('Starting parser...')
		
		parsedData = self.parser(dataLine)
		if parsedData is not None:
			parsedData = parsedData[0].split(';')
			self.dataDict['EMPIRE_NAME'] = parsedData[0]
			self.dataDict['DAYS_PASSED'].append(int(parsedData[1]))
			self.dataDict['MINERAL_PRICE'].append(float(parsedData[2]))
			self.dataDict['FOOD_PRICE'].append(float(parsedData[3]))
			self.dataDict['CONSUMER_GOODS_PRICE'].append(float(parsedData[4]))
			self.dataDict['ALLOY_PRICE'].append(float(parsedData[5]))
			self.dataDict['MOTES_PRICE'].append(float(parsedData[6]))
			self.dataDict['CRYSTALS_PRICE'].append(float(parsedData[7]))
			self.dataDict['GAS_PRICE'].append(float(parsedData[8]))
			self.dataDict['DARK_MATTER_PRICE'].append(float(parsedData[9]))
			self.dataDict['ZRO_PRICE'].append(float(parsedData[10]))
			self.dataDict['LIVING_METAL_PRICE'].append(float(parsedData[11]))

	def parser(self, dataLine):
		logCSV = re.findall(self.regex, dataLine)
		if len(logCSV) > 0:
			return logCSV

if __name__ == '__main__':
	logDir = "../../logs/"
	LogReader.stellarisIsOpen()
	with open(f'{logDir}game.log', 'r') as stellarisLogs:
		print('Starting')
		logLine = LogReader.reader()
		for log in logLine:
			print(log)