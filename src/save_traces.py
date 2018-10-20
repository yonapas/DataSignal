import numpy as np

import matplotlib as mpl
#mpl.use('Qt5Agg')

import matplotlib.pyplot as plt
import settings
import fileinput
import petl as etl
import csv
from datetime import datetime
from numpy import interp
import logging

logger = logging.getLogger(__name__)

saved_data_folder = settings.save_data_folder
dpi = settings.save_fig_dpi
save_format = settings.save_traces_format
checkAgainFolder = settings.CheckAgainFolder
checkAgainFile = settings.CheckAgainFile
catalogfile = settings.flatfile
priod_value = settings.interpulate_value


class Save():

	def __init__(self, trace, ename):
		self.event_name = ename
		self.trace = trace
		self.name = self.trace.get_id().replace(".", "_")
		self.sta = self.name.split("_")[1]
		self.dt = self.trace.stats.delta

	def save_traces_in_file(self):
		self.trace.write("{0}/{1}/{2}_data.txt".format(saved_data_folder, self.event_name, self.name),
						 format=save_format)

		headers = "unit (m/s^2), dt {0}".format(self.dt).split()
		for line in fileinput.input(["{0}/{1}/{2}_data.txt".format(saved_data_folder, self.event_name, self.name)],
									inplace=True):
			if fileinput.isfirstline():
				print(' '.join(headers))
			print(line, end=' ')

	def update_trace(self, new_trace):
		self.trace = new_trace

	def save_check_again(self, time, acc, freq, amp, eno):
		mpl.rcParams.update({'font.size': 6})

		f = open(checkAgainFile, 'a')
		f.write("{0},{1},{2}\n".format(self.event_name, eno, self.name))
		f.close()

		fig, (ax, ax1) = plt.subplots(2, 1)
		fig.suptitle("Time Domain and Freq Domain")

		ax.plot(time, acc)
		ax1.loglog(freq, amp)
		ax.set_xlabel("time [sec]")
		ax.set_ylabel("Acceleration [g]")
		ax.set_title("{0} {1}".format(self.event_name, self.name))
		ax1.set_ylabel("amplitude")

		fig.savefig('{0}/{1}_{2}_fig'.format(checkAgainFolder, self.event_name, self.name), dpi=dpi)
		plt.close()

	def save_meta_data(self):
		metafile = open("{0}/{1}/{2}_meta.txt".format(saved_data_folder, self.event_name, self.name), "w")
		for item in self.trace.meta:
			metafile.write("{0}\n".format(self.trace.meta[item]))
		metafile.close()

	def save_baseline(self, acc, disp, BLacc, BLdisp, time):

		fig, (ax, ax1) = plt.subplots(2, 1, sharex="all")
		fig.suptitle("Trace Before and After Base Line Filter")

		ax.plot(time, acc, "black", time[:-2], BLacc, "red")
		ax1.plot(time, disp, "black", time, BLdisp, "red")
		ax.set_xlabel("time [sec]")
		ax.set_ylabel("Acceleration [g]")
		ax.set_title("Acceleration Difference ")
		ax1.set_title("Displacement Difference")
		ax1.set_ylabel("Displacement [m]")

		fig.savefig("{0}/{1}/{2}_baseline".format(saved_data_folder, self.event_name, self.name), dpi=dpi)
		plt.close()

	def save_plot_ori_new(self, Ftime, Facc, Ffreq, Fampli, time, acc, freq, ampli, dt, filters):

		mpl.rcParams.update({'font.size': 6})
		PGA_raw = max(np.abs(acc))
		PGA_filter = max(np.abs(Facc))
		# save plot:
		fig, axarr = plt.subplots(2, 2)
		fig.suptitle('{0} {1} ,dt:{2}'.format(self.name, self.event_name, dt), fontsize=14, fontweight='bold')

		axarr[0, 0]._label = "Time"
		axarr[0, 1]._label = "Frequncy"
		axarr[1, 0]._label = "FilterTime"
		axarr[1, 1]._label = "FilterFrequncy"

		axarr[0, 0].set_xlabel("time [sec]\n PGA {0} g".format(PGA_raw))
		axarr[0, 0].set_ylabel("ACC [g]")
		axarr[0, 0].plot(time, acc, "k")

		axarr[0, 1].loglog(freq, ampli, "k")

		axarr[1, 0].plot(Ftime, Facc)
		axarr[1, 0].set_xlabel("time [sec]\n PGA {0} g".format(PGA_filter))
		axarr[1, 0].set_ylabel("ACC [g]")

		axarr[1, 1].loglog(Ffreq, Fampli)

		if filters["highpass"] or filters["lowpass"]:
			axarr[1, 1].text(0.95, 0.01, 'highpass = {0} lowpass = {1}'.format(filters["highpass"], filters["lowpass"]),
							 verticalalignment='bottom', horizontalalignment='right',
							 transform=axarr[1, 1].transAxes,
							 color='red', fontsize=7)
		if filters["tstop"]:
			axarr[1, 0].text(0.95, 0.01, 'Cut time'.format(filters["tstop"]),
							 verticalalignment='bottom', horizontalalignment='left',
							 transform=axarr[1, 0].transAxes,
							 color='red', fontsize=7)

		try:
			axarr[1, 1].axvline(x=filters["highpass"], color='red')
			axarr[1, 1].axvline(x=filters["lowpass"], color='red')
		except TypeError:
			pass

		plt.savefig("{0}/{1}/{2}_raw_filter".format(saved_data_folder, self.event_name, self.name), dpi=dpi)
		plt.close()
		return

	def save_trace_flatFile(self, station_detils, magnituda, motion, filters, distance, peak, hypo):
		headersfile = open(settings.headres, "r").readlines()
		headers = headersfile[0].split(",")
		valuesdict = {}
		for head in headers:
			valuesdict[head] = None

		date = datetime.strptime(self.event_name, '%Y%m%d%H%M%S')
		valuesdict["YEAR"] = str(date.year)
		valuesdict["MODY"] = "{0}{1}".format(date.strftime('%m'), date.strftime('%d'))
		valuesdict["HRMN"] = "{0}{1}".format(date.strftime('%H'), date.strftime('%M'))
		valuesdict["Earthquake Magnitude"] = magnituda["mw"]
		valuesdict["EpiD      (km)"] = distance
		valuesdict["Station Latitude"] = station_detils["latitude"]
		valuesdict["Station Longitude"] = station_detils["longitude"]
		valuesdict["PGA (g)"] = peak["PGA"]
		valuesdict["PGV (cm/sec)"] = peak["PGV"]
		valuesdict["PGD (cm)"] = peak["PGD"]
		valuesdict["HP (Hz)"] = filters["highpass"]
		valuesdict["LP (Hz)"] = filters["lowpass"]
		valuesdict["Hypocenter Longitude (deg)"] = hypo["long"]
		valuesdict["Hypocenter Latitude (deg)"] = hypo["lat"]
		valuesdict["Station Network"] = station_detils["network"]
		valuesdict["Station Type"] = station_detils["type"]
		valuesdict["Station Name"] = self.sta
		valuesdict["Record Sequence Number"] = self.get_n_row() + 1
		valuesdict["Component"] = station_detils["channel"]
		valuesdict["Depth"] = station_detils["local_depth"]

		exist_row = self.existtrace(valuesdict)
		if exist_row:
			f = open(catalogfile, 'r').readlines()
			fn = open(catalogfile, "w")
			for line in f:
				seqnum = line.split(",")[0]
				if seqnum != exist_row[0]:
					fn.write(line)
			fn.close()
			valuesdict["Record Sequence Number"] = exist_row[0]

		for item in motion:
			if item == 0.01:
				valuesdict["f 0.01 Hz"] = motion[item]
			elif str(item) in valuesdict.keys():
				valuesdict[str(item)] = motion[item]
			elif str(item) + "0" in valuesdict.keys():
				valuesdict[str(item) + "0"] = motion[item]
			elif str(item) + "00" in valuesdict.keys():
				valuesdict[str(item) + "00"] = motion[item]
			else:
				logging.error(item)
		# ToDo:
		# save traces in MongoDb

		output = csv.DictWriter(open(catalogfile, 'a'), delimiter=',', lineterminator='\n', fieldnames=headers)
		output.writerow(valuesdict)

	@staticmethod
	def existtrace(dict):
		existtabel = etl.fromcsv(catalogfile)
		if etl.nrows(existtabel) < 1:
			return False
		lkp = etl.lookup(existtabel, ("Station Name", "YEAR", "MODY", "HRMN"), "Record Sequence Number")
		try:
			exist = lkp[(dict["Station Name"], dict["YEAR"], dict["MODY"], dict["HRMN"])]
		except:
			return False
		if len(exist) > 1:
			logger.warning("more then one row duplicate {}".format(dict))
		if exist:
			return exist

	@staticmethod
	def get_n_row():
		existtabel = etl.fromcsv(catalogfile)
		n = etl.nrows(existtabel)
		return n

	@staticmethod
	def interpulate(x, y, dt):
		"""

		:param x: Amplitude after filter
		:param y: Freq after filter
		:param dt: Delta time

		:return: Dictionry of interpulated value to FAS
		"""

		# Y = np.abs(y[0:(N // 2)+1]) # normalize freq
		priod_value = settings.interpulate_value  # values to interpulate
		if dt == 0.025:
			priod_value = sorted(i for i in priod_value if i <= 20.0)  # if dt = 0.025 s --> interpulate max 20 Hz

		new_value = interp(priod_value, x, y)  # numpy interpulation
		ground_motion = zip(priod_value, new_value)  # match x to y ((x1,y1), (x2,y2)....)
		ground_motion = sorted(ground_motion, key=lambda point: point[0])  # sorted x-y
		return dict(ground_motion)
