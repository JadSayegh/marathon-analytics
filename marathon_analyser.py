import pandas as pd
import numpy as np
import re, csv
from io import StringIO
from datetime import datetime, timedelta
import string

import pdb
ELEMENT_PER_RACE = 5


def make_clean_marathon_file(csv_path):
	# line below changes "data/abc.csv" to "data/abc_clean.csv"
	clean_csv_path = "".join([*csv_path.split('.')[:-1], "_clean.csv"]) 
	
	with open(csv_path, 'r') as original:
		with open(clean_csv_path , 'w') as clean:
			for index, line in enumerate(original):	
				# line_elm = line.strip().split(',')
				# line_len = len(line_elm)

				line_stream = StringIO(line)
				# handles lines with commas in the fields and make lower case
				line_elm = list(csv.reader(line_stream, skipinitialspace=True))[0]
				for i, elm in enumerate(line_elm):
					line_elm[i] = elm.replace(',', '.').lower()
				
				# check if this line is faulty (too many / too few values to add to the dataframe)
				if (len(line_elm) - 1) % 5 != 0:
					print("ERROR on line %s: line length was %s"%(index + 1, len(line_elm)))
					continue


				# take headers from first line
				if index == 0 :
					clean.write('%s\n'%','.join(line_elm[:6]))
					continue
				
				participant = line_elm[0]

				line_elm = line_elm[1:]
				while line_elm:
					if len(line_elm) < 5:
						print("ERROR parsing data: not enough data in line %s, length was %s:\n\n%s\n\n"%(index + 1, line_len, line))
						break
	
						
					clean.write('%s\n'%','.join([participant] + line_elm[:5]))
					line_elm = line_elm[5:]

def get_age_bracket(date, category):
	seconds_in_day = 86400
	days_in_year = 365.25

	age_low , age_high 	= np.NaN, np.NaN
	if category and not pd.isnull(category):
		date_diff = datetime.strptime("2016:09:25", "%Y:%m:%d") - date #time passed since race
		years_diff = int((date_diff.total_seconds()/seconds_in_day)/days_in_year)
		m = re.search(r'[MFmf](\d+)-(\d+)' , category) 
		if m:
			age_low , age_high = int(m.group(1)), int(m.group(2))
			age_low , age_high = age_low + years_diff , age_high + years_diff # add time offset since last race
		else:
			m = re.search(r'[MFmf](\d+)[\+-]' , category) 
			if m:
				age_low = int(m.group(1))
				age_low += years_diff

	return age_low , age_high

def get_gender(category):
	if category and not pd.isnull(category):
		m = re.search(r'^([MFmf])' , category)
		if m:
			return m.group(1).upper()
	# print("Irregular category:\t%s"%category) # Helps us see what we might have missed
	
	if 'garcons' in str(category) or 'hommes' in str(category):
		return 'M'
	
	return np.NaN

def get_max_age(date, category):
	_, max_age = get_age_bracket(date, category)
	return max_age

def get_min_age(date, category):
	min_age, _ = get_age_bracket(date, category)
	return min_age


def get_datetime_from_str(date_str):
	format = "%Y-%m-%d"
	return (datetime.strptime(date_str, format))

def agg_min_age(ages):
	# uses the max function because the goal is narrow the spread between min and max
	return ages.max()

def agg_max_age(ages):
	# uses the min function because the goal is narrow the spread between min and max
	ages = ages.dropna()
	if not ages.empty:
		return ages.min()
	else:
		return np.NaN

def agg_gender(genders):
	genders = genders.dropna()
	if not genders.empty:
		if genders.nunique() ==1 :
			# Use first element for gender
			return genders.values[0] 
		elif genders.nunique() == 2 and 'M' in genders.values and 'F' in genders.values:
			return "MF"
		else:
			pdb.set_trace()

			print("Gender class irregularity")
			return "??"
	else:
		return np.NaN

def get_participant_info(data, output_path="data/participant_data.csv"):
	# get age, gender info from each participant race entry
	
	participant_race_data = pd.DataFrame()
	participant_race_data['participant id'] = data['participant id']

	#Below: axis=1 --> apply to each row
	data['date'] = data['event date'].apply(get_datetime_from_str) # get event date in date time object
	participant_race_data['max age'] = data[['date', 'category']].apply(lambda x: get_max_age(*x), axis=1) 
	participant_race_data['min age'] = data[['date', 'category']].apply(lambda x: get_min_age(*x), axis=1)
	participant_race_data['gender'] = data['category'].apply(get_gender) # No axis because 'apply' called by a Series

	participant_data = participant_race_data.groupby(['participant id']).agg({ 	
		'max age' : agg_max_age, 
		'min age' : agg_min_age, 
		'gender' : agg_gender})
	# Use the average of max and min age as the participant's age
	participant_data['age'] = (participant_data['max age'] + participant_data['min age'] )/ 2
	pdb.set_trace()
	# Keep min and max age as reference as an indicator of age accuracy
	participant_data = participant_data.reindex_axis(['gender','age', 'min age','max age'], axis=1)
	
	with open(output_path, 'w') as output_file:
		participant_data.to_csv(output_file)



#make_clean_marathon_file("data/marathon.csv")
# data = pd.read_csv("data/marathon_clean.csv")
# get_participant_info(data)

