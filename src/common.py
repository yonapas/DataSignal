from glob import glob
import petl as etl
import settings
import csv
import numpy as np

raw_data_folder = settings.raw_data_folder
CheckAgainFile = settings.CheckAgainFile
files = []

G = 9.81


class MseedExtractor():

	def __init__(self, mode):
		self.mode = mode

	def get_file(self):
		if self.mode == "MAIN":
			files = glob("{0}/2008-10-19*.mseed".format(raw_data_folder))

		if self.mode == "CHECK":
			check_trace_table = etl.fromcsv(CheckAgainFile)
			print check_trace_table
			events = set(etl.values(check_trace_table, "mseedname"))
			files = []
			for e in events:
				files.append(glob("{0}/{1}.mseed".format(raw_data_folder, e))[0])

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
