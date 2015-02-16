import pyaudio
from pylab import *
import numpy
import threading

RATE = 44100
BUFFER_SIZE = 1024
RECORD_TIME = 1.0 # seconds
DATA_BUFFER_SIZE =  2 * RATE
FORMAT = pyaudio.paFloat32
CHANNELS = 1

class Recorder():

	def __init__(self, rate = RATE, buffersize = BUFFER_SIZE, time = RECORD_TIME, databuffersize = DATA_BUFFER_SIZE):
		self.rate = rate
		self.buffersize = buffersize
		self.databuffersize = databuffersize
		self.record_time = time
		self.p = pyaudio.PyAudio()
		self.datacount = 0
		self.recordingTime = 0.0
		#self.stop = False
		self.overflow = False
		self.time = RECORD_TIME
		self.frames = numpy.zeros([DATA_BUFFER_SIZE])
		self.done = False
		self.t = threading.Thread(target = self.record)
		self.stream = self.p.open(format = FORMAT,
			channels = CHANNELS,
			rate = self.rate,
			input = True,
			frames_per_buffer = BUFFER_SIZE)

	def getAudio(self):
		audiostring = self.stream.read(self.buffersize)
		return numpy.fromstring(audiostring, 'Float32')

	def pushAudio(self):
		data = self.getAudio()
		if self.datacount < self.databuffersize:
			roomAv = self.databuffersize - self.datacount # compute room available
			#print 'Available:', roomAv, 'Appending: ', data[0:roomAv].size, '@ ', self.recordingTime, 'Data count:', self.datacount
			self.frames = numpy.append(self.frames, data[0:roomAv])
			self.datacount += data[0:roomAv].size
		else:
			print 'Buffer full @ ', self.recordingTime, 'Dropping data.'
		self.recordingTime += float(data.size)/RATE

	def popAudio(self):
		revdata = self.frames[::-1]
		data = revdata[0:self.datacount-1]
		self.datacount = 0
		return data

	def start(self):
		self.done = False
		self.t.start()

	def record(self):
		print 'Recording.'
		while not self.done:
			self.pushAudio()
			if self.recordingTime >= self.time:
				self.stop()

	def stop(self):
		self.stream.close()
		self.done = True

	def isDone(self):
		return self.done
			
if __name__ == '__main__':
	r = Recorder()
	r.start()
	while not r.isDone():
		pass
	audio = r.popAudio()
	t = linspace(0, r.recordingTime, audio.size)
	plot(t, audio)
	show()

	
