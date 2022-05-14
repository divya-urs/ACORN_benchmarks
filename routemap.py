class Routemap(object):
    '''
    A match action rule
    '''
    def __init__(self, match_list, action_list, seq_num, result):
        self.matches = match_list # list of match stmts -- stmts in the list are ANDed
        self.actions = action_list # list of set stmts (at most one per attribute)
        self.seq_num = seq_num # sequence number; smallest executed first
        self.result = result # permit or deny

    def setsLp(self):
        for a in self.actions:
            if a.set_attr == 'lp':
                return True
        
        return False

    def setsLpNondefault(self, default_lp):
        for a in self.actions:
            if a.set_attr == 'lp' and a.set_val != default_lp:
                return True
        
        return False

    def getNondefaultLpVals(self, default_lp):
        lp_vals = []
        for a in self.actions:
            if a.set_attr == 'lp' and a.set_val != default_lp:
                lp_vals.append(a.set_val)
        
        return lp_vals

    def resultDeny(self):
        return self.result == 'deny'

    def __repr__(self):
        return '\n(match: {}\n actions: {}\n seq_num: {}\n result: {})\n'.format(
            self.matches, self.actions, self.seq_num, self.result)

    def __eq__(self, other):
        return (self.matches == other.matches) and (self.actions == other.actions) and \
            (self.seq_num == other.seq_num) and (self.result == other.result)

    def write(self): # return dictionary
        r = {}
        r['match'] = [m.write() for m in self.matches]
        r['actions'] = [a.write() for a in self.actions]
        r['seq_num'] = self.seq_num
        r['result'] = self.result
        return r
    
    @classmethod
    def read(cls, d):
        matches = [Match.read(m) for m in d['match']]
        actions = [Action.read(a) for a in d['actions']]
        return cls(match_list=matches, action_list=actions, seq_num=d['seq_num'], result=d['result'])


# class Routemap(object):
#     '''
#     A list of route map entries
#     '''
#     def __init__(self, entry_list):
#         self.entry_list = entry_list # list of routemap entries

class Match(object):
    def __init__(self, match_attr, match_vals):
        self.match_attr = match_attr
        self.match_vals = match_vals # list of values (combined using OR) or dictionary of parameters

    def __repr__(self):
        return '(match_attr: {}, match_vals: {})'.format(self.match_attr, self.match_vals)

    def __eq__(self, other):
        return (self.match_attr == other.match_attr) and (self.match_vals == other.match_vals)

    def write(self):
        return {'match_attr': self.match_attr, 'match_vals': self.match_vals}

    @classmethod
    def read(cls, d):
        return cls(match_attr=d['match_attr'], match_vals=d['match_vals'])

class Action(object):
    def __init__(self, set_attr, set_val, set_type):
        self.set_attr = set_attr
        self.set_val = set_val
        self.set_type = set_type # set (assignment), prop (propagate), incr or decr. Community can only be set.

    def __repr__(self):
        return '(set_attr: {}, set_val: {}, set_type: {})'.format(self.set_attr, self.set_val, self.set_type)

    def __eq__(self, other):
        return (self.set_attr == other.set_attr) and (self.set_val == other.set_val) and \
             (self.set_type == other.set_type)

    def write(self):
        return {'set_attr': self.set_attr, 'set_val': self.set_val, 'set_type': self.set_type}

    @classmethod
    def read(cls, d):
        return cls(set_attr=d['set_attr'], set_val=d['set_val'], set_type=d['set_type'])

class Property(object):
    def __init__(self, prop, params={}):
        self.prop = prop
        self.params = params
    
    def __repr__(self):
        return '{}, params: {}'.format(self.prop, self.params)
        
    def __eq__(self, other):
        return (self.prop == other.prop) and (self.params == other.params)

    def write(self):
        return {'name': self.prop, 'params': self.params}
    
    @classmethod
    def read(cls, d):
        return cls(prop=d['name'], params=d['params'])