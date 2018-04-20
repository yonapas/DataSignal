from obspy import read, read_inventory
from glob import glob
from DButils import DBtraces
import datetime
from os import mkdir
import showgraph
import save_traces
import magnitude
import settings
import baseline


TYPE = settings.remove_response_unit
raw_data_folder = settings.raw_data_folder
saved_data_folder = settings.save_data_folder
save_format = settings.save_traces_format

files = glob("{0}/*501.mseed".format(raw_data_folder))
# Traces = DBtraces()
dt_list = {}

for f in files:
	traces = read(f)
	event_name = f.split(".mseed")[0].split("/")[-1]
	print event_name
	try:
		inv = read_inventory("{0}/{1}.xml".format(raw_data_folder ,event_name))
		d = datetime.datetime.strptime(event_name, '%Y-%m-%dT%H:%M:%S.%f')
		d = d.strftime('%Y%m%d%H%M%S')
		event_name = d
	except:
		print "no xml file found {0}".format(f)

	# find magnitude for the event
	details = magnitude.find_eq_details(event_name)
	fc = magnitude.calc_fc(details["mw"])
	print round(fc, 3)

	try:
		# try to create new folder for saved traces
		mkdir("{0}/{1}".format(saved_data_folder, event_name))
	except OSError:
		pass # alredy exsit

	# merge traces by ID
	traces.merge(1, fill_value='interpolate')
	id_dt = []

	for tr in traces:
		tr.data = tr.data[:-1]

		if tr.meta["network"] == "IS":
			tr.remove_response(inventory=inv, output=TYPE)

		if tr.meta["network"] == "AA":
			cha = tr.meta["channel"]
			if "H" in cha[1]:
				print "skipping H channel..."
				continue

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

			canvasName, value = showgraph.set_plot(time, acc, freq, ampli, dt, N, name, event_name, fc)

			tr_filter = tr.copy()
			while canvasName != None:
				if canvasName == "Frequency":
					FreqPass = round(value, 3)

				if canvasName == "Time":
					Tstop = round(value, 3)

				if canvasName == "reset":
					tr_filter = tr.copy()
					FreqPass = False
					Tstop = False

				if FreqPass:
					if FreqPass < fc:
						Filter = "highpass"
						highpass = FreqPass
						# Use filter, and show graph agin
					if FreqPass > fc+2.0:
						Filter = "lowpass"
						lowpass = FreqPass
						# Use filter, and show graph agin
					tr_filter.filter(Filter, freq=FreqPass, corners=2, zerophase=True)
				if Tstop:
					tr_filter.trim(Tstart, Tstart +Tstop)

				Ftime, Facc, Ffreq, Fampli, FN = save_traces.do_fft(tr_filter)
				canvasName, value = showgraph.set_plot(Ftime, Facc, Ffreq, Fampli, dt, FN, name, event_name, fc,
													   low=lowpass, high=highpass, time=Tstop)

			# tr_filter. - baseline
			tr_baseline = baseline.useBaseLine(tr_filter, inv, event_name, name)

			# save data
			print "save trace with highpass {0}, lowpass {1}, cut time {2} [sec]".format(highpass, lowpass, Tstop)
			# save_traces.SavePlotOriNew(tr, tr_filter, event_name, name, fc, lowpass, highpass, Tstop)
			save_traces.SavePlotOriNew(Ftime, Facc, Ffreq, Fampli, FN, time, acc, freq, ampli, dt, N, name, event_name, fc, lowpass=lowpass, highpass=highpass, timecut=Tstop)
			save_traces.SaveTracesInFile(tr_filter, event_name, name, dt)
			save_traces.SaveMetaData(tr_filter, event_name, name, location)
