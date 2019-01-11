from pymongo import MongoClient
from pandas import DataFrame, read_csv


client = MongoClient()

db = client.earthquake
coll = db["flatfile_"]

target_col = db["unprocessed-traces"]

flatfile = r"/Users/yona/PycharmProjects/DataSignal/checkAgain/checkAgain.csv"
df = read_csv(flatfile)

df["components"] = df["sta"].apply(lambda x: x.split("_")[-1])
df["network"] = df["sta"].apply(lambda x: x.split("_")[0])
df["sta"] = df["sta"].apply(lambda x: x.split("_")[1])

df["YEAR"] = df["eventname"].apply(lambda x: str(x)[:4])
df["MODY"] = df["eventname"].apply(lambda x: str(x)[4:8])
df["HRMN"] = df["eventname"].apply(lambda x: str(x)[8:12])

df = df.drop(df.columns[:2], axis=1)


remove_index = []

for index, row in df.iterrows():
	dup = coll.find({"YEAR": int(row["YEAR"]), "MODY": int(row["MODY"]), "HRMN": int(row["HRMN"]),
			"Station Name": row["sta"], "Component": row["components"], "Station Network": row["network"]})
	try:
		print(dup.next())
		print(index)
		remove_index.append(index)
	except StopIteration:
		pass

print(remove_index)
df = df.drop(df.index[remove_index])
data_to_mongo = df.to_dict(orient='records')
# print(df.count())

target_col.insert_many(data_to_mongo)
