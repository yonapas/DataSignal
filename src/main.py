from obspy import read, read_inventory
import datetime
from os import mkdir
from save_traces import Save
import metaData
import settings
import baseline
from GraphIt import graph
import AAnetwork
from common import MseedExtractor, CheckAgain, CorrectTrace, dofft, ConnectToMongo
import logging

logging.basicConfig(filename='../logs/DataSignal_{}.log'.format(datetime.datetime.now()), format='%(asctime)s %(message)s')
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('DataSignal')
logger.setLevel(logging.INFO)

TYPE = settings.remove_response_unit
raw_data_folder = settings.raw_data_folder
saved_data_folder = settings.save_data_folder
save_format = settings.save_traces_format
CheckAgainFolder = settings.CheckAgainFolder
CheckAgainFile = settings.CheckAgainFile
flatefile_table_name = settings.flatefile_table_name
chackagain_table_name = settings.chackagain_table_name
mongo_host = settings.host
mongo_port = settings.port
db_name = settings.db_name

# define km per magnitude
magnitude5_dis = settings.mag5updistance
magnitude5dis = settings.mag5distance
magnitude4dis = settings.mag4distance


extract = MseedExtractor()
trace_bin = CheckAgain()
files = extract.get_file()
mongo = ConnectToMongo(mongo_host, mongo_port, db_name, flatefile_table_name, chackagain_table_name)


def find_file_pattern(event_name):
	date_pattern = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H_%M_%S', '%Y-%m-%d %H:%M:%S.%f' ]
	for pattern in date_pattern:
		try:
			return datetime.datetime.strptime(event_name, pattern)
		except Exception as e:
			logger.debug("Name pattern is not {}".format(pattern))

	logger.error("Date is not in expected format: {}".format(event_name))


def distance_too_far(magnitude, distance):
	if magnitude <= 3.9 and distance > magnitude4dis:
		return True
	elif magnitude <= 5.0 and distance > magnitude5dis:
		return True
	elif magnitude > 5.0 and distance > magnitude5_dis:
		return True
	return False


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
		HRMN = "{0}{1}".format(event_name_object.strftime('%H'), event_name_object.minute)
		# FF.load_event_data(YEAR, MODY, HRMN)

		# find magnitude for the event
		#details = metaData.find_eq_details_2018(event_name_object)
		details = metaData.find_eq_details(event_name_object)
		print(details)

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


			try:
				seismograph = inv.get_channel_metadata(tr.get_id())

			except Exception as e:
				logger.debug("no inv data for trace {}".format(name))
				continue
			"""
			ARAD station only
			seismograph = {}
			seismograph["latitude"] = 31.2567
			seismograph["longitude"] = 35.2103
			seismograph["local_depth"] = 0
			"""

			distance = metaData.calculate_distance(seismograph, epiLocation)
			seismograph["network"] = tr.meta["network"]
			seismograph["station"] = tr.meta["station"]
			seismograph["channel"] = tr.meta["channel"]


			already_exsist_ff = mongo.exists_trace_mongo_ff({"YEAR": int(YEAR), "MODY": int(MODY), "HRMN": int(HRMN), "Station Name": seismograph["station"],
										"Component": seismograph["channel"],"Station Network": seismograph["network"]})
			already_exist_ca = mongo.exists_trace_mongo_ca({"YEAR": YEAR, "MODY": MODY, "HRMN": HRMN, "sta": seismograph["station"],
										"components": seismograph["channel"], "network": seismograph["network"]})

			if already_exist_ca or already_exsist_ff:
				logger.info("trace already exists in flatfile or trash")
				continue

			# exist_filters = FF.filters_exist(name)
			exist_filters = False
			logger.info("trace dose'nt exists in FlatFile {}, {}".format(exist_filters, name))

			dt = float(tr.meta["delta"])

			#if seismograph["network"] == "GE" or dt == 0.02:
			if seismograph["network"] == "GE" :
				# ToDo : Ge process, acc unit
				logger.info("not valid trace {} dt:{}".format(name, dt))
				continue

			if distance_too_far(details["mw"], distance):
				logger.info("station too far ({} km)".format(distance))
				continue

			if seismograph["network"] == "IS":
				try:
					pre_filt = (0.005, 0.006, 30.0, 35.0)
					# tr.remove_response(inventory=inv, output=TYPE, pre_filt=pre_filt)
					tr.remove_response(inventory=inv, output=TYPE) # m/s2
					seismograph["type"] = None
				except (ValueError, AttributeError) as e:
					logger.warning("cannot use remove response {}".format(tr.get_id()))
					continue

			if seismograph["network"] == "AA":
				seismograph["type"] = AAnetwork.getStationType(seismograph["station"])

				if "H" in seismograph["channel"][1]:
					logger.info("skipping H channel... {}".format(tr.get_id()))
					continue

			save = Save(tr, event_name, mongo)
			pre_filter_parameters = dofft(tr) # m/ s2

			# {"x": t, "xf": xf, "y": y, "N": N, "yf": yf}
			time, acc, freq, ampli, N = pre_filter_parameters["x"], pre_filter_parameters["y"], \
										pre_filter_parameters["xf"], pre_filter_parameters["yf"], pre_filter_parameters["N"]
			tr_filter = tr.copy() # m/ S2

			if not exist_filters:

				show_graph = graph(tr_filter, dt, name, event_name, distance)
				show_graph.dofft()
				show_graph.init_graph()
				value = show_graph.get_key()

				if value == "n":
					logger.info("moving trace to {0} folder, {1}".format(CheckAgainFolder, name))
					save.save_check_again(time, acc, freq, ampli, event_name_o)

				else:
					# if user press Y or exit
					filters = show_graph.getfilters()
					tr_filter = show_graph.getfiltertrace() # G unit
					logger.info("save trace with filters : {}".format(filters))

					# if show_graph.usefilters():
					Ftime, Facc, Ffreq, Fampli, FN = show_graph.get_Filter_data()

			tr_baseline = baseline.useBaseLine(tr_filter)  # G unit
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
