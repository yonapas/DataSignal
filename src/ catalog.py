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

# define catagory, same category in file 
category = smallEQ[0].split(",")
print(category)

# delete heas line from catalog
del smallEQ[0], bigEQ[0]

for EQ in bigEQ:
	try:
		eq_data = EQ.split('\n')[0].split(',')
		eq_data = dict(zip(category, eq_data))

		# orgenaize data by type
		eq_data = ConvertType(eq_data)

		# try to download mseed file from website
		date =eq_data["Date"]

		Date = "{0}-{1}-{2}T{3}".format(date.year, date.month, date.day, eq_data["Time(UTC)"])
		download_mseed.getMseedFromWeb(eq_data["Md"], Date)
	except:
		print(Date)

