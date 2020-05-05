import datetime
from collections import deque


class Time_Keeper:

	def __init__(self, num_planned_events=None, name=""):
		self.name = name
		self.start_time = datetime.datetime.now()
		self.num_planned_events = num_planned_events
		self.num_completed_events = 0
		self.EVENT_HISTORY_LENGTH = 30
		self.completed_event_times = deque([], self.EVENT_HISTORY_LENGTH)
		self.completed_event_nieve_time_remaining = deque([], self.EVENT_HISTORY_LENGTH)
		self.children = []
		self.parent = None

	def make_child(self, num_planned_events=None,name=""):
		newt = Time_Keeper(num_planned_events,name)
		newt.parent = self
		self.children.append(newt)
		return newt
	
	def get_elapsed_seconds(self):
		current_time = datetime.datetime.now()
		diff = current_time - self.start_time
		return diff.seconds+diff.microseconds/1000000.0
	
	def get_elapsed_minutes(self):
		return self.get_elapsed_seconds()/60.0
	
	def notify_complete_event(self):
		self.num_completed_events += 1

	def get_remaining_minutes(self):
		return (self.get_elapsed_minutes()+0.0001)/(self.num_completed_events+1) * (self.num_planned_events-self.num_completed_events)
	
	def get_progress_text(self):
		if self.num_planned_events is None:
			return "{:.2f} minutes elapsed".format(self.get_elapsed_minutes())
		elif self.num_completed_events > 0:
			return "{} of {} items completed {:.2f} minutes elapsed, {:.2f} minutes remaining".format(self.num_completed_events, self.num_planned_events, self.get_elapsed_minutes(), self.get_remaining_minutes())
		else:
			return "{} items completed {:.2f} minutes elapsed, {:.2f} minutes remaining".format(self.num_completed_events, self.get_elapsed_minutes(), self.get_remaining_minutes())
			
	
	def itterate_over_list(self, arg_list):
		print("")
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>")
		print(">>> Starting Timed Loop: "+self.name)
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>")
		
		self.num_planned_events = len(arg_list)
		self.start_time = datetime.datetime.now()
		for item in arg_list:
			if self.num_completed_events < 100 or self.num_completed_events % 50 == 0:
				print(">>> "+self.get_progress_text())
			yield item, self
			self.notify_complete_event()
		
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>")
		print(">>> Loop " + self.name)
		print(">>> DONE")
		print(">>>")
		print(">>> " + self.get_progress_text())
		print(">>>")
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>")
		print("")
