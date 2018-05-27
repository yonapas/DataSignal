import numpy as np 
from numpy import diff
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from scipy import integrate
from obspy import read, read_inventory
from glob import glob
import save_traces


def func(x, a1, a2, a3, a4, a5):
	func = a1*x**2+a2*x**3+a3*x**4+a4*x**5+a5*x**6
	return func


def xdataCorrection(xdata, ydata):
	if (len(xdata) - len(ydata) == 1):
		xdata = xdata[:1]
	return xdata


def useBaseLine(trace, nevent, sta):
	"""
	the funcation get filterd trace (after proccesing)
	and doing "baseline tapaer"- for data in disp domain

	return:
	trace in acceleration domain.
	"""

	trace_baseline = trace.copy()
	acc = trace_baseline.data
	velocity =[0]
	disp = [0]

	dt = trace.stats.delta
	xdata = np.arange(0, len(acc)*dt, dt)

	# double integrate:
	for a in acc:
		velocity.append(velocity[-1] + a*dt)
	del velocity[0]

	for v in velocity:
		disp.append(disp[-1] + v*dt)
	del disp[0]

	# fit polynomial 6th order
	xdata = xdataCorrection(xdata, disp)
	popt, pcov = curve_fit(func, xdata, disp)
	dispBL = func(xdata, *popt)

	# secound derivative for dispBaseLine (fit function)
	velocityBL = np.diff(dispBL)/ np.diff(xdata)
	accBL = np.diff(velocityBL)/ np.diff(xdata[:-1])

	# subtractsthe second  derivative of the fitted  polynomial from the acceleration  
	newAcc = acc[:-2] - accBL

	save_traces.SaveBaseline(acc, disp, newAcc, dispBL, xdata, nevent, sta)

	trace_baseline.data = newAcc

	return trace_baseline
