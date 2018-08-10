from obspy import read, read_inventory
import datetime
from os import mkdir
from save_traces import Save
import metaData
import settings
import baseline
from GraphIt import graph
import AAnetwork
import petl as etl
from common import MseedExtractor, CheckAgain, CorrectTrace, dofft

TYPE = settings.remove_response_unit
raw_data_folder = settings.raw_data_folder
saved_data_folder = settings.save_data_folder
save_format = settings.save_traces_format
CheckAgainFolder = settings.CheckAgainFolder
CheckAgainFile = settings.CheckAgainFile
mode = settings.mode
flatfile = settings.oriflatfile

check_trace_table = False

extract = MseedExtractor(mode)
trace_bin = CheckAgain()
files = extract.get_file()
FF = CorrectTrace(flatfile)


for f in files:
	traces = read(f)
	event_name_o = f.split(".mseed")[0].split("/")[-1]
	print event_name_o
	try:
		inv = read_inventory("{0}/{1}.xml".format(raw_data_folder ,event_name_o))
		b = datetime.datetime.strptime(event_name_o, '%Y-%m-%dT%H_%M_%S')
		d = b.strftime('%Y%m%d%H%M%S')
		event_name = d

	except Exception:
		print "no xml file found {0}".format(f)
		continue

	# find magnitude for the event
	YEAR = str(b.year)
	MODY = "{0}{1}".format(b.month, b.day)
	HRMN = "{0}{1}".format(b.hour, b.second)
	FF.load_event_data(YEAR, MODY, HRMN)

	# find magnitude for the event
	details = metaData.find_eq_details(event_name)
	# fc = magnitude.calc_fc(details["mw"])
	epiLocation = details["epi_center"]
	# metaData.loadStationData(inv)

	try:
		# try to create new folder for saved traces
		mkdir("{0}/{1}".format(saved_data_folder, event_name))
	except OSError:
		pass
		# already exsit

	# merge traces by ID
	traces.merge(1, fill_value='interpolate')
	print len(traces)
	id_dt = []

	for tr in traces:
		name = tr.get_id().replace(".", "_")
		if check_trace_table:
			table = etl.select(check_trace_table, lambda rec: rec.sta == name and rec.mseedname == event_name_o)
			if etl.nrows(table) > 0:
				pass
			else: continue

		tr.data = tr.data[:-1]
		try:
			seismograph = inv.get_channel_metadata(tr.get_id())
		except:
			print "no inv data"
			print tr.get_id()
			continue

		distance = metaData.calculate_distance(seismograph, epiLocation)
		seismograph["network"] = tr.meta["network"]
		seismograph["station"] = tr.meta["station"]
		seismograph["channel"] = tr.meta["channel"]
		name = tr.get_id().replace(".", "_")
		exist_filters = FF.filters_exist(name)

		dt = float(tr.meta["delta"])

		if seismograph["network"] == "GE" or dt == 0.02:
			# ToDo : Ge process, acc unit
			id_dt.append(tr.get_id())
			continue

		if seismograph["network"] == "IS":
			pre_filt = (0.005, 0.006, 30.0, 35.0)
			tr.remove_response(inventory=inv, output=TYPE, pre_filt=pre_filt)
			seismograph["type"] = None

		if seismograph["network"] == "AA":
			seismograph["type"] = AAnetwork.getStationType(seismograph["station"])

			if "H" in seismograph["channel"][1]:
				print "skipping H channel..."
				continue

		save = Save(tr, event_name)
		pre_filter_parameters = dofft(tr)

		# {"x": t, "xf": xf, "y": y, "N": N, "yf": yf}
		time, acc, freq, ampli, N = pre_filter_parameters["x"], pre_filter_parameters["y"], \
									pre_filter_parameters["xf"], pre_filter_parameters["yf"], pre_filter_parameters["N"]
		tr_filter = tr.copy()

		if exist_filters:
			Ftime, Facc, Ffreq, Fampli, FN, filters, tr_filter = FF.reprocess(tr_filter, pre_filter_parameters)

		if not exist_filters:
			Tstart = tr.stats.starttime

			show_graph = graph(tr_filter, dt, name, event_name, distance)
			show_graph.dofft()
			show_graph.init_graph()
			value = show_graph.get_key()

			if value == "n":
				print "unknow trace, move to {0} folder".format(CheckAgainFolder)

				if mode == "MAIN":
					save.save_check_again(time, acc, freq, ampli, N, event_name_o)
				if mode == "CHECK":
					# ToDo : rebuild function, for absolutely trash trace and temp trash trace
					raw_bin = {"event": event_name, "network": seismograph["network"], "station": seismograph["station"],
							"channel": seismograph["channel"], "distance": distance, "magnitude [mw]": details["mw"]}
					trace_bin.tracebin(raw_bin)
				continue

			else:
			# if user press Y or exit
				filters = show_graph.getfilters()
				tr_filter = show_graph.getfiltertrace()

				if show_graph.usefilters():
					Ftime, Facc, Ffreq, Fampli, FN = show_graph.get_Filter_data()

		tr_baseline = baseline.useBaseLine(tr_filter, event_name, name)
		save.trace = tr_baseline

		# save data
		save.save_plot_ori_new(Ftime, Facc, Ffreq, Fampli, FN, time, acc, freq, ampli, dt, N, filters)

		peak_ground = metaData.double_integrate(tr_baseline.data, dt)

		flatfile_data = Save.interpulate(Ffreq, Fampli, dt, FN)
		save.save_traces_in_file()
		# Save.save_meta_data()

		save.save_trace_flatFile(seismograph, details, flatfile_data, filters, distance, peak_ground, epiLocation)
		metaData.movefromtrash(event_name, name)
