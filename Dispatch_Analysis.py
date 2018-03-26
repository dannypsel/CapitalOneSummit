from __future__ import division
from collections import Counter
from flask import Flask, render_template, request, url_for
import csv
import os
import sys
import math

app = Flask(__name__)

def compare_time_stamps(r, d):
	r_date = int(r[8:10])
	r_hour = int(r[11:13])
	r_minute = int(r[14:16])
	r_second = int(r[17:19])

	d_date = int(d[8:10])
	d_hour = int(d[11:13])
	d_minute = int(d[14:16])
	d_second = int(d[17:19])

	result = 0
	if(r_date>d_date):
		d_hour+=24
		result+=(d_hour-r_hour)*3600 + (d_minute-r_minute)*60 + (d_second-r_second)

	else:
		result+=(d_hour-r_hour)*3600 + (d_minute-r_minute)*60 + (d_second-r_second)
	
	return result
"""
#test case
test_d=	"2018-01-25 00:05:31.000000 UTC"
test_r=	"2018-01-24 07:05:05.000000 UTC"
print(compare_time_stamps(test_r, test_d))
"""

def long_lat_sat (long_t, lat_t, time_t, long, lat, time, unit_type):
	result = list()
	for i in range(len(long)):
		long_temp = float(long[i])
		lat_temp = float(lat[i])
		time_temp = time[i]
		unit_temp = unit_type[i]
		if(math.sqrt(((long_temp-long_t)*88000)**2 + ((lat_temp-lat_t)*111000)**2) < 400):

			if(abs(compare_time_stamps(time_temp, time_t))<1800):
				result.append(unit_temp)
	return result

def least_common(l):
    return min(set(l), key=l.count)

def most_common(l):
    return max(set(l), key=l.count)


#1. Given an address and time, what is the most likely dispatch to be required?
def most_likely_dispatched(file, long_t, lat_t, time_t):

	data = csv.reader(csvfile)
	#transposes the data
	new_data = map(list, zip(*data))

	
	for row in new_data:
		if(row[0]=="dispatch_timestamp"):
			dispatched_ts = row[1::]
		elif (row[0]=="latitude"):
			lat = row[1::]

		elif (row[0]=="longitude"):
			long = row[1::]
		elif (row[0]=="unit_type"):
			unit_type = row[1::]

	unit_type_list = long_lat_sat (long_t, lat_t, time_t, long, lat, dispatched_ts, unit_type)

	result = Counter(unit_type_list).most_common(1)

	if(len(result)==0):
		return None
	else:
		return result[0][0]


#2. Which areas take the longest time to dispatch to on average? How can this be reduced?
def dispatch_required(file):
	with open(file) as csvfile:
		data = csv.reader(csvfile)
		#transposes the data
		new_data = map(list, zip(*data))

		

		#gets data needed from all data
		for row in new_data:
			if(row[0]=="dispatch_timestamp"):
				dispatched_ts = row[1::]
			elif (row[0]=="received_timestamp"):
				received_ts = row[1::]
			elif (row[0]=="zipcode_of_incident"):
				zip_code = row[1::]

		max_dispatch = 0
		max_index = 0

		#find the largest dispatched time
		for i in range(len(dispatched_ts)):
			compare = compare_time_stamps(received_ts[i], dispatched_ts[i])
			if(compare>max_dispatch):
				max_dispatch = compare
				max_index = i

		return zip_code[max_index]


#3 Crime Correlation: First, match each data to a neighborhood by their zip code, 
#then take the region with the least dispatches. 
def least_crime(file1, zip_code_file):
	with open(file1) as csvfile:
		data = csv.reader(csvfile)

		#transpose the data
		new_data = map(list, zip(*data))


		for row in new_data:
			if (row[0]=="zipcode_of_incident"):
				zip_code = row[1::]

		least_common_zip = least_common(zip_code)


	with open(zip_code_file) as csvfile:
		zip_data = csv.reader(csvfile)
		for row in zip_data:
			if(row[0]==least_common_zip):
				return row[1]
		return None
		
#4: Preparing for the future:
#Compare each neighborhoods dispatches for the first three days vs dispatches over all 12 days. 
#The  region with the biggest change is the one with the greatest increase in dispatch calls. 
#(Find 3 regions) 
#Also find the most common type of dispatch service at each of the 3 regions.

def future(file, zip_code_file):

	with open(file) as csvfile:
		data = csv.reader(csvfile)
		#transposes the data
		new_data = map(list, zip(*data))

		call_date=list()
		for row in new_data:
			if(row[0]=="call_type"):
				call_type = row[1:]
			elif(row[0]=="zipcode_of_incident"):
				zip_code = row[1:]
			elif(row[0]=="call_date"):
				call_date = row[1:]
		call_date_mini = list()
		call_type_mini = list()
		zip_mini = list()
		for i in range(len(call_date)):
			if(len(call_date[i])>4):
				temp = call_date[i][2:4]
				if(int(temp)<16):
					call_date_mini.append(call_date[i])
					call_type_mini.append(call_type[i])
					zip_mini.append(zip_code[i])
	with open(zip_code_file) as csvfile:
		zip_data = csv.reader(csvfile)

		max = 0
		second = 0
		max_neigh = ""
		second_neigh = ""
		max_zip = ""
		second_zip = ""

		for(row) in zip_data:
			temp = list.count(zip_mini, row[0])

			temp2 = list.count(zip_code, row[0])

			temp3 = ((temp2)/12) - (temp/3)
			if(temp3 > max):
				max = temp3
				max_neigh = row[1]
				max_zip = row[0]
			elif(temp3>second):
				second = temp3
				second_neigh = row[1]
				second_zip = row[0]


		return ((max_neigh, largest_dispatch_service(max_zip, zip_code, call_type)),
				(second_neigh, largest_dispatch_service(second_zip, zip_code, call_type)))

def largest_dispatch_service(zip_code_t, zip_code_list, call_type_list):
	call_type = list()
	for i in range(len(zip_code_list)):
		if(zip_code_list[i]==zip_code_t):
			call_type.append(call_type_list[i])
	return most_common(call_type)





print(least_crime("sfpd_dispatch_data_subset.csv", "SF_zip_code_to_neighborhood.csv"))
print(most_likely_dispatched("sfpd_dispatch_data_subset.csv", -122.4142853, 37.78186545, "2018-01-24 12:01:55.000000 UTC" ))
print(dispatch_required("sfpd_dispatch_data_subset.csv"))
print(future("sfpd_dispatch_data_subset.csv", "SF_zip_code_to_neighborhood.csv"))

