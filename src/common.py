from glob import glob
import petl as etl
import settings
import csv
import numpy as np
from pymongo import MongoClient

raw_data_folder = settings.raw_data_folder
CheckAgainFile = settings.CheckAgainFile
prefix = settings.prefix_mseed
files = []


class MseedExtractor():

	def __init__(self):
		self.mode = None

	def get_file(self):

		files = glob("{0}/{1}.mseed".format(raw_data_folder, prefix))
		return files


class CheckAgain():
	def __init__(self):
		self.binfile= settings.TraceBinFie
		self.header = open(self.binfile, "r").readlines()[0].split(",")

	def tracebin(self, tracedict):
		f = csv.DictWriter(open(self.binfile, 'a'), delimiter=',', lineterminator='\n', fieldnames=self.header)
		f.writerow(tracedict)
		pass


class CorrectTrace():
	def __init__(self, flatfile):
		self.table = etl.fromcsv(flatfile)
		self.eventtable = None
		self.lookup_filters = None
		self.oriparm = None

	def load_event_data(self, year, mo_day, hour):
		self.eventtable = etl.select(self.table, lambda rec: rec.YEAR == year and rec.MODY == mo_day and rec.HRMN == hour)
		self.lookup_filters = etl.lookup(self.eventtable, "Station Name", ("HP (Hz)", "LP (Hz)"))

	def filters_exist(self, sta):
		try:
			self.filters = self.lookup_filters[sta][0]
			return True
		except:
			return False

	def reprocess(self, trace, original):

		self.oriparm = original

		highpass = float(min(self.filters))
		lowpass = float(max(self.filters))
		trace.filter("highpass", freq=highpass, corners=2, zerophase=True)
		trace.filter("lowpass", freq=lowpass, corners=2, zerophase=True)

		Fparam = dofft(trace)
		Ftime, Facc, Ffreq, Fampli, FN = Fparam["x"], Fparam["y"], Fparam["xf"], Fparam["yf"], Fparam["N"]
		filters = {"highpass": highpass, "lowpass": lowpass, "tstop": None}
		trace.data = trace.data / G

		return Ftime, Facc, Ffreq, Fampli, FN, filters, trace


class ConnectToMongo():
	def __init__(self, host, port, db, ff, ca):
		client = MongoClient(host, port)
		self._db = client[db]
		self.flatfile = self._db[ff]
		self.checkagain = self._db[ca]

	def exists_trace_mongo_ff(self, dict):
		ff_exists = self.flatfile.find(dict)
		try:
			ff_exists.next()
			# this trace is exists
			return True
		except StopIteration:
			# this trace is not exists
			return False

	def exists_trace_mongo_ca(self, dict):
		ca_exists = self.checkagain.find(dict)
		try:
			ca_exists.next()
			# this trace is exists
			return True
		except StopIteration:
			# this trace is not exists
			return False

	def insert_ff(self, dict):
		self.flatfile.insert_one(dict)

	def insert_checkagain(self, dict):
		self.checkagain(dict)

	def count_row(self):
		return self.flatfile.count()


def dofft(trace):
	Ts = trace.stats.delta  # sampling interval

	y = trace.data
	N = len(y)
	t = np.arange(0, N * Ts, Ts)  # time vector
	xf = np.fft.rfftfreq(N, Ts)

	yf = np.abs(np.fft.rfft(y))
	if (len(t) - len(y) == 1):
		t = t[:-1]

	return {"x": t, "xf": xf, "y": y, "N": N, "yf": yf}
