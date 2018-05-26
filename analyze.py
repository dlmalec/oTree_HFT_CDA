import json
import pandas as pd
import logging

log =logging.getLogger(__name__)



class Market:

	def __init__(self, filename):
		self.events = self.read(filename)

	def read(self, filename):
		try:
			f = open(filename, 'r').read()
		except FileNotFoundError:
			raise Exception('Lab log file not found.')
		splitted = f.split('\n')
		events = [json.loads(row) for row in splitted[:-1]]		# since we split by new line you get the -1
		return events

	def provide(self):
		return self.events

class Processor: 

	initial = {
		'state': 'OUT',
		'speed': False,
		'spread': 2000
	}

	def __init__(self, player_count):
		self.player_count = player_count
		self.init_val = None

	def default(self):
		initial_state= dict()
		for player in range(self.player_count):
			player_no = str(player + 1)
			initial_state[player_no] = self.init_val
		initial_state['time'] = 0
		return initial_state

	def process(self, market):
		""" process market data """

	def update(self, row):
		""" process a row """

	def is_type(self, row, field):
		keep = (1 if row['type'] == field else 0)
		return keep

	def to_dataframe(self):
		""" 
		convert to a dataframe
		do operations if necessary
		"""

	def _rowwisesum(self, df, value):
		df_bool= df.replace(value, 1)
		df_bool= df_bool.where(df == value, 0)
		total = df_bool.sum(axis=1)
		return total

	def export(self, row):
		""" export as csv """


class StateProcessor(Processor):

	def __init__(self, player_count):
		super().__init__(player_count)
		self.init_val = self.__class__.initial['state']    # ? do I need class here ?

	def process(self, market):
		initial_state = self.default()
		data = market.provide() 
		self.states = [dict(initial_state)]   # reference trick !!
		past = initial_state
		for row in data:
			if self.is_type(row, 'state'):
				new_state = self.update(row, past)
				self.states.append(dict(new_state))   # reference trick !!
				past = new_state

	def update(self, row, previous_state):
		new_state = previous_state
		logtime = row['time']
		updating_player  = str(row['context']['player_id'])
		state = row['context']['state']
		new_state[updating_player] = state
		new_state['time'] = logtime
		return new_state

	def to_dataframe(self):
		df = pd.DataFrame.from_records(self.states, index='time')
		df['Total MAKER'] = self._rowwisesum(df, 'MAKER')
		df['Total SNIPER'] = self._rowwisesum(df, 'SNIPER')
		return df


class SpeedProcessor(Processor):

	def __init__(self, player_count):
		super().__init__(player_count)
		self.init_val = self.__class__.initial['speed']    # ? do I need class here ?

	def process(self, market):
		initial_state = self.default()
		data = market.provide() 
		self.states = [dict(initial_state)]   # reference trick !!
		past = initial_state
		for row in data:
			if self.is_type(row, 'speed'):
				new_state = self.update(row, past)
				self.states.append(dict(new_state))   # reference trick !!
				past = new_state

	def update(self, row, previous_state):
		new_state = previous_state
		logtime = row['time']
		updating_player  = str(row['context']['player_id'])
		state = row['context']['speed']
		new_state[updating_player] = state
		new_state['time'] = logtime
		return new_state

	def to_dataframe(self):
		df = pd.DataFrame.from_records(self.states, index='time')
		f = self._rowwisesum(df, True)
		s = self._rowwisesum(df, False)
		df['Total Fast'] = f
		df['Total Slow'] = s
		return df


def test():
	market = Market('../logs/exp_20180522 14.04.txt')
	processor = SpeedProcessor(2)
	processor.process(market)
	df = processor.to_dataframe()
	df.to_csv('test-3.csv')
	return df


if __name__ == '__main__':
	test()




