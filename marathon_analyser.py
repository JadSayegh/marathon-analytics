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
	
	with open(csv_path, 'r') as org:
		with open(clean_csv_path , 'w') as clean:
			for index, line in enumerate(org):	
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