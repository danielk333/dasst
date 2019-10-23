#!/usr/bin/env python

'''

'''

#Python standard import
import logging
import datetime
import time
import pathlib

#Third party import


#Local import


def extract_format_strings(form):
    '''Extracts the formatting string inside curly braces by returning the index positions
    
    For example:

    string = "{2|number_of_sheep} sheep {0|has} run away"
    form_v = extract_format_strings(string)
    print(form_v)
    for x,y in form_v:
        print(string[x:y])

    gives:
        2|number_of_sheep
        0|has
    '''

    form = ' '+form
    form_v = []
    ind = 0
    while ind < len(form) and ind >= 0:
        ind_open = form.find('{',ind+1)
        ind = ind_open
        if ind_open > 0:
            ind_close = form.find('}',ind+1)
            if ind_close > 0:
                form_v.append((ind_open, ind_close-1))
            ind = ind_close

    return form_v


def extract_format_keys(form):
    '''This function looks for our special formatting of indicating index of argument and name of argument
    
    Returns a list of tuples where each tuple is the key in index format and in named format
    '''
    form_inds = extract_format_strings(form)

    keys = []
    for start, stop in form_inds:
        form_arg = form[start:stop]

        if form_arg.index('|') > 0:
            keys.append(tuple(form_arg.split('|')))
        else:
            raise Exception('Log call formating only works with key | formating')

    return form_inds, keys


def construct_formatted_format(form, args_len, kwargs):
    '''This takes a special formatted string, extracts the two possible keys, 
        and based on what was passed as key-word arguments and what was passed as indexed arguemnts, 
        chooses the correct format. 
        If a option has a default value it will indicate this and not report a value.

        Returns a correctly formatted string for the input arguemts of the function.
    '''
    form_inds, keys = extract_format_keys(form)

    form_str = ''
    cntr = 0
    last_ind = 0

    for start,stop in form_inds:
        form_str += form[last_ind : start]

        ind, key = keys[cntr]

        if key.find('.') > 0:
            key_check = key[:key.find('.')]
        else:
            key_check = key

        if key_check in kwargs:
            form_str += key
            form_str += '}'
        else:
            if ind.find('.') > 0:
                ind_check = int(ind[:ind.find('.')])
            else:
                ind_check = int(ind)

            if ind_check > args_len-1:
                form_str = form_str[:-1]
                form_str += '[' + key + ':default]'
            else:
                form_str += ind
                form_str += '}'

        last_ind = stop+1
        cntr += 1
    form_str += form[last_ind :]

    return form_str


def function_log_call(form, logger, level):

    _log = getattr(logger, level)

    def log_call_decorator(method):
        def logged_fn(*args, **kwargs):

            form_str = construct_formatted_format(
                form,
                len(args),
                kwargs
            )
            _log('{}: {}'.format(
                    method.__name__, 
                    form_str.format(*args, **kwargs)
                )
            )
            return method(*args, **kwargs)

        return logged_fn
    return log_call_decorator


def method_log_call(form, logger, level):

    _log = getattr(logger, level)

    def log_call_decorator(method):
        def logged_fn(*args, **kwargs):

            form_str = construct_formatted_format(
                form,
                len(args),
                kwargs
            )
            _log('{}.{}: {}'.format(
                    repr(args[0]),
                    method.__name__, 
                    form_str.format(*args, **kwargs)
                )
            )
            return method(*args, **kwargs)

        return logged_fn
    return log_call_decorator

