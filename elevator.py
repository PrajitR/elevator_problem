from collections import deque
from sets import Set

# Set of actionos and how they move the elevator.
Actions = { 'up': 1, 'down': -1, 'open': 0 }

class Elevator:
	"""
	Implements the business logic of a simple elevator. Uses
	a simple decision function that always goes to the next floor
	on the queue, dropping off other people on the way. This bounds
	the maximum wait time by preventing thrashing between two floors.
	Notably, the queue treats elevator requests and destination requests
	the same way, because we want to minimize total wait time.
	"""

	def __init__(self, nfloors):
		self.next_floors = deque()
		self.already_activated = Set()
		self.nfloors = nfloors
		self.current_floor = 1

	def new_requests(self, requests):
		"""
		Add new requests to the queue if they are not
		already on the queue.
		"""
		for floor in requests:
			if floor not in self.already_activated:
				self.next_floors.append(floor)
				self.already_activated.add(floor)

	def action(self):
		"""
		Takes the next action. Open the doors if there are people
		who need to get off. Otherwise, move towards the floor that
		is first on queue.
		"""
		if len(self.next_floors) == 0:
			# Move towards the middle floor if there is nothing to do.
			move = Actions['up'] if self.current_floor < (self.nfloors / 2) else Actions['down']
		elif self.current_floor in self.next_floors:
			self.next_floors.remove(self.current_floor)
			self.already_activated.remove(self.current_floor)
			move = Actions['open']
		else:
			move = Actions['up'] if self.current_floor < self.next_floors[0] else Actions['down']

		self.current_floor += move
		return move
