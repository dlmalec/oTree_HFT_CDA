import json
import pandas as pd
import logging

log = logging.getLogger(__name__)

time_start = 0
group_id = 586
player_count = 2


class MarketEvents:

    def __init__(self, filename, group_id):
        self.group_id = group_id
        self.read(filename)

    def read(self, filename):
        try:
            f = open(filename, 'r').read()
        except FileNotFoundError:
            raise Exception('Lab log file not found.')
        splitted = f.split('\n')
        events = []
        for row in splitted[:-1]:   # -1 since we split by a new line
            record = json.loads(row)
            if self._is_group(record):
                events.append(record)
        self.events = events

    def _is_group(self, row):
        keep = 1 if row['group'] == self.group_id else 0
        return keep

    def __iter__(self):
        return iter(self.events)

"""
module level functions to process each row
"""
def update_choice(event, choice_type, choice_state):
    new_state = dict(choice_state[-1])
    player = str(event['context']['player_id'])
    new_choice = event['context'][choice_type]
    new_state[player] = new_choice
    logtime = event['time']
    new_state['time'] = logtime
    choice_state.append(new_state)
    return choice_state


class MarketState:

    start_state = {
        'state': 'OUT',
        'speed': False,
        'profit': 0
    }

    processors = {
        'state': update_choice,
        'speed': update_choice,
        'profit': None  # TODO
    }

    def __init__(self, market_events, player_count):
        self.events = market_events
        self.pc = player_count
        self.init_states()

    def init_states(self):
        self.state = {k: self._default(v) for k, v in self.start_state.items()}

    def _default(self, initial):
        first_row = {str(i + 1): initial for i in range(self.pc)}
        first_row.update({'time': time_start})
        return [first_row]

    def process(self):
        for event in self.events:
            typ = event['type']
            try:
                current_state = self.state[typ]
                new_state = self.processors[typ](event, typ, current_state)
            except KeyError:
                log.info('Processor not available for the type.')
                continue
            self.state[typ] = new_state

    def dump(self):
        return {self.events.group_id : self.state}
    
    def export_json(self, filename):
        out = self.dump()
        with open(filename, 'w') as f:
            json.dump(out, f)



def test():
    market = MarketEvents('./logs/exp_20180522 14.04.txt', group_id)
    state = MarketState(market, player_count)
    state.process()
    state.export_json('test.json')


if __name__ == '__main__':
    test()
