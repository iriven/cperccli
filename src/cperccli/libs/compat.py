#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
import os
import sys
import shlex
import subprocess
import platform
sys.path.append(os.getcwd())

os.setpgrp()

class PackageVersion(object):
    
    def __init__(self, **kwargs) -> None:
        kwargs.setdefault('python',None)
        self.expected = {
            'version': kwargs.get('legacy', kwargs.get('python')),
        }
    
    def __normalize(self, version: str)->list:
        parts = [int(x) for x in version.split('.')]
        while parts[-1] == 0:
            parts.pop()
        return parts

    def compare(self, version: str, legacy: str=None, match: bool=False)->bool:
        legacy = legacy if not legacy is None else self.expected.get('version')
        if match:
            return bool((self.__normalize(version) == self.__normalize(legacy)))
        return bool((self.__normalize(version) >= self.__normalize(legacy)))
    
class Package(object):
    def __init__(self, **kwargs) -> None:
        self.expected = {
            'package': kwargs.get('package', None),
            'pkg_version': kwargs.get('pkg_version', None),
            'pkg_minversion': kwargs.get('pkg_minversion', None),
        }

    def __isInstalled(self)->bool:
        if not self.expected.get('package'):
            return False
        process = subprocess.Popen(
            ['rpm', '-qa', self.expected.get('package').lower()], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            encoding='unicode_escape')
        output, err = process.communicate()           
        if output:
            return True
        return False
    
    def isCompliant(self)->bool:
        return self.__isInstalled()
    
class PythonLibrary(object):
    def __init__(self, **kwargs) -> None:
        self.expected = {
            'py_version': kwargs.get('py_version', None),
            'py_minversion': kwargs.get('py_minversion', '3.6'),
        }
        
    def __getVersion(self)->dict:
        return platform.python_version()
    
    def isCompliant(self)->bool:
        versionManager = PackageVersion(legacy=self.expected.get('py_minversion'))
        if self.expected.get('py_version'):
            versionManager = PackageVersion(legacy=self.expected.get('py_version'))
            return versionManager.compare(self.__getVersion(), match=True)
        return versionManager.compare(self.__getVersion())
        

class OperatingSystem(object):
    def __init__(self, **kwargs) -> None:
        self.expected = {
            'os': kwargs.get('os', 'linux')
        }
    
    def __Name(self):
        return platform.system()

    def __getArchitechture(self)->str:
        return list(platform.architecture()).pop(0)  

    def is64Bits(self)->bool:
        if self.__getArchitechture().startswith('64'):
            return True
        return False

    def isCompliant(self)->bool:
        if not self.__Name().lower().startswith(self.expected.get('os').lower()) :
            return False
        return True
        

class Manufacturer(object):
    def __init__(self, **kwargs) -> None:
        self.expected = {
            'manufacturer': kwargs.get('manufacturer', 'dell'),
        }
        self.os = platform.system()
        
    def __Name(self)->str:
        command = 'wmic computersystem get manufacturer' if self.os in ['Windows','nt'] else 'dmidecode -s system-manufacturer'
        process = subprocess.Popen(shlex.split(command), 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            encoding='unicode_escape')
        output, err = process.communicate()
        if self.os in ['Windows','nt']:
            output = output.strip().splitlines()
            return output[2]
        return output

    def isCompliant(self)->bool:
        if not self.__Name().lower().startswith(self.expected.get('manufacturer').lower()) :
            return False
        return True
    
    def getName(self):
        return self.__Name()

class SystemValidator(object):
    def __init__(self, **kwargs) -> None:
        kwargs.setdefault('os', 'linux')
        kwargs.setdefault('os_distribution', 'redhat')
        kwargs.setdefault('manufacturer','dell')
        kwargs.setdefault('package', 'perccli')
        kwargs.setdefault('py_minversion', '3.6') 
        kwargs.setdefault('pkg_minversion', '7.0')
        self.Python             = PythonLibrary(**kwargs)
        self.Manufacturer       = Manufacturer(**kwargs)        
        self.OperatingSystem    = OperatingSystem(**kwargs)
        self.RequiredPackage    = Package(**kwargs)
            
    def isCompliant(self)->bool:
        try: 
            if not self.Manufacturer.isCompliant() :
                raise ValueError('This Program is designed for "' + self.Manufacturer.expected.get('manufacturer')  + '" servers only')             
            if not self.OperatingSystem.isCompliant():
                raise ValueError('This Program is designed for "' + self.OperatingSystem.expected.get('os')  + '" servers only') 
            if not self.Python.isCompliant() :
                raise ValueError('This Program need at least Python ' + self.Python.expected.get('py_minversion') + ' to run properly')
            if not self.RequiredPackage.isCompliant() :
                raise ValueError('You must install ' + self.RequiredPackage.expected.get('package') + ' before using this program.')  
            return True
        except ValueError as e:
            print(e)
            return False
        
if __name__ == '__main__':
    print('Direct access to {} not allowed'.format(__file__))
    sys.exit(0)

