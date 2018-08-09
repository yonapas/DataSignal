from scipy.fftpack import fft
import numpy as np
from obspy import read, read_inventory
from obspy.geodetics import gps2dist_azimuth
from glob import glob 
from datetime import datetime 

global epi_mag
epi_mag = open("../catalog/EQData.txt", "r").readlines()


def getEpiCenterMagnitude(date):
	t = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
	for line in epi_mag:
		line = line.split("\t")
		if line[-6] == str(t.year):
			if line[-5] == str(t.month):
				if line[-4] == str(t.day):
					if line[-3] == str(t.hour):
						epice = (line[1], line[2])
						depth = line[3]
						ID = line[0]
						mag = line[5]
						return epice, mag, depth, ID
	
	print "no earthQ found in txt file\n"
	return None
	

xml_file = glob("*.xml")


for file in xml_file:
	traces_file = glob("{0}.mseed".format(file.split(".")[0]))

	if not traces_file:
		print "no mseed found to xml {0} \n".format(file)
		continue 

	if traces_file:
		traces = read(traces_file[0])
		date = traces[0].times("utcdatetime")[0]
		date = str(date).split(".")[0]
		acc = {}

		for tr in traces:
			try:
				channels = tr.meta["channel"]
				network = tr.meta["network"]
				station = tr.meta["station"]

				name = "{0}.{1}..{2}".format(network, station, channels)
				acc_max = max(tr.remove_response(inventory=file, output="ACC").data)
				acc[name] = str(acc_max)
			except:
				print name , file

		try:
			epi, mag, depth, ID= getEpiCenterMagnitude(date)

			lat_epi = epi[0]
			long_epi = epi[1]
			outfile = open("data_from_stations{0}.csv".format(file), "w")
			outfile.write("dateEQ: {0},\nmagnitude: {1},\nEpicenter Lat: {2},\nEpicenter Long: {3},\nDepth: {4}\n"
				.format(date, mag, lat_epi, long_epi , depth))

			station_data = read_inventory(file)
			data =  station_data.get_contents() 
			station_list = data['channels']

			for sta in station_list:
				### find distance in km
				d = station_data.get_channel_metadata(sta)
				lng = d['longitude']
				lat = d['latitude']

				if float(lat) < 90:
					epi_dist, az, baz = gps2dist_azimuth(float(lat_epi), float(long_epi), 
														float(lat), float(lng))
				else: 
					continue

				dista =  epi_dist/1000 # meters

				staSplit = sta.split(".")
				_net = staSplit[0]
				_sta = staSplit[1]
				_channel = staSplit[-1]
				acc_sta = 0

				if str(sta) in acc:
					acc_sta = acc[str(sta)]
				

				outfile.write("{0}, {1}, {2}, {3}, {4}, {5}, {6}\n"
						.format(_net, _sta, _channel ,lat, lng, dista, acc_sta))
			outfile.close()
		except:
			print "error"
			print file

 
