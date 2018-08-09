import settings
import petl as etl


def loadStationsFile():
	catalog_file = settings.station_catalog
	catalog = etl.fromtext(catalog_file)
	return catalog


def StationExist(catalog, sta):
	net = sta["network"]
	st = sta["station"]
	channel = sta["channel"]


	pass


def addStation(station):
	pass
