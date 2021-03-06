from datetime import datetime
from glob import glob

import numpy as np
import os
import settings
from obspy.geodetics import gps2dist_azimuth

trash = settings.CheckAgainFile
bin = settings.CheckAgainFolder

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
		t_file = datetime.strptime(line[0],'%m/%d/%Y')
		if compare_dates(date, t_file):
			epi_center = {"lat": float(line[6]), "long": float(line[7])}
			# mw = line[-1].split("\\")[0]
			mw = line[3]
			try:
				mw = float(mw)
			except:
				mw = float(line[3])
			return {"mw": mw, "epi_center": epi_center}


def find_eq_details_2018(date):
	eq_file = open("../catalog/rslt_M3to9_2018.csv", "r").readlines()
	for line in eq_file[1:]:
		line = line.split(",")
		t_file = datetime.strptime(line[1], '%Y-%m-%dT%H:%M:%S.%f')
		if compare_dates(date, t_file):
			epi_center = {"lat": float(line[5]), "long": float(line[6])}
			# mw = line[-1].split("\\")[0]
			mw = line[4]
			try:
				mw = float(mw)
			except:
				mw = float(line[4])
			return {"mw": mw, "epi_center": epi_center}



def calculate_distance(staloc, eventloc):
	sta_lat = staloc["latitude"]
	sta_lng = staloc["longitude"]

	event_lat = eventloc["lat"]
	event_lng = eventloc["long"]

	epi_dist, az, baz = gps2dist_azimuth(float(event_lat), float(event_lng), float(sta_lat), float(sta_lng))
	return round(epi_dist/1000, 6)


def double_integrate(acc, dt):
	"""

	:param acc: data in g unit!
	:param dt:
	:return: PGA PGV PGD
	"""
	velocity = [0]
	disp = [0]

	for a in acc:
		velocity.append(velocity[-1] + a * dt)
	del velocity[0]

	for v in velocity:
		disp.append(disp[-1] + v * dt)
	del disp[0]

	PGD = max(np.abs(disp))
	PGV = max(np.abs(velocity))
	PGA = max(np.abs(acc))

	return {"PGA": PGA, "PGV": PGV, "PGD": PGD}


def movefromtrash(event, sta):
	trash_csv = open(trash, "r").readlines()
	new_trash = open(trash, "w")

	for line in trash_csv:
		if event in line and sta in line:
			pass
		else:
			new_trash.write(line)

	for filename in glob("{0}/{1}_{2}*".format(bin, event, sta)):
		os.remove(filename)


