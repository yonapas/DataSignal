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
import logging

# logging.basicConfig(filename='DataSignal.log', format='%(asctime)s %(message)s')
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('DataSignal')
logger.setLevel(logging.INFO)

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
# FF = CorrectTrace(flatfile)


def find_file_pattern(event_name):
	date_pattern = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H_%M_%S']
	for pattern in date_pattern:
		try:
			return datetime.datetime.strptime(event_name, pattern)
		except Exception as e:
			logger.debug("Name pattern is not {}".format(pattern))

		logger.error("Date is not in expected format: {}".format(event_name))


def main():

	for f in files:
		traces = read(f)
		event_name_o = f.split(".mseed")[0].split("/")[-1]
		logger.info(event_name_o)
		try:
			inv = read_inventory("{0}/{1}.xml".format(raw_data_folder, event_name_o))
			event_name_object = find_file_pattern(event_name_o)
			event_name = event_name_object.strftime("%Y%m%d%H%M%S")
		except Exception as e:
			logger.debug("no xml file found {0}".format(f))
			continue

		# find magnitude for the event
		YEAR = str(event_name_object.year)
		MODY = "{0}{1}".format(event_name_object.strftime('%m'), event_name_object.strftime('%d'))
		HRMN = "{0}{1}".format(event_name_object.strftime('%H'), event_name_object.second)
		# FF.load_event_data(YEAR, MODY, HRMN)

		# find magnitude for the event
		details = metaData.find_eq_details(event_name_object)

		epiLocation = details["epi_center"]

		try:
			# try to create new folder for saved traces
			mkdir("{0}/{1}".format(saved_data_folder, event_name))
		except OSError:
			logger.info("directory {} already exists".format(event_name))

		# merge traces by ID
		traces.merge(1, fill_value='interpolate')
		logger.info("{} Traces in Streem".format(len(traces)))

		for tr in traces:
			name = tr.get_id().replace(".", "_")
			logger.info("trace name: {}".format(name))

			if check_trace_table:
				table = etl.select(check_trace_table, lambda rec: rec.sta == name and rec.mseedname == event_name_o)
				if etl.nrows(table) > 0:
					pass
				else:
					continue

			# tr.data = tr.data[:-1]
			try:
				seismograph = inv.get_channel_metadata(tr.get_id())
			except Exception as e:
				logger.debug("no inv data for trace {}".format(name))
				continue

			distance = metaData.calculate_distance(seismograph, epiLocation)
			seismograph["network"] = tr.meta["network"]
			seismograph["station"] = tr.meta["station"]
			seismograph["channel"] = tr.meta["channel"]

			# exist_filters = FF.filters_exist(name)
			exist_filters = False
			logger.info("trace dose'nt exists in FlatFile {}, {}".format(exist_filters, name))

			dt = float(tr.meta["delta"])

			if seismograph["network"] == "GE" or dt == 0.02:
				# ToDo : Ge process, acc unit
				logger.info("GE network {}".format(name))
				continue

			if seismograph["network"] == "IS":
				try:
					pre_filt = (0.005, 0.006, 30.0, 35.0)
					#tr.remove_response(inventory=inv, output=TYPE, pre_filt=pre_filt)
					tr.remove_response(inventory=inv, output=TYPE)
					seismograph["type"] = None
				except ValueError:
					logger.warning("cannot use remove response {}".format(tr.get_id()))
					continue

			if seismograph["network"] == "AA":
				seismograph["type"] = AAnetwork.getStationType(seismograph["station"])

				if "H" in seismograph["channel"][1]:
					logger.info("skipping H channel... {}".format(tr.get_id()))
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

				show_graph = graph(tr_filter, dt, name, event_name, distance)
				show_graph.dofft()
				show_graph.init_graph()
				value = show_graph.get_key()

				if value == "n":
					logger.info("moving trace to {0} folder, {1}".format(CheckAgainFolder, name))

					if mode == "MAIN":
						save.save_check_again(time, acc, freq, ampli, event_name_o)
					if mode == "CHECK":
						# ToDo : rebuild function, for absolutely trash trace and temp trash trace
						raw_bin = {"event": event_name, "network": seismograph["network"],
								"station": seismograph["station"],
								"channel": seismograph["channel"], "distance": distance, "magnitude [mw]": details["mw"]}
						trace_bin.tracebin(raw_bin)
					continue

				else:
					# if user press Y or exit
					filters = show_graph.getfilters()
					tr_filter = show_graph.getfiltertrace()
					logger.info("save trace with filters : {}".format(filters))

					# if show_graph.usefilters():
					Ftime, Facc, Ffreq, Fampli, FN = show_graph.get_Filter_data()

			tr_baseline = baseline.useBaseLine(tr_filter)
			save.update_trace(tr_baseline)

			# save data
			save.save_plot_ori_new(Ftime, Facc, Ffreq, Fampli, time, acc, freq, ampli, dt, filters)

			peak_ground = metaData.double_integrate(tr_baseline.data, dt)

			flatfile_data = Save.interpulate(Ffreq, Fampli, dt)
			save.save_traces_in_file()
			# Save.save_meta_data()

			save.save_trace_flatFile(seismograph, details, flatfile_data, filters, distance, peak_ground, epiLocation)
			# ToDo convert this function to mongodb search
			# metaData.movefromtrash(event_name, name)


if __name__ == "__main__":
	logger.info("starting....")
	main()
