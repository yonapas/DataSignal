from scipy.fftpack import fft
import numpy as np
from obspy import read, read_inventory, Stream
import matplotlib.pyplot as plt
import matplotlib as mpl 
from glob import glob 
from DButils import DBtraces
from app.main import pasData


def makePlot(N, dt, x, y, xf, yf, sta, cha, net):
	plt.subplots_adjust()

	time = plt.subplot(2,2,1)
	time.set_title("{0} {1} {2}, dt:{3}".format( net, sta, cha, dt))
	time.plot(x, y)

	plt.subplot(2,2,2)
	plt.loglog(xf, 2.0/N * np.abs(yf[0:N//2]))
	plt.axvline(x=1/(2*dt), color="red", lw=2)
	plt.grid()
	plt.savefig("{0}_{1}_{2}".format(net, sta, cha))
	plt.close()
	return

def filter_by_time(time, data, cut):
	matrix = np.stack((time, data))
	new_mat = matrix[:,:cut]
	return new_mat[0], new_mat[1]


def CheckStations(trace, pre_trace):
	"""
	the function handle with many traces for one station

	the function get trace and previos trace, and check the stataion is equal.

	if same station --> add the new trace to pre trace, 
	else --> save plot
	"""

	if len(trace.data) > 1:
		# if pre_trace not None
		if pre_trace:
			# define name to pre trace
			pre_name = "{0}_{1}_{2}".format(pre_trace.meta["network"], 
				pre_trace.meta["station"], pre_trace.meta["channel"])

			# define name to trace
			name = "{0}_{1}_{2}".format(trace.meta["network"], 
				trace.meta["station"], trace.meta["channel"])
			# check if equal
			if pre_name == name:
				# add to previos trece
				return True

			# is new station, plot resulte
			else:
				return False
							

mpl.rcParams["lines.linewidth"] = 0.4

TYPE="ACC"
time_filt = int((4*60)/0.025)
print time_filt

files = glob("*502.mseed")
Traces = DBtraces()
for file in files:

	traces = read(file)
	event_name = file.split(".")[0]

	try:
		inv = read_inventory("{0}.xml".format(event_name))
	except:
		print "no xml file found {0}".format(file)
	
	old_tr = None
	
	for tr in traces:
		
		network = tr.meta["network"]
		station = tr.meta["station"]
		channel = tr.meta["channel"]
		dt = float(tr.meta["delta"]) # delta t
		print len(tr.data), station, channel, network

			# delete last item in trace
 		tr.data = tr.data[:-1]
		same_station = CheckStations(tr, old_tr)
		if same_station:
			tr.data = tr.data+old_tr.data

		if same_station == False:
			if network == "AA":
				print "AA"
			if network == "IS":
				print "IS" 
			

		old_tr = tr

		
		"""
		TODO:
		"""
		
		if network == "IS":
			try:
				tr.remove_response(inventory=inv, output=TYPE)
				
				
				location = tr.meta["location"]

				Ts = dt; # sampling interval
				print dt
				Fs = 1/dt # sampling rate
				
				y = tr.data
				# N = len(tr.data)
				n = len(y)
				t = np.arange(0, n*Ts, Ts) # time vector
				k = np.arange(n)
				T = n/Fs

				#t, y = filter_by_time(t, y , time_filt)
				# x = np.arange(0.0, N*dt, dt)
				
				freq = k/T
				freq = freq[range(n/2)]

				# yf = fft(y)
				yf = np.fft.fft(y)*2/n
				yf = yf[range(n/2)]
				# xf = np.linspace(0.0, 1/(dt), N//2)

				# pasData({"time":[x, y], "fft": [xf, yf]})


				if (len(t)-len(y) == 1):
					t = t[:-1]

				makePlot(n, dt, t, y, freq, yf, station, channel, network)
				
				"""
				# save in db 
				# x = x.tolist() #save just delta
				data = y.tolist()
				xf = xf.tolist()
				yf = str(yf.tolist())
				

				
				Traces.insertTime(long(event_name), data, dt, station, network, channel, "remove_response")
				Traces.insertFreq(long(event_name), [xf, yf], dt, station, network, channel, "remove_response")
				"""
					
			except:
				print "error", network, station, dt
				pass
				#print "t-",len(t) ,"y-" ,len(y), "freq-",len(freq), "yf-",len(yf)
