#-Assume tipple is full at 5 a.m. of Day 1 and workers who loaded the tipple have already been paid
#-Assume Day 1 is a Sunday
#-Assume at least one crew is working to fill tipple if it is not full and no trains are waiting
#-Assume trains are filled on a first-come, first-serve basis
#-Two crews should always be working if train is waiting (demurrage is costlier than crew)
#-The simulation is executed on an hourly basis
#-Work modulo 24 to simulate 24 hours in each day
import random
import operator

def display_results():
    total_wait_time = 0
    total_hc_wait_time = 0
    total_demurrage = 0
    total_hc_demurrage = 0
    total_crew_hours = [0 for i in range(max_crew_number)]

    for day in days:
        for train in day:
            if train['engines'] == 3:
                total_wait_time += train["waiting_time"]
                total_demurrage += train["demurrage"]
            else:
                total_hc_wait_time += train["waiting_time"]
                total_hc_demurrage += train["demurrage"]   
    
    for day in range(number_of_days):
    	for crew in range(max_crew_number):
    		total_crew_hours[crew] += crew_hours[day][crew]
    
    first_crew_cost = total_crew_hours[0] * first_crew_rate
    additional_crews_cost = sum(total_crew_hours) * additional_crew_rate - total_crew_hours[0] * additional_crew_rate
    total_crew_cost = first_crew_cost + additional_crews_cost

    #print("Two crews on Thursdays, one crew in all other cases")
    #print("Three crews on Thursdays, two crews when a train is waiting, once crew in remaining cases")
    #print("Three crews when a train is waiting and on Thursdays, one crew in remaining cases")
    #print("Three crews when a train is waiting and on Thursdays, two crews in remaining cases")
    #print("Three crews in all cases")
    print("REGULAR SCENARIO")
    print("Number of days simulation is run: %d" % (number_of_days))    
    print("Total Waiting Time: %.3f" % (total_wait_time))
    print("Total High Capacity Waiting Time: %d" % (total_hc_wait_time))
    print("Total Demurrage: %d" % (total_demurrage))
    print("Total High Capacity Demurrage: %d" % (total_hc_demurrage))
    print("Average Waiting Time: %.3f" % (total_wait_time/number_of_days/3))
    print("Average High Capacity Waiting Time: %.3f" % (total_hc_wait_time/number_of_thursdays))
    print("Hours worked by first crew: %.2f" % (total_crew_hours[0]))
    print("Hours worked by second crew: %.2f" % (total_crew_hours[1]))
    print("Cost of first crew: %.2f" % first_crew_cost)
    print("Cost of additional crew(s): %.2f" % additional_crews_cost)
    print("Total cost of crews: %.2f" % total_crew_cost)
    print("Total cost (demurrage and crew): %.2f" % (total_crew_cost + total_demurrage + total_hc_demurrage))

def generate_arrival_time():
	#Time of standard train arrivals is uniformly distributed between 0500 and 2000
	#Trains arrive on the hour
	return random.choice([5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])

def generate_hc_arrival_time():
	#Time of high-capacity train arrival is uniformly distribruted between 1100 and 1300
	#Trains arrive on the hour
	return random.choice([11, 12, 13])

def is_thursday(i):
	#Returns True if it is Thursday (fifth day of week)
	return i % days_in_week == 4

def work_before_next_train(train, day, train_index):
	#Returns time tipple is available and full enough to load current train
	#Calculates and tracks hours worked by crews to fill tipple
	global tipple_available
	global coal_left_in_tipple
	global current_day

	#Determine number of crews that should be working when no trains are waiting to be filled and considering day of week:
	waiting = False
	crews = number_of_crews(waiting, train_index)

	#Calculate hours necessary to fill tipple to its maximum capacity (with one or two crews):
	hours_until_full = ((tipple_max - coal_left_in_tipple)/tipple_loading_rate)/crews
	
	#Calculate hours worked by both crews between trains:
	if train['arrival_time'] >= tipple_available and train['day'] == current_day:
		hours_worked = (train['arrival_time'] - tipple_available) % 24
	else:
		hours_worked = 0

	if hours_until_full < hours_worked:
		hours_worked = hours_until_full 

	#Track hours worked by each crew:
	for crew in range(crews):
		crew_hours[day][crew] += hours_worked

	#Update coal left in tipple after the crews work the determined amount of hours:
	coal_left_in_tipple += (hours_worked * tipple_loading_rate) * crews

	#Return time the tipple is available for the train to be loaded:
	if tipple_available > train['arrival_time'] or (tipple_available <= train['arrival_time'] and current_day != train['day']):
		return tipple_available
	else:
		return (tipple_available + hours_worked) % 24

def train_load_start(train, day, train_index):
	#Calculates time current train starts loading based on amount of coal in tipple at train's arrival time
	global tipple_available
	global coal_left_in_tipple
	if (train['arrival_time'] < tipple_available and current_day == train['day']) or (train['arrival_time'] >= tipple_available and current_day != train['day']):
		if train['engines'] == 3 and coal_left_in_tipple < 1.0:
			#Determine number of crews that should be working when at least one train is waiting to be filled:
			waiting = True
			crews = number_of_crews(waiting, train_index)
			prev_coal_in_tipple = coal_left_in_tipple
			coal_left_in_tipple = 1.0
			for crew in range(crews):
				crew_hours[day][crew] += (((1.0 - prev_coal_in_tipple)/tipple_loading_rate)/crews)
			return (tipple_available + ((1.0 - prev_coal_in_tipple)/tipple_loading_rate)/crews) % 24
		elif train['engines'] == 5 and coal_left_in_tipple < 1.5:
			#Determine number of crews that should be working when at least one train is waiting to be filled:
			waiting = True
			crews = number_of_crews(waiting, train_index)
			prev_coal_in_tipple = coal_left_in_tipple
			coal_left_in_tipple = 1.5
			for crew in range(crews):
				crew_hours[day][crew] += (((1.5 - prev_coal_in_tipple)/tipple_loading_rate)/crews)
			return (tipple_available + ((1.5 - prev_coal_in_tipple)/tipple_loading_rate)/crews) % 24
		else:
			return tipple_available % 24
	elif train['engines'] == 3 and coal_left_in_tipple < 1.0:
		#Determine number of crews that should be working when at least one train is waiting to be filled:
		waiting = True
		crews = number_of_crews(waiting, train_index)
		prev_coal_in_tipple = coal_left_in_tipple
		coal_left_in_tipple = 1.0
		for crew in range(crews):
			crew_hours[day][crew] += (((1.0 - prev_coal_in_tipple)/tipple_loading_rate)/crews)
		return (train['arrival_time'] + ((1.0 - prev_coal_in_tipple)/tipple_loading_rate)/crews) % 24
	elif train['engines'] == 5 and coal_left_in_tipple < 1.5:
		#Determine number of crews that should be working when at least one train is waiting to be filled:
		waiting = True
		crews = number_of_crews(waiting, train_index)
		prev_coal_in_tipple = coal_left_in_tipple
		coal_left_in_tipple = 1.5
		for crew in range(crews):
			crew_hours[day][crew] += (((1.5 - prev_coal_in_tipple)/tipple_loading_rate)/crews)
		return (train['arrival_time'] + ((1.5 - prev_coal_in_tipple)/tipple_loading_rate)/crews) % 24
	else:
		return train['arrival_time'] % 24

	print("ERROR: Load time not set")
	quit()

def train_waiting_time(train, day, train_index):
	#Returns total waiting time for current train
	if train['engines'] == 3:
		return (train['load_start'] - train['arrival_time']) % 24
	else: 
		#Determine number of crews that should be working while train is waiting to be filled:
		waiting = True
		crews = number_of_crews(waiting, train_index)

		#Account for hours worked by crew to refill tipple:
		for crew in range(crews):
			crew_hours[day][crew] += ((0.5/tipple_loading_rate)/crews)

		#Add time it takes to fill tipple to waiting time so high-capacity train can finish loading:
		return ((train['load_start'] - train['arrival_time']) % 24) + (0.5/tipple_loading_rate)/crews

def number_of_crews(waiting, train_index):
	#Determines number of crews that should be working
	if waiting:
		return 2
	elif is_thursday(train_index):
		return 2
	else:
		return 1

random.seed(0)

number_of_days = 7300 #Number of days the simulation is run
number_of_thursdays = 0 #Number of Thursdays covered by the simulation
days_in_week = 7 #Number of days in a week
tipple_loading_rate = 0.25 #Crew can fill tipple at rate of 0.25 units per hour
standard_train_load_time = 3 #Takes 3 hours to load standard train
hc_train_load_time = 6 #Takes 6 hours to load high-capacity train
demurrage_rate = 5000 #Demurrage rate is $5000 per engine per hour
first_crew_rate = 9000 #First crew loads tipple at rate of $9000 per hour
additional_crew_rate = 12000 #Second and third crews load tipple at rate of $12000 per hour
max_crew_number = 3 #Maximum number of crews that can load tipple at one time
coal_left_in_tipple = 1.5 #Standard train loads of coal remaining in tipple
tipple_max = 1.5 #Maximum amount of standard train loads of coal the tipple can hold
tipple_available = 5 #Time at which tipple is available on first day of simulation
current_day = 0 #Tracks which day it is based on time (from 0 to (number_of_days - 1))

#Trains sorted by day in a 2D array:
#Example: train[0][2] refers to dictionary for third train on day 1
days = [[] for i in range(number_of_days)] 

#Generate one high-capacity (five-engine) train arrival time for each Thursday:
for i in range(number_of_days):
	if is_thursday(i):
		days[i].append({'arrival_time':generate_hc_arrival_time(), 'engines':5, 'load_time':6, 'day':i})
		number_of_thursdays += 1

#Generate three standard (three-engine) train arrival times for each day:
for i in range(number_of_days):	
	for j in range(3):
		days[i].append({'arrival_time':generate_arrival_time(), 'engines':3, 'load_time':3, 'day':i})

#Sort trains for each day based on arrival time:
for day in range(number_of_days):
	for train in range(len(days[day])):
		days[day].sort(key=operator.itemgetter('arrival_time'))

#2D array that holds hours worked by first and second crew each day:
#Example: crew_hours[0][1] represents hours worked by second crew on day 1
crew_hours = [[0 for crew in range(max_crew_number)] for day in range(number_of_days)]

def simulation():
	#Loops through days and crew_hours simultaneously to simulate trains being loaded each day
	global tipple_available
	global coal_left_in_tipple
	global current_day
	for day, daily_hours in zip(days, crew_hours):
		for train in day:
			#Determine when tipple will be full enough to fill train until train is at its maximum capacity:
			tipple_available = work_before_next_train(train, days.index(day), day.index(train))

			#Determine when the train begins to load:
			train['load_start'] = train_load_start(train, days.index(day), day.index(train))

			#Calculate the train's total waiting time:
			train['waiting_time'] = train_waiting_time(train, days.index(day), day.index(train))
			
			#Subtract from tipple the amount of coal loaded into current train:
			if train['engines'] == 3:
				coal_left_in_tipple -= 1.0
			else:
				coal_left_in_tipple -= 1.5

			#Catch if amount of coal left in tipple becomes negative:
			if coal_left_in_tipple < 0:
				print("ERROR: Negative amount of coal in tipple")
				quit()

			#Calculate when the train finishes loading:
			train_load_stop = (train['arrival_time'] + train['waiting_time'] + train['load_time'])
			train['load_stop'] = train_load_stop % 24
			tipple_available = train['load_stop']

			#Account for trains being loaded overnight:
			if day.index(train) == (len(day) - 1) and coal_left_in_tipple < 1.5 and train['load_stop'] >= 18:
				tipple_available -= 24

			#Account for carry over into next day:
			if train['load_stop'] < train_load_stop and current_day == train['day']:
				current_day += 1

		#Update current_day to ensure it correctly reflects the current day:
		if current_day < days.index(day) + 1:
			current_day += 1

#Execute the simulation:
simulation()

#Calculate demurrage for each train:
for day in days:
	for train in day:
		train['demurrage'] = train['waiting_time'] * train['engines'] * demurrage_rate

#Calculate crew costs for each day:


#Display results:
display_results()

#Print results:
"""print("******************************************************************************************************************************")
print("FOR TESTING ONLY:")
i = 1
for day in days:
	print("Day " + str(i))
	i += 1
	for train in day:
		print(train)"""
