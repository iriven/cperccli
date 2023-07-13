#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
import os
import re
import sys
sys.path.append(os.getcwd())
from .painters import Colors, ColorObject
from .utils import dictionary, Array

os.setpgrp()

class PERCParser(object):
    
    def __init__(self, data=None, **kwargs) -> None:
        kwargs.setdefault('maxkeys' , 9)
        kwargs.setdefault('EmptyLineRegex' , re.compile('(?:\r?\n){2,}'))
        kwargs.setdefault('hdgBlockRegex', re.compile('^\\s*([^=:]+)\\s*:\\s*(?:\r?\n)[=]+\\s*$'))
        kwargs.setdefault('infBlockRegex' , re.compile('(?m)\s*^\s*(.+)\s*\|\s*(.+)\s*', re.MULTILINE))
        kwargs.setdefault('stdBlockRegex' , re.compile('(?sm)\s*^\s*([^=]+)\s*=\s*([^=\n\r]+)\s*(?:(?:\r?\n)|\Z)', re.MULTILINE))        
        kwargs.setdefault('tblBlockRegex', re.compile('^[-]{2,}\s*(([^-]+)\s*[-]{2,}(?:\r?\n)\s*((.+)\s*(?:\r?\n))+)[-]{2,}', re.MULTILINE))
        kwargs.setdefault('bannedKeys', ['Firmware Version', 'Vendor Id', 'Consistency Check Reoccurrence', 'Topology Type'])
        kwargs.setdefault('specialKeys', ['Controller', 'Model', 'Serial Number', 'Controller Status','SAS Address', 'PCI Address', 'Operating system', 'CLI Version ','Description'])
        for key,value in kwargs.items():
            setattr(self, key, value)
        self.__data = self._parse(data)
        self.__colors = Colors.All()
        self.__color = next(self.__colors)
        
    def _parse(self, ResponseData: str)->list:
        ParsedGroups = list()
        singletons = dict()
        specialGroup = dict()
        #  Each record is separated by double newlines
        BlockDescription = None
        stdBlockDescription = None
        Blocks = self.EmptyLineRegex.split(ResponseData.strip())
        for block in Blocks:
            helpBlock = self.infBlockRegex.findall(block)
            if helpBlock:
                continue 
            Description = self.hdgBlockRegex.findall(block)
            if Description:
                BlockDescription = ''.join(Description).replace('_',' ').upper()
                stdBlockDescription = BlockDescription
                continue             
            sectionBlock = self.tblBlockRegex.findall(block)
            if sectionBlock:
                sectionBlock = sectionBlock[0]
                for sblock in sectionBlock: 
                    sblock = sblock.splitlines()
                    sectionDatas = list()
                    sectionHeaders = list()
                    for element in sblock:
                        if element.startswith('---'):
                            continue
                        mrep = lambda s, d: s if not d else mrep(s.replace(*d.popitem()), d)
                        element = ' '.join(element.split())
                        element = mrep(element, {' GB': '_GB', ' Disk': '_Disk', ' hour': '_hour'})
                        element = element.split(' ')
                        if not sectionHeaders:
                            sectionHeaders.extend(element)
                            continue
                        if len(sectionHeaders) > len(element):
                            for lt in range(0,len(sectionHeaders),1):
                                if sectionHeaders[lt] == 'Port#':
                                    element.insert(lt,'n/a')                              
                        element = [w.replace('_', ' ') for w in element]
                        sectionDatas.append(dict(zip(sectionHeaders, element)))
                    if sectionHeaders and sectionDatas:                     
                        ParsedGroups.append(dict({'header': sectionHeaders, 'data': sectionDatas , 'desc': BlockDescription})) 
                        BlockDescription = None                   
                continue
            stdBlock = self.stdBlockRegex.findall(block)
            if stdBlock:
                blockStyle = 'table'
                blockDatas =dictionary.trim(dict({entry[0] : entry[1] for entry in stdBlock}))
                if len(blockDatas) < 1:
                    continue
                if int(len(blockDatas)) == 1 :
                    singletons.update(blockDatas)
                    continue
                blockHeaders = list(blockDatas.keys())
                Banned = Array.intersect(self.bannedKeys, blockHeaders)
                Allowed = Array.intersect(self.specialKeys, blockHeaders)
                if len(Banned) > 0:
                    continue
                if len(Allowed) > 0:
                    for item in Allowed:
                        specialGroup.update({item:blockDatas.get(item)}) 
                    continue             
                if dictionary.len(blockDatas) > int(self.maxkeys)  and not 'Property' in blockDatas.keys():
                    vblock = dict()
                    vheader = ['Property', 'Value']
                    vdata = []
                    for key, val in blockDatas.items():
                        vdata.append(dict({'Property':key,'Value':val}))
                    vblock.update({
                        'header' : vheader,
                        'data' : vdata , 
                        'desc': stdBlockDescription
                        })
                    ParsedGroups.append(vblock)
                    stdBlockDescription = None                                      
                    continue
                if not ParsedGroups:
                    ParsedGroups.append(dict({'header': blockHeaders, 'data': [blockDatas] , 'desc': stdBlockDescription, 'style': blockStyle}))
                    stdBlockDescription = None 
                    blockStyle = 'table'
                else:
                    groupOffset = 0
                    added = False
                    for group in ParsedGroups:
                        groupdata = group.get('data',list())
                        if not groupdata:
                            continue
                        if sorted(group.get('header')) == sorted(blockHeaders):
                            ParsedGroups[groupOffset] = dict({
                                'header': group.get('header'),
                                'data': groupdata.append(blockDatas) ,
                                'desc': stdBlockDescription, 
                                'style': blockStyle
                            })
                            stdBlockDescription = None 
                            blockStyle = 'table'
                            added = True
                            break
                        groupOffset += 1
                    if not added:
                        ParsedGroups.append(dict({
                            'header': blockHeaders, 
                            'data': [blockDatas] , 
                            'desc': stdBlockDescription, 
                            'style': blockStyle}))
                        stdBlockDescription = None 
                        blockStyle = 'table'
                        added = True
                continue
        if specialGroup:
            spHeaders = list(specialGroup.keys()) 
            ParsedGroups.insert(0, dict({
                'header': spHeaders, 
                'data': [specialGroup],
                'desc': 'System overwiew'
                })) 
        if singletons:
            sHeaders = list(singletons.keys())
            ParsedGroups.append(dict({'header': sHeaders, 'data': [singletons]}))
        return ParsedGroups
    
    def colorize(self, text:str, color:str=None, bold: bool=False)->str:
        if color:
            if not bold:
                sys.stdout.write(ColorObject.normalize(
                    '{reset}{color}{line}{reset}{sep}',
                    color=color,
                    line=text,
                    sep=os.linesep))
            else:
                sys.stdout.write(ColorObject.normalize(
                    '{reset}{bold}{color}{line}{reset}{sep}',
                    color=color,
                    line=text,
                    sep=os.linesep))
            sys.stdout.flush()             
        else:
            if not bold:
                sys.stdout.write(ColorObject.normalize(
                    '{reset}{white}{line}{reset}{sep}',
                    line=text,
                    sep=os.linesep))
            else:
                sys.stdout.write(ColorObject.normalize(
                    '{reset}{bold}{white}{line}{reset}{sep}',
                    line=text,
                    sep=os.linesep))
            sys.stdout.flush() 

    def __renderer(self, data: list, headers: list):
        viewData = list()
        if not headers :
            headers = list(data[0].keys() if data else [])
        viewData.append(headers)
        if isinstance(data,dict):
            viewData.append(list(data.values()))
        else:
            for groupData in data:
                if isinstance(groupData,dict):
                    viewData.append([str(groupData.get(col, None)) for col in list(headers)])
        colwidth = [max(map(len,col))+2 for col in zip(*viewData)]
        for i in  range(0, 2)[::-1]:
            viewData.insert(i, ['-' * i for i in colwidth])
        rowSep = ' '.join(["{{:<{}}}".format(i) for i in colwidth])
        colSep = '-'.join(["{{:<{}}}".format(i) for i in colwidth])
        t=0      
        for item in viewData:
            if not item:
                continue
            if item[0][0] == '-':
                self.colorize(text=colSep.format(*item), color=self.__color)
                continue           
            if t <= 0:
                self.colorize(text=rowSep.format(*item), color=self.__color, bold=True)                 
            else:
                self.colorize(text=rowSep.format(*item))
            t += 1
        self.colorize(text=colSep.format(*['-' * i for i in colwidth]), color=self.__color)

    def render(self):
        for item in self.__data:
            Description = item.get('desc', None)
            itemData = item.get('data', None)
            itemHeaders = item.get('header', None)
            if not itemData:
                continue
            if Description:
                underline = ''
                for j in  range(0, len(Description))[::-1]:
                    underline = underline + '='
                line = os.linesep.join([Description.strip() + ':', underline])  #
                sys.stdout.write(ColorObject.normalize(
                    '{reset}{green}{line}{reset}{sep}',
                    color=self.__color,
                    line=line,
                    sep=os.linesep))
                sys.stdout.flush()    
                for i in  range(0, 1)[::-1]:
                    print()
            style = item.get('style', 'table').lower()
            if style == 'table':
                self.__renderer(data=itemData, headers=itemHeaders)
            else:
                self.__vrenderer(data=itemData)
            for i in  range(0, 2)[::-1]:
                print()
    
    def __vrenderer(self, data: dict):
        
        for groupData in data:
            if isinstance(groupData,dict):
                keywidth = len(max(groupData, key=len))+1
                Valuewidth = len(max(groupData, value=len))+1
                for k,v in groupData.items():
                    kl = len(k)
                    while kl < keywidth:
                        kl += 1
                        k += ' '
                    sys.stdout.write(ColorObject.normalize(
                        '{reset}{color}{key}{tab}{reset}{value}{sep}',
                        color=self.__color,
                        key=k + ':',
                        tab='\t',
                        value=v,
                        sep=os.linesep))
                    sys.stdout.flush()            
            print()

if __name__ == '__main__':
    print('Direct access to {} not allowed'.format(__file__))
    sys.exit(0)
