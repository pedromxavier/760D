from functools import wraps

import os
import pickle
import datetime as dt

def kwget(key, kwargs, default=None):
    try:
        return kwargs[key]
    except KeyError:
        return default

class Debugger(object):

    NULL_FUNC = lambda *args, **kwargs : None

    def __init__(self, debug=True, level=0):
        self.__level = level
        self.__debug = debug

    def __getitem__(self, level):
        if self.debug and (self.level is None or self.level >= level):
            tab = '\t' * level
            sep = '\n' + tab
            return lambda *args : self(tab, *args, sep=sep)
        else:
            return self.NULL_FUNC

    def __call__(self, *args, **kwargs):
        if self.debug: return print(*args, **kwargs)

    @property
    def level(self):
        return self.__level

    @property
    def debug(self):
        return self.__debug

    def toggle_debug(self):
        self.__debug = not self.__debug

        if self.__debug:
            print(":: Debug on  ::")
        else:
            print(":: Debug off ::")

class _Tempo(object):

    __ref__ = None

    def __new__(cls):
        if cls.__ref__ is None:
            cls.__ref__ = object.__new__(cls)
        return cls.__ref__

    @property
    def hms(self):
        now = dt.datetime.now()
        return (now.hour, now.minute, now.second)

    @property
    def now(self):
        return dt.datetime.now()

    @property
    def morning(self):
        return 5 <= self.now.hour < 12

    @property
    def evening(self):
        return 12 <= self.now.hour < 18

    @property
    def night(self):
        return not (self.morning or self.evening)

Tempo = _Tempo()