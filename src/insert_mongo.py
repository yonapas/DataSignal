from pymongo import MongoClient
from pandas import DataFrame, read_csv
import pandas as pd
import numpy as np

flatfile = r"/Users/yona/PycharmProjects/DataSignal/catalog/finalDB_fix.csv"
collection = db["flatfile_"]

df = read_csv(flatfile)
print(df.columns.values)

def func(x):
	try:
		sta = x.split("_")[1]
		return sta
	except IndexError:
		return x

client = MongoClient()
db = client.earthquake

headers = ['Record Sequence Number', 'EQID', 'YEAR', 'MODY', 'HRMN', 'Station Name', 'Component', 'Station Sequence Number', 'Station ID  No', 'Station Type', 'Station Network', 'Depth', 'Earthquake Magnitude', 'Magnitude Type', 'Mo (dynecm)', 'Strike (deg)', 'Dip (deg)', 'Rake Angle (deg)', 'Mechanism', 'Hypocenter Latitude (deg)', 'Hypocenter Longitude (deg)', 'Hypocenter Depth (km)', 'Finite Rupture Model: 1=Yes;  0=No', 'Depth to Top Of Fault Rupture Model', 'Fault Rupture Width (km)', 'Fault Rupture Area (km^2)', 'Fault Name', 'Slip Rate (mm/Yr)', 'EpiD(km)', 'HypD(km)', 'Joyner-Boore Dist (km)', 'FW/HW Indicator', 'Source to Site Azimuth (deg)', 'Vs30 (m/s) selected for analysis', 'Preferred NEHRP Based on Vs30', 'Surface Geological Unit', 'Station Latitude', 'Station Longitude', 'Depth to Top Judea (km)', 'Depth to Vs=1100', 'File Name (Horizontal 1)', 'File Name (Horizontal 2)', 'File Name (Vertical)', 'H1 azimth (degrees)', 'H2 azimith (degrees)', 'Type of Recording', 'Instrument Model', 'Type of Filter', 'npass', 'HP (Hz)', 'LP (Hz)', 'Factor', 'Lowest Usable Freq - V (Hz)', 'PGA (g)', 'PGV (cm/sec)', 'PGD (cm)', '0.01', '0.012', '0.014', '0.017', '0.021', '0.025', '0.030', '0.036', '0.044', '0.052', '0.063', '0.076', '0.091', '0.110', '0.130', '0.160', '0.190', '0.230', '0.280', '0.330', '0.400', '0.480', '0.580', '0.690', '0.830', '1.00', '1.20', '1.450', '1.740', '2.090', '2.510', '3.020', '3.630', '4.370', '5.250', '6.310', '7.590', '9.120', '10.970', '13.180', '15.850', '19.060', '22.910', '27.540', '33.110', '39.810', '47.860', '57.540', '69.180', '83.180', '100.00']
# header = list(df.columns.values)
df = df[headers]
df["Station Name"] = df["Station Name"].apply(lambda x: func(x))
df = df.sort_values(['YEAR','MODY','HRMN','Station Name','Component']).drop_duplicates(subset=['YEAR','MODY','HRMN','Station Name','Component']).reset_index()
print(df[:5])


df.to_csv("../catalog/FlatFile_2018.csv", index=False)

hz = df.iloc[:, 56:].values.tolist()
df["FAS"] = hz

freq = [0.01,0.012,0.014,0.017,0.021,0.025,0.030,0.036,0.044,0.052,0.063,0.076,0.091,0.110,0.130,0.160,0.190,0.230,0.280,0.330,0.400,0.480,0.580,0.690,0.830,1.00,1.20,1.450,1.740,2.090,2.510,3.020,3.630,4.370,5.250,6.310,7.590,9.120,10.970,13.180,15.850,19.060,22.910,27.540,33.110,39.810,47.860,57.540,69.180,83.180,100.00]
d = list(df.columns[56:-1])
dff = df.drop(d, axis=1)


# print(dff["Station Name"])
# print(list(dff.columns[:]))
data_to_mongo = dff.to_dict(orient='records')

collection.insert_many(data_to_mongo)

collection.update_many({}, {"$set": {"Frequency": freq}})

