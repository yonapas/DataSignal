import numpy as np 
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from obspy import read, read_inventory
from glob import glob
import save_traces


def func(x, a1, a2, a3, a4, a5, a6):
	func = a1*x**2+a2*x**3+a3*x**4+a4*x**5+a5*x**6
	return func

def useBaseLine(trace, inv, nevent, sta):
	"""
	the funcation get filterd trace (after proccesing)
	and do "baseline tapaer". for data in disp domain

	return:
	trace in acceleration domain.
	"""
	trace.remove_response(inventory=inv, output="DISP")
	trace_baseline = trace.copy()
	Ts = trace.stats.delta
	ydata = trace_baseline.data
	xdata = np.arange(0, len(ydata)*Ts, Ts)
	if (len(xdata)-len(ydata) == 1):
		xdata = xdata[:-1]

	popt, pcov = curve_fit(func, xdata, ydata)
	x = xdata
	ybaseline = func(x, *popt)
	
	trace_baseline.data = ydata - ybaseline

	# save fig for trace before baseline func and after
	save_traces.SaveBaseline(trace, trace_baseline, nevent, sta)

	trace.remove_response(inventory=inv, output="ACC")	
	return trace
