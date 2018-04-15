from obspy import read, read_inventory, Stream
from glob import glob
outdepth = open("depthstation.txt", "w")

files = glob("*.mseed")

for f in files:
	traces = read(f)
	event_name = f.split(".mseed")[0]
	print event_name
	inv = read_inventory("{0}.xml".format(event_name))
	for net in inv:
		nt = net.code
		for sta in net:
			# print dir(sta)

			station =  sta.site.name 
			for cha in sta:
				print  net.code, sta.site.name, cha.code, cha.sensor.type
				chaN = cha.code
				chaD = cha.depth
				#outdepth.write("{0},{1},{2},{3}\n".format(nt, station, chaN, chaD))

outdepth.close()
print "done"
