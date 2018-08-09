# Using python and obspy, it should be very easy to download data and metadata.
# here is an example for the Nueba event of Nov. 22, 1995:
# lines starting with `#` are comments. Should be run in a python terminal or code.

######################## copy from here ############################
# import needed modules
from obspy import UTCDateTime
from obspy.clients.fdsn import Client as fdsnclient
import settings

raw_data_folder = settings.raw_data_folder
geoIP = 'http://82.102.143.46:8181'
HIGH_MAGNITUDE = 4.5


def getMseedFromWeb(magnituda, date):
	# connect to server at GII
	flink = fdsnclient(geoIP)
	# fedine origin time `ot`
	# ot = UTCDateTime(year, month, day, hour, minu, sec, microsec)
	ot = UTCDateTime(date)
	# print ot

	# if high magnitude, download AA net too.
	if magnituda >= HIGH_MAGNITUDE:
		get_networks = 'AA, IS'

	if magnituda < HIGH_MAGNITUDE:
		get_networks = 'IS'

	filename = date
	# get all data available 10 s before and 600 s after origin time.
	r = flink.get_waveforms("*", '*', '*', '???', ot-10, ot+550, attach_response=True)
	# save data to file with YmdHMS.mseed format (year,month,day,hours,minutes,seconds).
	# Can save to SAC if needed (replace mseed to sac).
	r.write('{0}/{1}.mseed'.format(raw_data_folder,filename), 'MSEED')
	# get inventory from server
	inventory = flink.get_stations(ot-1, ot+550, network=get_networks, station='*', location='*', channel='???', level='response')
	# save inventory to an xml file. format may be STATIONXML, SACPZ for SAC poles and zeros format
	inventory.write('{0}/{1}.xml'.format(raw_data_folder,filename), format='STATIONXML')
	print "download file", filename
	######################## copy ends here ############################

# getMseedFromWeb(5.1, '1993-03-08T16:33:22')
