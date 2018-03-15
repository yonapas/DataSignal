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
	
	old_tr = traces[0]

	for tr in traces:
		tr.data = tr.data[:-1]
		if old_tr.get_id() == tr.get_id():
			if old_tr.data.dtype == tr.data.dtype:
				tr = old_tr + tr
				old_tr = tr
		else:
			#old_tr.plot(output="{0}".format(old_tr.get_id()))
			full_trace = old_tr
			print full_trace
			old_tr = tr

			if full_trace.meta["network"] == "IS":
				full_trace.remove_response(inventory=inv, output=TYPE)
			
			try:
				location = full_trace.meta["location"]
				network = full_trace.meta["network"]
				station = full_trace.meta["station"]
				channel = full_trace.meta["channel"]
				dt = float(full_trace.meta["delta"])

				Ts = dt; # sampling interval
				print dt
				Fs = 1/dt # sampling rate
				
				y = full_trace.data
				print y
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
				print yf
				yf = yf[range(n/2)]
				# xf = np.linspace(0.0, 1/(dt), N//2)

				# pasData({"time":[x, y], "fft": [xf, yf]})


				if (len(t)-len(y) == 1):
					t = t[:-1]

				makePlot(n, dt, t, y, freq, yf, station, channel, network)
				
			except:
				print tr.get_id()
				old_tr = tr

		"""
		Traces.insertTime(long(event_name), data, dt, station, network, channel, "remove_response")
		Traces.insertFreq(long(event_name), [xf, yf], dt, station, network, channel, "remove_response")
		"""
			