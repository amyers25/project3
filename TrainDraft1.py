#-Always have a single crew work overnight (2000-0500) for six hours to fill the tipple for the next morning
#-Assume tipple is full when simulation starts (filled the night prior)
#-Assume at least one crew is working to fill tipple if it is not full and no trains are waiting
#-This means the tipple must be filled once on every day except Thursday
#-Two crews should always be working if train is waiting (demurrage is costlier than crew)
import random
import operator

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
	return i % 5 == 3

#def coal_left_in_tipple(loading_time):
	"""Returns amount of coal left in the tipple after a given train has been loaded"""
	#tipple -= ((1/3) * loading_time)

def train_waiting_time(train):
	if train['engines'] == 3:
		return train['load_start'] - train['arrival_time']
	else: 
		return (train['load_start'] - train['arrival_time']) + (0.5/tipple_loading_rate)/crews

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

number_of_days = 10 #Number of days the simulation is run
tipple_loading_rate = 0.25 #Crew can fill tipple at rate of 0.25 units per hour, or 0.25/60 units per minute
crews = 2 #number of crews loading tipple at a given time
demurrage_rate = 5000 #demurrage rate is $5000 per engine per hour
standard_train_load_time = 3 #takes 3 hours to load standard train
hc_train_load_time = 6 #takes 6 hours to load high-capacity train
tipple_available = 5 #tipple available at 5am
coal_left_in_tipple = 1.5 #initiailizing tipple with a full load 


"""Trains sorted by day in a 2D array"""
days = [[] for i in range(number_of_days)] 
#train[0][2] refers to dictionary for third train on day 1

#Generate one high-capacity (five-engine) train arrival time for each Thursday:
for i in range(number_of_days):
	if is_thursday(i):
		days[i].append({'arrival_time':generate_hc_arrival_time(), 'engines':5})

#Generate three standard (three-engine) train arrival times for each day:
for i in range(number_of_days):	
	for j in range(3):
		days[i].append({'arrival_time':generate_arrival_time(), 'engines':3})

#Sort trains for each day based on arrival time:
for i in range(number_of_days):
	for j in range(len(days[i])):
		days[i].sort(key=operator.itemgetter('arrival_time'))


#Simulation
def train_loading_time (train, tipple_available, coal_left_in_tipple):
	for day in days:
		for train in day:
			'''if train arrival time is less than the availibility of the tipple, and the train is normal (3 engines) && the tipple is not 2/3s full(1) the train will begin to load once the tipple has reached 1 standard train load'''
			if train['arrival_time'] < tipple_available:
				if train['engines'] == 3 and coal_left_in_tipple < 1.0:
					train['load_start'] = tipple_available + ((1.0 - coal_left_in_tipple)/tipple_loading_rate)/crews%24
					'''if the train is large (5 engines) && the tipple is not full (1.5) the train will begin to load once the tipple 
					has reached maximum capacity'''
				elif train['engines'] == 5 and coal_left_in_tipple < 1.5:
					train['load_start'] = tipple_available + ((1.5 - coal_left_in_tipple)/tipple_loading_rate)/crews%24
				'''if the tipple is available, and the train is normal (3 engines) && the tipple is not 2/3s full (1) the train will
				begin to load once the tipple has reached 1 standard train load'''
			elif train['engines'] == 3 and coal_left_in_tipple < 1.0:
				train['load_start'] = train['arrival_time'] + ((1.0 - coal_left_in_tipple)/tipple_loading_rate)/crews%24
				'''if the tipple is available, and the train is large (5 engines) && the tipple is not full (1.5) the train will begin 
				to load once the tipple has reached maximum capacity'''
			elif train['engines'] == 5 and coal_left_in_tipple < 1.5:
				train['load_start'] = train['arrival_time'] + ((1.5 - coal_left_in_tipple)/tipple_loading_rate)/crews%24
				'''if the tipple is available, and full, load immediately'''
			else:
				train['load_start'] = train['arrival_time']%24
				'''set the waiting time for train by calling train waiting method (line ~27)'''
			train['waiting_time'] = train_waiting_time(train)
			'''set the load time for a normal train by calling the train loading method (yet to be added)'''
			if train['engines'] == 3:
				train['load_time'] = standard_train_load_time
				coal_left_in_tipple -= 1.0
				'''set the load time for a large train by calling the train loading method (yet to be added)'''
			else:
				train['load_time'] = hc_train_load_time
				coal_left_in_tipple -= 1.5

			train['load_stop'] = train['arrival_time'] + train['waiting_time'] + train['load_time']
			tipple_available = train['load_stop']%24


#Calculate idle time for each day, during which crew is loading tipple if it is not full:


#Calculate demurrage for each train:
def demurrage_calc(train):
	for day in days:
		for train in day:
			train['demurrage'] = train['waiting_time'] * train['engines'] * demurrage_rate

#Calculate crew costs for each day?


#Print results:
i = 1
for day in days:
	print("Day " + str(i))
	i += 1
	for train in day:
		print(train)
