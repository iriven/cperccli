#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
import sys
import os
from itertools import chain

os.setpgrp()

class ColorBase(object):
    @staticmethod
    def all()->list:
        return [
                'grey',
                'red',
                'green',
                'yellow',
                'blue',
                'magenta',
                'cyan',
                'white'
            ]

class ColorCode(type):
    bold = '\033[1m'
    underline = '\033[4m'
    reset = '\033[0m'

    def __new__(self, name, bases, attributes):
        colors = dict()
        for i, name in enumerate(ColorBase.all()):
            colors.update({
                name : '\033[{0}m'.format(str(30 + i)),
                f'bold_{name}' : self.bold + '\033[{0}m'.format(str(30 + i)),
                f'light_{name}' : '\033[{0}m'.format(str(90 + i)),
            })
        attributes['colors'] = colors
        attributes.update(colors)
        return super().__new__(self, name, bases, attributes)

class ColorObject(metaclass=ColorCode):
    @classmethod
    def normalize(self, message, **context):
        context = {
            **context,
            **self.colors,
            'bold': self.bold,
            'underline': self.underline,
            'reset': self.reset}

        return message.format(**context)

class Colors(object):
    
    @staticmethod
    def All()->list:
        return chain([
            ColorObject.cyan, 
            ColorObject.magenta, 
            ColorObject.yellow,
            ColorObject.green, 
            ColorObject.light_blue, 
            ColorObject.white,
            ColorObject.grey, 
            ColorObject.light_red,
            ColorObject.light_grey,
            ColorObject.light_yellow, 
            ColorObject.light_green
        ])
        
if __name__ == '__main__':
    print('Direct access to {} not allowed'.format(__file__))
    sys.exit(0)        
