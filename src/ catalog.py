import download_mseed 
from datetime import datetime


def ConvertType(eqinfo):

	eqinfo["Date"] = datetime.strptime(eqinfo["Date"], "%m/%d/%Y")
	eqinfo["Time(UTC)"] =eqinfo["Time(UTC)"]
	eqinfo["Millisecond"] = int(eqinfo["Millisecond"])
	eqinfo["Md"] = float(eqinfo["Md"])
	eqinfo["Lat"] = float(eqinfo["Lat"])
	eqinfo["Long"] = float(eqinfo["Long"])
	eqinfo["Depth(Km)"] = float(eqinfo["Depth(Km)"])

	return eqinfo

# read earth quakes catalog from geophisics ins. 
smallEQ = open('../catalog/rslt_M3to8_2008to2018.csv','r').readlines()
bigEQ = open('../catalog/rslt_M5to8_1985to2007.csv', 'r').readlines()
# eq2018 = open("../catalog/rslt_M3to9_2018.csv", "r").readlines()

# print(bigEQ)

# define catagory, same category in file 
category = bigEQ[0].split(",")
# category = eq2018[0].split(",")
print(category)

# delete heas line from catalog
del smallEQ[0]
del bigEQ[0]

# for EQ in eq2018[1:]:
for EQ in bigEQ[1:2]:
	try:
		eq_data = EQ.split('\n')[0].split(',')
		eq_data = dict(zip(category, eq_data))

		# orgenaize data by type
		eq_data = ConvertType(eq_data)

		# try to download mseed file from website
		# 2018-05-29T22:37:37.980
		# date = datetime.strptime(eq_data["DateTime"], '%Y-%m-%dT%H:%M:%S.%f')
		date = eq_data["Date"]

		# Date = "{0}-{1}-{2}T{3}".format(date.year, date.month, date.day, eq_data["Time(UTC)"])
		# download_mseed.getMseedFromWeb(eq_data["Md"], date)
		download_mseed.getMseedFromWeb(eq_data["Md"], Date)
	except :
		print(eq_data["DateTime"])

