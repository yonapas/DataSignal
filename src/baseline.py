import numpy as np 
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from obspy import read, read_inventory
from glob import glob


def func(x, a1, a2, a3, a4, a5, a6):
	func = a1*x**2+a2*x**3+a3*x**4+a4*x**5+a5*x**6
	return func

def useBaseLine(trace, inv):
	"""
	the funcation get filterd trace (after proccesing)
	and do "baseline tapaer". for data in disp domain

	return:
	trace in acceleration domain.
	"""
	trace.remove_response(inventory=inv, output="DISP")
	Ts = trace.stats.delta
	ydata = trace.data
	xdata = np.arange(0, len(ydata)*Ts, Ts)

	popt, pcov = curve_fit(func, xdata, ydata)
	x = xdata
	ybaseline = func(x, *popt)
	if (len(xdata)-len(ydata) == 1):
		xdata = xdata[:-1]

	trace.data = ydata - ybaseline

	trace.remove_response(inventory=inv, output="ACC")
	return trace
