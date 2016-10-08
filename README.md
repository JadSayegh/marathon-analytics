# marathon-analytics


In this post, we'll be getting some practice with data scrubbing and data mining using the Pandas module in Python. A friend of mine taking a machine learning class was gracious enough to share one of their assignment data with me. The dataset shows data for 8713 race participants, including what races each participant has recently competed in, the date, what kind of race it was, their time of completition and finally their category in the race (usually consists of an age bracket and a gender). 


### Restructuring the Dataset

While this all seems dandy, a quick look at the .csv shows that each racer's data is crammed into a single line, with some lines containing many more fields than others (when the participant has done many more races), and redundant column headers. 
Since I want to be able to use each race data as its own entry (and also because Pandas won't access a jagged .csv), our first step will be to reorganize the data, and have every participant's individual race data appear on its own row.

As a first try I parsed the lines using .split(',')

line_elm = line.strip().split(',')

However, this would tripped on rows containing commas such as the one below

02:15:26,M30-39,2012-04-29,Banque Scotia 21km et 5km,"21,1 km",01:58:34,M30-34

Instead, I used the built in `csv` module to deal with the in-field commas, and as an added bonus, replaced the commas by periods. While this doesn't hurt the readability of categorical data, at least this way values such as "25,5 km" still make sense. NOTE: This probably isn't a good idea if there are values like "10,000" in the dataset.

with open('data/marathon_clean.csv' , 'w') as clean:
	for index, line in enumerate(org):	
		line_stream = StringIO(line)
		# handles lines with commas in the fields and make lower case
		line_elm = list(csv.reader(line_stream, skipinitialspace=True))[0]
		for i, elm in enumerate(line_elm):
			line_elm[i] = elm.replace(',', '.').lower()

Now that that's out of the way, I extract the headers from the first line, then go through every line and breaking up everything that's after the participant ID into chunks of 5. Each of these is now it's own line, in a more coherent table. 

In case there's any issues with the way a particular csv line is structured I use the code below to make sure that the number of line elements checks out. If not I print a message and skip this line. Another approach would print the faulty line to a "trouble.csv" file on which we can experiment to see more clearly why our current code isn't working. This is the approach I used to find the issues discussed above.

# check if this line is faulty (too many / too few values to add to the dataframe)
if (len(line_elm) - 1) % 5 != 0:
	print("ERROR on line %s: line length was %s"%(index + 1, len(line_elm)))
	continue

Full function code below:


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


### Extracting/Estimating Age and Gender

My first bit of data mining concerned getting information on each participant's age and gender from the "category" colums. Since most categories are expressed in age brackets, I decided to use these age brackets with the race date to calculate, for every participant, a maximum age and minimum age according to each race. 


participant_race_data = pd.DataFrame()
participant_race_data['participant id'] = data['participant id']
participant_race_data['max age'] = data[['date', 'category']].apply(lambda x: get_max_age(*x), axis=1)
participant_race_data['min age'] = data[['date', 'category']].apply(lambda x: get_min_age(*x), axis=1)
participant_race_data['gender'] = data[['category']].apply(lambda x: get_gender(*x), axis=1)


def get_datetime_from_str(date_str):
	format = "%Y-%m-%d"
	return (datetime.strptime(date_str, format))

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

def get_max_age(date, category):
	_, max_age = get_age_bracket(date, category)
	return max_age

def get_min_age(date, category):
	min_age, _ = get_age_bracket(date, category)
	return min_age

Now that I have the info from each race, it's time to bring all that information together to get the most accurate estimate: I group each race entry by participant, and aggregate the max age, min age and gender. While we end up with some participants having no age / gender data, most participants' age is estimated within a 3 year margin of error, well below the max tolerance threshold, given that we want to use this data to predict their performance.

def get_gender(category):
	if category and not pd.isnull(category):
		m = re.search(r'^([MFmf])' , category)
		if m:
			return m.group(1).lower()
	print(category) # Helps us see what we might have missed
	return np.NaN


For the gender data, while most race cateogries specified gender, some didn't and a few others did so in unexpected ways. By printing out everything that didn't fit the general case, I found that 'hommes' or 'garcons' (French for 'men' and 'boys') was being also being used. 



def agg_min_age(ages):
	# uses the max function because the goal is narrow the spread between min and max
	return ages.max()

def agg_max_age(ages):
	# uses the max function because the goal is narrow the spread between min and max
	ages = ages.where(ages != np.NaN)
	if not ages.empty:
		return ages.min()
	else:
		return np.NaN

def agg_gender(genders):
	# uses the max function because the goal is narrow the spread between min and max
	genders = genders.where(genders != np.NaN)
	if not genders.empty:
		if genders.nunique() > 1 :
			# Use first element for gender
			return genders[0] 
		else:
			print("Gender class conflict.")
			return "??"
	else:
		return np.NaN


participant_data = participant_race_data.groupby(['participant id']).agg({ 	'max age' : agg_max_age,
																			 	'min age' : agg_min_age,
																			  	'gender' : agg_gender})
participant_data['age'] = (participant_data['max age'] + participant_data['min age'] )/ 2
