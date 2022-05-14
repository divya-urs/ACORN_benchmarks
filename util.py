from routemap import *

lp_default = 100

def incr_pathlen_action(i):
    return Action(set_attr='pathlen', set_val=i, set_type='incr')

def set_lp_action(lp_val):
    return Action(set_attr='lp', set_val=lp_val, set_type='set')

def default_lp_action():
    return Action(set_attr='lp', set_val=lp_default, set_type='set')

def prop_comm_action(): # propagate comm
    return Action(set_attr='comm', set_val=None, set_type='prop')

def set_comm_action(comm_val):
    return Action(set_attr='comm', set_val=comm_val, set_type='set')




def incr_pathlen_clause(i):
    return Routemap(
            match_list = [], 
            action_list = [Action(set_attr='pathlen', set_val=i, set_type='incr')],
            seq_num = 10,
            result = 'permit')

def set_comm_clause(comm_val): # set comm to comm_val
    return Routemap(
            match_list = [],
            action_list = [Action(set_attr='comm', set_val=comm_val, set_type='set'),
                        Action('pathlen', 1, 'incr')],
            seq_num = 10,
            result = 'permit')


def drop_comm_clause(bad_comms): # drop if comm is in bad_comms list
    return Routemap(
            match_list = [Match('comm', bad_comms)],
            action_list = [],
            seq_num = 10,
            result = 'deny')

def cond_set_lp_clause(comm_vals, lp_val): # if comm is in comm_vals list, set lp to lp_val
    return Routemap(
            match_list = [Match('comm', comm_vals)],
            action_list = [Action('lp', lp_val, 'set'),
                            Action('pathlen', 1, 'incr')],
            seq_num = 10,
            result = 'permit')


def default_clause(lp_default): # unconditionally set comm and lp to default values
    return Routemap(
            match_list = [],
            action_list = [Action('comm', None, 'prop'),
                            Action('lp', lp_default, 'set'),
                            Action('pathlen', 1, 'incr')],
            seq_num = 10,
            result = 'permit')



        