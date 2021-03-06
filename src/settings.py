raw_data_folder = "../raw_data"
save_data_folder = "../saved_traces"
aa_station_file = "../catalog/AAstation.csv"
CheckAgainFolder = "../checkAgain/"
CheckAgainFile = "../checkAgain/checkAgain.csv"
flatfile = "../catalog/finalDB_fix.csv"
headres = "../catalog/headers"
TraceBinFie = "../checkAgain/trace_bin.csv"

remove_response_unit = "ACC"
save_traces_format = "SLIST"
save_fig_dpi = 400

default_lowpass = 17
default_highpass = 0.01

interpulate_value = [0.01,0.012,0.014,0.017,0.021,0.025,0.030,0.036,0.044,0.052,0.063,0.076,0.091,0.110,0.130,0.160,0.190,0.230,0.280,0.330,0.400,0.480,0.580,0.690,0.830,1.000,1.200,1.450,1.740,2.090,2.510,3.020,3.630,4.370,5.250,6.310,7.590,9.120,10.970,13.180,15.850,19.060,22.910,27.540,33.110,39.810,47.860,57.540,69.180,83.180,100.000]

# distance filter define
mag5updistance = 400  # KM
mag5distance = 300  # KM
mag4distance = 150 # km

# mongo define
flatefile_table_name = "flatfile"
chackagain_table_name = "unprocessed-traces"
host = "127.0.0.1" # localhost
port = 27017 # default port
db_name = "earthquake"

# choose mseed file or files:
prefix_mseed = "2017-11*"