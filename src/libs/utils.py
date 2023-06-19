#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
import sys
import copy

class dictionary(object):
    
    @staticmethod
    def explode(data: dict, maxkeys: int=15)->list:
        '''
        Splits dict into multiple dicts with given maximum length. 
        Returns a list of dictionaries.
        '''
        subDictionnaries = list()
        current = dict()
        for k, v in data.items():
            if len(current.keys()) < int(maxkeys):
                current.update({k: v})
            else:
                subDictionnaries.append(copy.deepcopy(current))
                current = dict({k: v})
        subDictionnaries.append(current)
        return subDictionnaries
    
    @staticmethod
    def len(data: dict)->int:
        if not isinstance(data, (dict,list)):
            return 0
        if isinstance(data, list):
            return len(data)
        return len(data.keys())
    
    @staticmethod
    def maxValuelen(data:dict)->int:        
        maks=max(data, key=lambda k: len(str(data[k])))
        return len(str(data[maks]))

    @staticmethod
    def maxKeylen(data:dict)->int:        
        return len(max(data, key=len))

class Array(object):
    
    @staticmethod
    def intersect(a, b):
        trim = lambda x:x.strip()
        a = [trim(v) for v in a]
        b = [trim(y) for y in b]
        if len(a) >len(b):
            return list(set(a).intersection(set(b)))  
        return list(filter(lambda x:x in a, b))
        # return list(set(a).intersection(set(a)))       

if __name__ == '__main__':
    print('Direct access to {} not allowed'.format(__file__))
    sys.exit(0)
