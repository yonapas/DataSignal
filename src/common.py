from glob import glob
import petl as etl
import settings

raw_data_folder = settings.raw_data_folder
CheckAgainFile = settings.CheckAgainFolder
files =[]


class MseedExtractor():

	def __init__(self, mode):
		self.mode = mode

	def get_file(self):
		if self.mode == "MAIN":
			files = glob("{0}/*914.mseed".format(raw_data_folder))

		if self.mode == "CHECK":
			check_trace_table = etl.fromcsv(CheckAgainFile)
			events = set(etl.values(check_trace_table, "mseedname"))
			files = []
			for e in events:
				files.append(glob("{0}/{1}.mseed".format(raw_data_folder, e))[0])

		return files