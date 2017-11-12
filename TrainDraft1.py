#-Assume tipple is full at 5 a.m. of Day 1 and workers who loaded the tipple have already been paid
#-Always have a single crew work overnight (2000-0500) for six hours to fill the tipple for the next morning
#-Assume tipple is full when simulation starts (filled the night prior)
#-Assume at least one crew is working to fill tipple if it is not full and no trains are waiting
#-This means the tipple must be filled once on every day except Thursday
#-Two crews should always be working if train is waiting (demurrage is costlier than crew)
import random
import operator

def display_results():
    total_wait_time = 0
    total_hc_wait_time = 0
    total_demurrage = 0
    total_hc_demurrage = 0
    for day in days:
        for train in day:
            if train['engines'] == 3:
                total_wait_time += train["waiting_time"]
                total_demurrage += train["demurrage"]
            else:
                total_hc_wait_time += train["waiting_time"]
                total_hc_demurrage += train["demurrage"]       
    print("Total Waiting Time: %d" % (total_wait_time))
    print("Total High Capacity Waiting Time: %d" % (total_hc_wait_time))
    print("Total Demurrage: %d" % (total_demurrage))
    print("Total High Capacity Demurrage: %d" % (total_hc_demurrage))
    print("Average Waiting Time: %d" % (total_wait_time/number_of_days/3))
    print("Average High Capacity Waiting Time: %d" % (total_hc_wait_time/number_of_days/3))

def generate_arrival_time():
	#Time of standard train arrivals is uniformly distributed between 0500 and 2000
	#Trains arrive on the minute
	return random.choice([5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])

def generate_hc_arrival_time():
	#Time of high-capacity train arrival is uniformly distribruted between 1100 and 1300
	#Trains arrive on the minute
	return random.choice([11, 12, 13])

def is_thursday(i):
	"""Returns True if it is Thursday"""
	return i % 7 == 4

def work_before_next_train(train, day, train_index, crews):
	global tipple_available
	global coal_left_in_tipple
	global current_day
	global waiting
	#Calculate hours necessary to fill tipple (with one or two crews)
	hours_until_full = ((tipple_max - coal_left_in_tipple)/tipple_loading_rate)/crews
	
	#Calculate hours worked by both crews between trains
	if train['arrival_time'] >= tipple_available and train['day'] == current_day:
		hours_worked = (train['arrival_time'] - tipple_available) % 24
	else:
		hours_worked = 0

	if hours_until_full < hours_worked:
		hours_worked = hours_until_full 

	for crew in range(crews):
		crew_hours[day][crew] += hours_worked

	coal_left_in_tipple += (hours_worked * tipple_loading_rate) * crews

	#Return time tipple is available for next train
	if tipple_available > train['arrival_time'] or (tipple_available <= train['arrival_time'] and current_day != train['day']):
		return tipple_available
	else:
		return (tipple_available + hours_worked) % 24

def train_load_start(train, crews, day, train_index):
	#Calculates start time for train based on amount of coal in tipple at train's arrival time
	global tipple_available
	global coal_left_in_tipple
	if (train['arrival_time'] < tipple_available and current_day == train['day']) or (train['arrival_time'] >= tipple_available and current_day != train['day']):
		if train['engines'] == 3 and coal_left_in_tipple < 1.0:
			prev_coal_in_tipple = coal_left_in_tipple
			coal_left_in_tipple = 1.0
			for crew in range(crews):
				crew_hours[day][crew] += (((1.0 - prev_coal_in_tipple)/tipple_loading_rate)/crews)
			return (tipple_available + ((1.0 - prev_coal_in_tipple)/tipple_loading_rate)/crews) % 24
		elif train['engines'] == 5 and coal_left_in_tipple < 1.5:
			prev_coal_in_tipple = coal_left_in_tipple
			coal_left_in_tipple = 1.5
			for crew in range(crews):
				crew_hours[day][crew] += (((1.5 - prev_coal_in_tipple)/tipple_loading_rate)/crews)
			return (tipple_available + ((1.5 - prev_coal_in_tipple)/tipple_loading_rate)/crews) % 24
		else:
			return tipple_available % 24
	elif train['engines'] == 3 and coal_left_in_tipple < 1.0:
		prev_coal_in_tipple = coal_left_in_tipple
		coal_left_in_tipple = 1.0
		for crew in range(crews):
			crew_hours[day][crew] += (((1.0 - prev_coal_in_tipple)/tipple_loading_rate)/crews)
		return (train['arrival_time'] + ((1.0 - prev_coal_in_tipple)/tipple_loading_rate)/crews) % 24
	elif train['engines'] == 5 and coal_left_in_tipple < 1.5:
		prev_coal_in_tipple = coal_left_in_tipple
		coal_left_in_tipple = 1.5
		for crew in range(crews):
			crew_hours[day][crew] += (((1.5 - prev_coal_in_tipple)/tipple_loading_rate)/crews)
		return (train['arrival_time'] + ((1.5 - prev_coal_in_tipple)/tipple_loading_rate)/crews) % 24
	else:
		return train['arrival_time'] % 24

	print("ERROR: Load time not set")
	quit()

def train_waiting_time(train):
	if train['engines'] == 3:
		return (train['load_start'] - train['arrival_time']) % 24
	else: 
		return ((train['load_start'] - train['arrival_time']) % 24) + (0.5/tipple_loading_rate)/crews

def call_second_crew(train):
	"""Returns True if it is determined that second crew should be called"""
	"""OR just move up time that tipple loading ends"""
	if tipple < 1.5 and crews < 2:
		if waiting:
			crews += 1
			return True
		else:
			if(is_thursday(train)):
				#crews++
				return True
			else:
				return False

def number_of_crews(train):
	if tipple < 1.5:
		if waiting:
			crews = 2
		else:
			if(is_thursday(train)):
				crews = 2
			else:
				crews = 1

random.seed(0)

number_of_days = 14 #Number of days the simulation is run
tipple_loading_rate = 0.25 #Crew can fill tipple at rate of 0.25 units per hour, or 0.25/60 units per minute
crews = 2 #number of crews loading tipple at a given time
demurrage_rate = 5000 #demurrage rate is $5000 per engine per hour
standard_train_load_time = 3 #takes 3 hours to load standard train
hc_train_load_time = 6 #takes 6 hours to load high-capacity train
tipple_max = 1.5 #maximum amount of standard train loads of coal the tipple can hold
tipple_available = 5 #time at which tipple is available on first day of simulation
coal_left_in_tipple = 1.5 #standard train loads of coal remaining in tipple
current_day = 0 #tracks which day it is based on time (from 0 to (number_of_days - 1))
waiting = False


"""Trains sorted by day in a 2D array"""
days = [[] for i in range(number_of_days)] 
#train[0][2] refers to dictionary for third train on day 1

#Generate one high-capacity (five-engine) train arrival time for each Thursday:
for i in range(number_of_days):
	if is_thursday(i):
		days[i].append({'arrival_time':generate_hc_arrival_time(), 'engines':5, 'load_time':6, 'day':i})

#Generate three standard (three-engine) train arrival times for each day:
for i in range(number_of_days):	
	for j in range(3):
		days[i].append({'arrival_time':generate_arrival_time(), 'engines':3, 'load_time':3, 'day':i})

#Sort trains for each day based on arrival time:
for day in range(number_of_days):
	for train in range(len(days[day])):
		days[day].sort(key=operator.itemgetter('arrival_time'))

#2D array that holds hours worked by first and second crew each day
crew_hours = [[0 for crew in range(2)] for day in range(number_of_days)]
#crew_hours[0][1] represents hours worked by second crew on day 1

#Simulation: loops through days and crew_hours simultaneously
def simulation():
	global tipple_available
	global coal_left_in_tipple
	global current_day
	for day, daily_hours in zip(days, crew_hours):
		for train in day:
			tipple_available = work_before_next_train(train, days.index(day), day.index(train), crews)
			train['load_start'] = train_load_start(train, crews, days.index(day), day.index(train))
			train['waiting_time'] = train_waiting_time(train)
			
			if train['engines'] == 3:
				coal_left_in_tipple -= 1.0
			else:
				coal_left_in_tipple -= 1.5

			if coal_left_in_tipple < 0:
				coal_left_in_tipple = 0

			train_load_stop = (train['arrival_time'] + train['waiting_time'] + train['load_time'])
			train['load_stop'] = train_load_stop % 24
			tipple_available = train['load_stop']

			if day.index(train) == (len(day) - 1) and coal_left_in_tipple < 1.5 and train['load_stop'] >= 18:
				tipple_available -= 24

			#Account for carry over into next day:
			if train['load_stop'] < train_load_stop and current_day == train['day']:
				current_day += 1

		if current_day < days.index(day) + 1:
			current_day += 1

simulation()

#Calculate demurrage for each train:
for day in days:
	for train in day:
		train['demurrage'] = train['waiting_time'] * train['engines'] * demurrage_rate

#Calculate crew costs for each day?
display_results()
print("******************************************************************************************************************************")
#Print results:
print("FOR TESTING ONLY:")
i = 1
for day in days:
	print("Day " + str(i))
	i += 1
	for train in day:
		print(train)
