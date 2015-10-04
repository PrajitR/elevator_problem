from elevator import Elevator, Actions
import random
import argparse
import math

class Simulation:
	"""
	Runs the elevator simulation. 
	"""

	def __init__(self, nfloors, max_new_people):
		self.nfloors = nfloors
		self.expo_lambda = [1. / (f ** 2 + 1) for f in xrange(nfloors)]
		self.intervals = [int(random.expovariate(self.expo_lambda[f])) for f in xrange(self.nfloors)]

		self.waiting_people = [[] for _ in xrange(self.nfloors)]
		self.elevator_people = [[] for _ in xrange(self.nfloors)]
		self.max_new_people = max_new_people

		self.elevator = Elevator(self.nfloors)
		self.stats = Stats()

	def run(self, time):
		"""
		Main loop of simulation. At each time step, new people request
		the elevator, the elevator makes an action, and statistics are
		aggregated about wait times and elevator position.
		"""
		for t in xrange(time):
			self.generate_new_requests()
			action = self.elevator.action()
			self.update(action)
		self.stats.display_stats()

	def generate_new_requests(self):
		"""
		Creates new people that request the elevator. Each floor has a 
		separate countdown timer before new people are created at that 
		floor. The intervals are determined by an exponential distribution,
		with varying parameters between floors. Once a timer hits 0, a random
		number of new people are created at the floor who request the elevator.
		"""
		requests = []
		for floor in xrange(self.nfloors):
			if self.intervals[floor] == 0:
				# Create new people on this floor who request elevator.
				new_people = int(random.random() * self.max_new_people) + 1
				for _ in xrange(new_people):
					self.waiting_people[floor].append(Person(self.nfloors, floor))
				requests.append(floor)

				# New interval until floor spawns new people.
				self.intervals[floor] = int(random.expovariate(self.expo_lambda[floor])) + 1
			else:
				# Decrement timer.
				self.intervals[floor] -= 1
		self.elevator.new_requests(requests)

	def update(self, action):
		"""
		Updates the state of people on the floor the elevator has stopped at.
		Also updates statistics about wait times and elevator position.
		"""
		f = self.elevator.current_floor
		self.stats.update_floor(f)

		if action == Actions['open']:
			# People getting off on this floor.
			for p in self.elevator_people[f]:
				self.stats.update_wait(p)
			self.elevator_people[f] = []

			# All waiting people get on the elevator and press their desired location.
			floor_requests = []
			for p in self.waiting_people[f]:
				floor_requests.append(p.desired_floor)
				self.elevator_people[p.desired_floor].append(p)
			self.elevator.new_requests(floor_requests)
			self.waiting_people[f] = []

		for f in xrange(self.nfloors):
			for p in self.elevator_people[f]:
				p.wait(True)
			for p in self.waiting_people[f]:
				p.wait(False)

class Stats:
	"""
	Aggregates waiting and elevator position statistics and displays them.
	"""

	def __init__(self):
		self.floor_wait_times = []
		self.elevator_wait_times = []
		self.floors = []

	def update_wait(self, person):
		"""
		Update waiting time history.
		"""
		self.floor_wait_times.append(person.floor_wait_time)
		self.elevator_wait_times.append(person.elevator_wait_time)

	def update_floor(self, current_floor):
		"""
		Update elevator position history.
		"""
		self.floors.append(current_floor)

	def display_stats(self):
		"""
		Displays basic statistics about wait times. If matplotlib is
		installed, plots detailed graphs about wait times and elevator
		positions.
		"""
		wt, et, n = sum(self.floor_wait_times), sum(self.elevator_wait_times), len(self.floor_wait_times)
		print('Mean waiting for elevator time: %.3f' % ((1. * wt) / n))
		print('Mean waiting on elevator time : %.3f' % ((1. * et) / n))
		print('Mean total wait time          : %.3f' % ((1. * wt + et) / n))

		try:
			# Plot figures if the user has installed matplotlib.
			from matplotlib import pyplot as plt

			fig = plt.figure(1)

			ax = plt.subplot(211)
			ax.set_title('Time spent waiting for elevator')
			ax.set_xlabel('Time')
			ax.set_ylabel('Number of people')
			ax.hist(self.floor_wait_times)

			ax = plt.subplot(212)
			ax.set_title('Time spent waiting on elevator')
			ax.set_xlabel('Time')
			ax.set_ylabel('Number of people')
			ax.hist(self.elevator_wait_times)

			fig = plt.figure(2)
			plt.plot(self.floors)
			ax = plt.gca()
			ax.set_title('Floor of the elevator over time')
			ax.set_ylabel('Floor')
			ax.set_xlabel('Time')

			plt.show()

		except ImportError:
			print('\nWARN: matplotlib not installed. Cannot create graphs. Install with:\n\tpip install matplotlib')

class Person:
	"""
	Represents a person waiting to reach their destination. Maintains
	personal statistics about wait times.
	"""

	def __init__(self, nfloors, floor):
		self.floor_wait_time = 0
		self.elevator_wait_time = 0

		# Randomly choose the desired floor for this person.
		# Biased towards lower floors (ex. people going down during lunch time).
		# Prevent getting on and off at the same floor.
		self.desired_floor = floor
		while self.desired_floor == floor:
			probs = [random.random() * 1 / (f ** 2 + 1) for f in xrange(nfloors)]
			self.desired_floor = sample(probs)

	def wait(self, in_elevator):
		"""
		Increments the wait time, depending on if the person is on
		the elevator or not.
		"""
		if in_elevator:
			self.elevator_wait_time += 1
		else:
			self.floor_wait_time += 1

def sample(probs):
	"""
	Randomly samples from a multinomial distribution.
	"""
	norm = sum(probs)
	rand = random.random() * norm
	i = 0
	while rand > probs[i]:
		rand -= probs[i]
		i += 1
	return i

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Run elevator simulation.')
	parser.add_argument('--floors', type=int, default=50,
	                   help='number of floors in the building')
	parser.add_argument('--iterations', type=int, default=100,
                       help='number of iterations to run simulation for')
	parser.add_argument('--max_new_people', type=int, default=3,
                       help='number of people that can arrive at the same time to wait for elevator')
	args = parser.parse_args()

	s = Simulation(args.floors, args.max_new_people)
	s.run(args.iterations)