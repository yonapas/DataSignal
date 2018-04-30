import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import smooth

G = 9.81


class graph():

	def __init__(self, tr, dt, name, ename, fc):
		self.trace = tr
		self.dt = dt
		self.N = None
		self.name = name
		self.ename = ename
		self.fc = fc
		self.ax1 = None
		self.ax2 = None
		self.fig = None
		self.tstop = None
		self.lowpass = None
		self.highpass = None
		self.x = None
		self.y = None
		self.xf = None
		self.yf = None
		if self.trace.meta["network"] == "AA":
			self.highpass = 0.1

	def init_graph(self):
		"""
		initial canves for each trace.
		should run only once for trace
		"""

		mpl.rcParams["lines.linewidth"] = 0.4

		self.fig = plt.figure(figsize=(8, 6))
		self.ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=2)
		self.ax2 = plt.subplot2grid((2, 2), (1, 0), colspan=1)
		self.set_titles()
		
		self.fig.canvas.mpl_connect('pick_event', self.onpick)
		self.fig.canvas.mpl_connect('key_press_event', self.press)

		manager = plt.get_current_fig_manager()
		manager.resize(*manager.window.maxsize())

		if self.lowpass or self.highpass or self.tstop:
			pass
		else:
			self.set_data()
			self.set_ori_date()
			plt.show()

	def set_ori_date(self):
		"""
		save Original parameters of trace.
		should run only once
		"""
		self.timeOri = self.x
		self.accOri = self.y 
		self.freqOri = self.xf
		self.ampliOri = self.yf
		self.NOri = self.N

	def set_titles(self):
		"""
		should run only once
		"""
		self.fig.suptitle('{0} {1} ,dt:{2}'.format(self.name, self.ename, self.dt), fontsize=20)
		self.ax1.set_title("press Esc for reset signal", fontsize=12)
		self.ax1.set_ylabel("ACC [g]")
		self.ax1.set_xlabel("time [sec]")

		# set name for any canvas:
		self.ax1._label = "Time"
		self.ax2._label = "Frequency"

	def set_data(self):
		"""
		run after change or filters
		"""
		yy = 2.0/self.N * np.abs(self.yf[0:self.N//2])
		smoo_y = smooth.smoo(yy, 101)

		self.ax1.plot(self.x, self.y, 'k', picker=7)
		self.ax2.loglog(self.xf, 2.0/self.N * np.abs(self.yf[0:self.N//2]), "k", picker=2)
		self.ax2.loglog(self.xf, smoo_y, linewidth=1.0)
		self.ax2.axvline(x=self.fc, color='red')

	def reset(self):
		"""
		reset the graphs, and pick filters again
		"""
		self.x, self.y, self.xf, self.yf, self.N = self.get_ori_data()
		self.lowpass, self.highpass, self.tstop = None, None, None
		self.init_graph()

	def onpick(self, event):
		self.xpick = event.mouseevent.xdata
		self.ypick = event.mouseevent.ydata
		self.labelpick = event.mouseevent.inaxes._label
		# plt.close()
		self.update()

	def press(self, event):
		self.key = event.key
		if self.key == "escape":
			self.close()
			self.reset()
		if self.key == "n":
			self.xpick = self.key
			self.close()

	def getXY(self):
		return self.xpick

	def update(self):
		self.ax2.cla()
		self.ax1.cla()

		if self.labelpick == "Frequency":
			self.filter = self.xpick
			self.filters()

		if self.labelpick == "Time":
			self.tstop = self.xpick
			self.cutTime()

		self.fig.canvas.draw()
		self.fig.canvas.flush_events()
		self.set_notes()
		self.set_data()
		plt.show()
	
	def cutTime(self):
		tstart =  self.trace.stats.starttime
		self.trace.trim(tstart , tstart +self.tstop)
		self.dofft()

	def filters(self):

		if self.filter < self.fc:
			self.highpass = self.filter
			self.trace.filter("highpass", freq=self.highpass, corners=2, zerophase=True)

		if self.filter > self.fc +2.0 :
			self.lowpass = self.filter
			self.trace.filter("lowpass", freq=self.lowpass, corners=2, zerophase=True)

		self.dofft()

	def set_notes(self):

		if self.lowpass or self.highpass:
			self.ax2.text(0.95, 0.01, 'highpass = {0} lowpass = {1}'.format(self.highpass, self.lowpass),
			verticalalignment='bottom', horizontalalignment='right',
			transform=self.ax2.transAxes,
			color='red', fontsize=10)

		if self.tstop:
			self.ax1.text(0.95, 0.01, 'cut time = {0}'.format(self.tstop),
			verticalalignment='bottom', horizontalalignment='right',
			transform=self.ax1.transAxes,
			color='red', fontsize=10)

	def getfilters(self):
		return self.tstop, self.lowpass, self.highpass

	def getfiltertrace(self):
		return self.trace

	def get_Filter_data(self):
		return self.x, self.y, self.xf, self.yf, self.N

	def get_ori_data(self):
		return self.timeOri, self.accOri, self.freqOri, self.ampliOri, self.NOri

	def dofft(self):
		Ts = self.trace.stats.delta # sampling interval
		Fs = 1/Ts # sampling rate
		
		y = self.trace.data/G
		n = len(y)
		t = np.arange(0, n*Ts, Ts) # time vector
		k = np.arange(n)
		T = n/Fs
		
		freq = k/T
		freq = freq[range(n/2)]

		yf = np.fft.fft(y)*2/n
		# yf = fft(y)
		self.yf = yf[range(n/2)]
		# xf = np.linspace(0.0, 1/(dt), N//2)

		if (len(t)-len(y) == 1):
			t = t[:-1]
		self.x = t
		self.xf = freq
		self.y = y
		self.N = n

	@staticmethod
	def close():
		plt.close()
