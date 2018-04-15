import numpy as np
from datetime import datetime


beta = 3600.0  # m/s sheer wave velocity
dSigma = 4.0  # Stress-drop

smallEQ = open("../catalog/rslt_M3to8_2008to2018.csv", "r").readlines()
bigEQ = open("../catalog/rslt_M5to8_1985to2007.csv", "r").readlines()
del smallEQ[0], bigEQ[0]

allEQ = smallEQ+bigEQ


def calc_fc(mw):
	"""
	function get magnitude moment,
	and return the predictable fc
	:param mw:
	:return fc:
	"""
	m0 = 10**(1.5*(mw+16.05))
	fc = 4.9*(10**6)*beta*(dSigma/m0)**(1.0/3.0)
	return fc


def compare_dates(t1, t2):
	if t1.year == t2.year:
		if t1.month == t2.month:
			if t1.day == t2.day:
				return True
	return False


def find_eq_details(date):

	for line in allEQ:
		line = line.split(",")
		t_file = datetime.strptime(line[0], '%m/%d/%Y')
		t_eq = datetime.strptime(date, '%Y%m%d%H%M%S')
		if compare_dates(t_eq, t_file):
			epi_center = {"lat": float(line[6]), "long": float(line[7])}
			mw = line[-1].split("\\")[0]
			return {"mw": float(mw), "epi_center": epi_center}
