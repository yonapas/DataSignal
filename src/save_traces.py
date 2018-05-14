import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl 
import settings
import fileinput
import petl as etl
import csv
from numba import jit
from datetime import datetime
# from scipy.interpolate import interp1d
from numpy import interp

G = 9.81 # m/s^2

saved_data_folder = settings.save_data_folder
dpi = settings.save_fig_dpi
save_format = settings.save_traces_format
checkAgainFolder = settings.CheckAgainFolder
catalogfile = settings.flatfile
priod_value = settings.interpulate_value

@jit
def do_fft(trace, dt=None):
	Ts = trace.stats.delta # sampling interval
	Fs = 1/Ts # sampling rate
	
	y = trace.data/G
	# y = trace.data
	n = len(y)
	t = np.arange(0, n*Ts, Ts) # time vector
	k = np.arange(n)
	T = n/Fs
	
	freq = k/T
	freq = freq[range(n/2)]

	yf = np.fft.fft(y)*2/n
	# yf = fft(y)
	yf = yf[range(n/2)]
	# xf = np.linspace(0.0, 1/(dt), N//2)

	if (len(t)-len(y) == 1):
		t = t[:-1]
	x = t
	xf = freq
	return x, y, xf, yf, n
	

def SaveTracesInFile(trace, event_name, name, dt):

	trace.write("{0}/{1}/{2}_data.txt".format(saved_data_folder, event_name, name), format=save_format)

	headers = "unit (g), dt {0}".format(dt).split()
	for line in fileinput.input(["{0}/{1}/{2}_data.txt".format(saved_data_folder, event_name, name)], inplace=True):
		if fileinput.isfirstline():
			print ' '.join(headers)
		print line,


def svaeCheckAgain(trace, nevent, sta, time, acc, freq, amp, N):
	mpl.rcParams.update({'font.size': 6})
	trace.write('{0}/{1}_{2}_data.mseed'.format(checkAgainFolder, nevent, sta), format="MSEED")
	fig, (ax, ax1) = plt.subplots(2, 1)
	fig.suptitle("Time Domain and Freq Domain")

	ax.plot(time, acc)
	ax1.loglog(freq, 2.0/N * np.abs(amp[0:N//2]))
	ax.set_xlabel("time [sec]")
	ax.set_ylabel("Acceleration [g]")
	ax.set_title("{0} {1}".format(nevent, sta))
	ax1.set_ylabel("amplitude")

	fig.savefig('{0}/{1}_{2}_fig'.format(checkAgainFolder, nevent, sta), dpi=dpi)
	plt.close()


def SaveMetaData(trace, event_name, name, ):
	metafile = open("{0}/{1}/{2}_meta.txt".format(saved_data_folder, event_name, name), "w")

	for item in trace.meta:
		metafile.write("{0}\n".format(trace.meta[item]))

	metafile.close()


def SaveBaseline(acc, disp, BLacc, BLdisp, time, nevent, sta):
	fig, (ax, ax1) = plt.subplots(2, 1, sharex=True)
	fig.suptitle("Trace Before and After Base Line Filter")

	ax.plot(time, acc, "black", time[:-2], BLacc,"red")
	ax1.plot(time, disp, "black", time, BLdisp, "red")
	ax.set_xlabel("time [sec]")
	ax.set_ylabel("Acceleration [g]")
	ax.set_title("Acceleration Difference ")
	ax1.set_title("Displacement Difference")
	ax1.set_ylabel("Displacement [m]")

	fig.savefig("{0}/{1}/{2}_baseline".format(saved_data_folder, nevent, sta), dpi=dpi)
	plt.close()
	

def SavePlotOriNew(Ftime, Facc, Ffreq, Fampli, FN, time, acc, freq, ampli, dt, N, sta, nevent, filters):

	mpl.rcParams.update({'font.size': 6})
	PGA_raw = max(np.abs(acc))
	PGA_filter = max(np.abs(Facc))
	# dt = ori_trace.stats.delta

	# save plot:
	fig, axarr = plt.subplots(2, 2)
	fig.suptitle('{0} {1} ,dt:{2}'.format(sta, nevent, dt), fontsize=14, fontweight='bold')


	axarr[0,0]._label = "Time"
	axarr[0,1]._label = "Frequncy"
	axarr[1,0]._label = "FilterTime"
	axarr[1,1]._label ="FilterFrequncy"

	axarr[0,0].set_xlabel("time [sec]\n PGA {0} g".format(PGA_raw))
	axarr[0,0].set_ylabel("ACC [g]")
	axarr[0,0].plot(time, acc, "k")

	axarr[0,1].loglog(freq, 2.0/N * np.abs(ampli[0:N//2]), "k")

	axarr[1,0].plot(Ftime, Facc)
	axarr[1,0].set_xlabel("time [sec]\n PGA {0} g".format(PGA_filter))
	axarr[1,0].set_ylabel("ACC [g]")

	axarr[1,1].loglog(Ffreq, 2.0/FN * np.abs(Fampli[0:FN//2]))

	if filters["highpass"] or filters["lowpass"]:
		axarr[1,1].text(0.95, 0.01, 'highpass = {0} lowpass = {1}'.format(filters["highpass"], filters["lowpass"]),
		verticalalignment='bottom', horizontalalignment='right',
		transform=axarr[1,1].transAxes,
		color='red', fontsize=7)
	if filters["tstop"]:
		axarr[1,0].text(0.95, 0.01, 'Cut time'.format(filters["tstop"]),
		verticalalignment='bottom', horizontalalignment='left',
		transform=axarr[1,0].transAxes,
		color='red', fontsize=7)

	axarr[1, 1].axvline(x=filters["highpass"], color='red')
	axarr[1, 1].axvline(x=filters["lowpass"], color='red')
		
	# plt.grid()

	plt.savefig("{0}/{1}/{2}_raw_filter".format(saved_data_folder, nevent, sta), dpi=dpi)

	plt.close()
	# plt.show()
	return


def interpulate(x, y, dt, N):
	Y = 2.0/N * np.abs(y[0:N//2])
	priod_value = settings.interpulate_value
	all_freq = sorted(list(x) + list(priod_value))
	if dt == 0.025:
		all_freq = sorted(i for i in all_freq if i <= 20.0)
		priod_value = sorted(i for i in priod_value if i <= 20.0)

	new_value = interp(priod_value, x, Y)
	ground_motion = zip(priod_value, new_value)
	ground_motion = sorted(ground_motion, key=lambda point: point[0])

	return dict(ground_motion)


def saveTraceFlatFile(trace, nevent, station_detils, magnituda, motion, filters, distance, peak, hypo):
	# existtabel = etl.fromcsv(catalogfile)
	headersfile = open(settings.headres, "r").readlines()
	headers = headersfile[0].split(",")
	valuesdict = {}
	for head in headers:
		valuesdict[head] = None

	date = datetime.strptime(nevent, '%Y%m%d%H%M%S')
	valuesdict["YEAR"] = date.year
	valuesdict["MODY"] = "{0}{1}".format(date.strftime('%m'), date.strftime('%d'))
	valuesdict["HRMN"] = "{0}{1}".format(date.strftime('%H'), date.strftime('%S'))
	valuesdict["Station Name"] = None
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
	valuesdict["Station Name"] = trace.get_id()

	for item in motion:
		if item == 0.01:
			valuesdict["f 0.01 Hz"] = motion[item]
		if item in valuesdict or str(item)+"0" in valuesdict:
			valuesdict[str(item)+"0"] = motion[item]

	print valuesdict

	with open(catalogfile, 'r+b') as f:
		header = next(csv.reader(f))
		print headers
		dict_writer = csv.DictWriter(f, header, -999)
		dict_writer.writerow(valuesdict)


