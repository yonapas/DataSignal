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
from common import MseedExtractor

TYPE = settings.remove_response_unit
raw_data_folder = settings.raw_data_folder
saved_data_folder = settings.save_data_folder
save_format = settings.save_traces_format
CheckAgainFolder = settings.CheckAgainFolder
CheckAgainFile = settings.CheckAgainFile
mode = settings.mode

check_trace_table = False

extract = MseedExtractor(mode)
files = extract.get_file()

for f in files:
	traces = read(f)
	event_name_o = f.split(".mseed")[0].split("/")[-1]
	print event_name_o
	try:
		inv = read_inventory("{0}/{1}.xml".format(raw_data_folder ,event_name_o))
		b = datetime.datetime.strptime(event_name_o, '%Y-%m-%dT%H:%M:%S')
		d = b.strftime('%Y%m%d%H%M%S')
		event_name = d
		
	except Exception:
		print "no xml file found {0}".format(f)
		continue

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

	for tr in traces[20:]:
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
		distance = metaData.calculate_distance(seismograph, epiLocation)
		seismograph["network"] = tr.meta["network"]
		seismograph["station"] = tr.meta["station"]
		seismograph["channel"] = tr.meta["channel"]
		name = tr.get_id().replace(".", "_")

		if seismograph["network"] == "IS":
			tr.remove_response(inventory=inv, output=TYPE)
			seismograph["type"] = None

		if seismograph["network"] == "AA":
			seismograph["type"] = AAnetwork.getStationType(seismograph["station"])

			if "H" in seismograph["channel"][1]:
				print "skipping H channel..."
				continue

		if seismograph["network"] == "GE":
			continue

		dt = float(tr.meta["delta"])

		if dt == 0.02:
			id_dt.append(tr.get_id())

		else:
			Tstart = tr.stats.starttime

			tr_filter = tr.copy()

			show_graph = graph(tr_filter, dt, name, event_name, distance)
			show_graph.dofft()
			show_graph.init_graph()
			value = show_graph.get_key()
			show_graph.close()

			# init save object
			save = Save(tr, event_name)

			if value == "n":
				print "unknow trace, move to {0} folder".format(CheckAgainFolder)
				time, acc, freq, ampli, N, k = show_graph.get_ori_data()
				save.save_check_again(time, acc, freq, ampli, N, event_name_o)

			else:
				filters = show_graph.getfilters()
				tr_filter = show_graph.getfiltertrace()

				tr_baseline = baseline.useBaseLine(tr_filter, event_name, name)
				save.trace = tr_baseline

				# save data
				print "save trace with filters: ", filters
				# save_traces.SavePlotOriNew(tr, tr_filter, event_name, name, fc, lowpass, highpass, Tstop)
				if show_graph.usefilters():
					Ftime, Facc, Ffreq, Fampli, FN = show_graph.get_Filter_data()
					time, acc, freq, ampli, N, k = show_graph.get_ori_data()
					save.save_plot_ori_new(Ftime, Facc, Ffreq, Fampli, FN, time, acc, freq, ampli, dt, N, filters)

				peak_ground = metaData.double_integrate(tr_baseline.data, dt)
				flatfile_data = Save.interpulate(Ffreq, Fampli, dt, FN)

				save.save_traces_in_file()
				# Save.save_meta_data()

				save.save_trace_flatFile(seismograph, details, flatfile_data, filters, distance, peak_ground, epiLocation)
				metaData.movefromtrash(event_name, name)

			"""
						if value == "n":
				print "unknow trace, move to {0} folder".format(CheckAgainFolder)
				time, acc, freq, ampli, N, k = show_graph.get_ori_data()
				save_traces.svaeCheckAgain(event_name, name, time, acc, freq, ampli, N, event_name_o)

			else:
				filters = show_graph.getfilters()
				tr_filter = show_graph.getfiltertrace()

				# tr_filter. - baseline
				tr_baseline = baseline.useBaseLine(tr_filter, event_name, name)
				print "error with base line", name
				tr_baseline = tr_filter

				# save data
				print "save trace with filters: ", filters
				# save_traces.SavePlotOriNew(tr, tr_filter, event_name, name, fc, lowpass, highpass, Tstop)
				if show_graph.usefilters():
					Ftime, Facc, Ffreq, Fampli, FN = show_graph.get_Filter_data()
					time, acc, freq, ampli, N, k = show_graph.get_ori_data()
					save_traces.SavePlotOriNew(Ftime, Facc, Ffreq, Fampli, FN, time, acc, freq, ampli, dt, N, name, event_name, filters)

				peak_ground = metaData.double_integrate(tr_baseline.data, dt)
				# get dict {"freq":"ampli"}
				flatfile_data = save_traces.interpulate(Ffreq, Fampli, dt, FN)

				save_traces.SaveTracesInFile(tr_baseline, event_name, name, dt)
				save_traces.SaveMetaData(tr_baseline, event_name, name)

				save_traces.saveTraceFlatFile(tr_baseline, event_name, seismograph, details, flatfile_data, filters,
											  distance, peak_ground, epiLocation)
				metaData.movefromtrash(event_name, name)

			"""