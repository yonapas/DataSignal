from scipy.fftpack import fft, ifft
import numpy as np
from obspy import read, read_inventory, Stream
import matplotlib.pyplot as plt
import matplotlib as mpl
from glob import glob
from DButils import DBtraces
from app.main import pasData
import datetime
from os import mkdir
import showgraph
from showgraph import Graph
import save_traces


def makePlot(N, dt, x, y, xf, yf, staname, eventname, filt=False):
	plt.subplots_adjust()

	time = plt.subplot(2,2,1)
	time.set_title("{0}, dt:{1}".format( staname, dt))
	time.plot(x, y)

	plt.subplot(2,2,2)
	plt.loglog(xf, 2.0/N * np.abs(yf[0:N//2]))
	plt.axvline(x=1/(2*dt), color="red", lw=2)
	plt.grid()
	if filt:
		plt.savefig("{0}/{1}_filter".format(eventname, staname))
	else:
		plt.savefig("{0}/{1}".format(eventname, staname))
	plt.close()
	return


mpl.rcParams["lines.linewidth"] = 0.4

TYPE="ACC"

files = glob("*002.mseed")
Traces = DBtraces()
dt_list = {}
for file in files:

	traces = read(file)
	event_name = file.split(".mseed")[0]
	print event_name
	try:
		inv = read_inventory("{0}.xml".format(event_name))
		d = datetime.datetime.strptime(event_name, '%Y-%m-%dT%H:%M:%S.%f')
		d = d.strftime('%Y%m%d%H%M%S')
		event_name = d
	except:
		print "no xml file found {0}".format(file)

	try:
		mkdir(event_name)
	except OSError:
		pass # alredy exsit

    # merge traces by ID
	print "len before merge:" , len(traces)
	traces.merge(1, fill_value='interpolate')
	print "len after merge:" , len(traces)
	id_dt=[]


	for tr in traces:
		tr.data = tr.data[:-1]

		if tr.meta["network"] == "IS":
			tr.remove_response(inventory=inv, output=TYPE)

		if tr.meta["network"] == "AA":
			cha =  tr.meta["channel"]
			if "H" in cha[1]:
				print "skipping H channel..."
				continue

		#try:
		location = tr.meta["location"]
		network = tr.meta["network"]
		station = tr.meta["station"]
		channel = tr.meta["channel"]
		name = tr.get_id().replace(".", "_")
		dt = float(tr.meta["delta"])

		if dt == 0.02:
			id_dt.append(tr.get_id())

		else:
			time, acc, freq, ampli, N = save_traces.do_fft(tr)
			Filter = 0
			highpass = False
			lowpass = False
			Tstart = tr.stats.starttime
			FreqPass = False
			Tstop = False

			canvasName, value = showgraph.set_plot(time, acc, freq, ampli, dt, N, name, event_name)

			tr_filter = tr.copy()
			while canvasName != None:
				if canvasName == "Frequency":
					FreqPass = round(value, 3)
				if canvasName == "Time":
					Tstop = round(value, 3)

				if FreqPass:
					if FreqPass < 2:
						Filter = "highpass"
						highpass = FreqPass
						# Use filter, and show graph agin
					if FreqPass > 5:
						Filter = "lowpass"
						lowpass = FreqPass
						# Use filter, and show graph agin
					tr_filter.filter(Filter, freq=FreqPass, corners=2, zerophase=True)
				if Tstop:
					tr_filter.trim(Tstart, Tstart +Tstop)

				Ftime, Facc, Ffreq, Fampli, FN = save_traces.do_fft(tr_filter)
				canvasName, value= showgraph.set_plot(Ftime, Facc, Ffreq, Fampli, dt, FN, name, event_name, low=lowpass, high=highpass, time=Tstop)


			# tr_filter. - baseline
			print "save trace with highpass {0}, lowpass {1}, cut time {2} [sec]".format(highpass, lowpass, Tstop)
			save_traces.SavePlotOriNew(tr, tr_filter, event_name, name, lowpass, highpass, Tstop)
			metafile = open("{0}/{1}_meta.txt".format(event_name, name), "w")
			for item in tr_filter.meta:
				metafile.write("{0}\n".format(tr_filter.meta[item]))
			metafile.close()
			tr_filter.write("{0}/{1}_data.txt".format(event_name, name), format="SLIST")

			

