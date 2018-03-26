import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl 

G = 9.81 # m/s^2


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

def SaveTracesInFile(trace):
	pass

def SavePlotOriNew(ori_trace, filter_trace, nevent, sta, lowpass=None, highpass=None, timecut=None):
	time, acc, freq, ampli, N = do_fft(ori_trace)
	Ftime, Facc, Ffreq, Fampli, FN = do_fft(filter_trace)

	PGA_raw = max(np.abs(acc))
	PGA_filter = max(np.abs(Facc))
	dt = ori_trace.stats.delta

	# save plot:
	fig, axarr = plt.subplots(2, 2, sharex='col')
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

	if highpass or lowpass:
		axarr[1,1].text(0.95, 0.01, 'highpass = {0} lowpass = {1}'.format(highpass, lowpass),
		verticalalignment='bottom', horizontalalignment='right',
		transform=axarr[1,1].transAxes,
		color='red', fontsize=10)
	if timecut:
		axarr[1,0].text(0.95, 0.01, 'Cut time'.format(timecut),
		verticalalignment='bottom', horizontalalignment='right',
		transform=axarr[1,0].transAxes,
		color='red', fontsize=10)


	# plt.grid()
	plt.savefig("{0}/{1}_raw_filter".format(nevent, sta))
	manager = plt.get_current_fig_manager()
    manager.resize(*manager.window.maxsize())
	plt.close()
	# plt.show()
	return
