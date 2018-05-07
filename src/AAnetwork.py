import petl as etl
import settings

station_file = settings.aa_station_file

station_list = etl.fromcsv(station_file)
station_list = etl.convert(station_list, 'type', 'lower')


def getStationType(name):

	if name in list(etl.values(station_list, "code")):
		lkp = etl.lookupone(station_list, "code", "type")
		return lkp[name]
	else:
		lkp = etl.lookupone(station_list, "oldCode", "code")
		newCode = lkp[name]
		lkp = etl.lookupone(station_list, "code", "type")
		return lkp[newCode]


def getDefaultFilter(name):
	if getStationType(name) == "etna":
		return 0.1
	else:
		return None

# print getStationType("ARD")
