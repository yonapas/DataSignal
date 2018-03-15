import download_mseed 
from datetime import datetime 


def ConvertType(eqinfo):

	eqinfo["Date"] = eqinfo["Date"]
	eqinfo["Time(UTC)"] =eqinfo["Time(UTC)"]
	eqinfo["Millisecond"] = int(eqinfo["Millisecond"])
	eqinfo["Md"] = float(eqinfo["Md"])
	eqinfo["Lat"] = float(eqinfo["Lat"])
	eqinfo["Long"] = float(eqinfo["Long"])
	eqinfo["Depth(Km)"] = float(eqinfo["Depth(Km)"])

	return eqinfo

# read earth quakes catalog from geophisics ins. 
smallEQ = open('rslt_M3to8_2008to2018.csv','r').readlines()
bigEQ = open('rslt_M5to8_1985to2007.csv', 'r').readlines()

# define catagory, same category in file 
category = smallEQ[0].split(",")

# delete heas line from catalog
del smallEQ[0], bigEQ[0]

for EQ in smallEQ:
	eq_data = EQ.split('\n')[0].split(',')
	eq_data = dict(zip(category, eq_data))

	# orgenaize data by type 
	eq_data = ConvertType(eq_data)

	# try to download mseed file from website
	
	Date = "{0}T{1}.{2}".format(eq_data["Date"], eq_data["Time(UTC)"], eq_data["Millisecond"])
	download_mseed.getMseedFromWeb(eq_data["Md"], Date)

