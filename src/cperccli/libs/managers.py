#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
import os
import sys
import subprocess
import shlex

os.setpgrp()

class PackageManager(object):
    def __init__(self) -> None:
        self.__pkginstaler = self.__installer()
    
    def __installer(self)->str:
        knownPkgInstallers = list([
        {'name':'dnf',      'command':'dnf install -y',       },        
        {'name':'yum',      'command':'yum install -y',       },
        {'name':'apt-get',  'command':'apt-get install -y',   },                    
        {'name':'apk',      'command':'apk add --no-cache',   },          
        {'name':'emerge',   'command':'emerge',               },     
        {'name':'pacman',   'command':'pacman -S --noconfirm',},
        {'name':'zypper',   'command':'zypper install',       }
        ])
        
        for pkgInstaller in knownPkgInstallers:
            process = subprocess.run(['which', pkgInstaller.get('name')], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if process.returncode == 0:
                return pkgInstaller.get('command')
        return None

    def getInstaller(self):
        return self.__pkginstaler

class PackageInstaller(PackageManager):
    
    def __init__(self, packages: list=[]) -> None:
        super().__init__()
        self.__packages = list(packages)
    
    def install(self)->bool:
        if self.__packages:
            packages = ' '.join(self.__packages) if isinstance(self.__packages, list) else str(self.__packages)
            command = '{} {}'.format(self.getInstaller(), packages)
            process = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if not process.returncode == 0: 
                return False
        return True

if __name__ == '__main__':
    print('Direct access to {} not allowed'.format(__file__))
    sys.exit(0)
