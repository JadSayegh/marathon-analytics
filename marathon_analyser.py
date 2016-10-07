import pandas as pd
import numpy as np
import re, csv
from io import StringIO
from datetime import datetime, timedelta
import string

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
	print(category) # Helps us see what we might have missed
	
	if 'garcons' in str(category) or 'hommes' in str(category):
		return 'M'
	
	return np.NaN

def get_max_age(date, category):
	_, max_age = get_age_bracket(date, category)
	return max_age

def get_min_age(date, category):
	min_age, _ = get_age_bracket(date, category)
	return min_age




make_clean_marathon_file("data2/marathon.csv")

