#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
import os
import sys
import subprocess
import venv

os.setpgrp()

class envBuilder(object):
    
    def __init__(self, **kwargs) -> None:
        self.__envDir = kwargs.setdefault('envDir', os.path.expanduser('~'))
        self.__envName = kwargs.setdefault('envName','.venv')
        self.__symlinks = kwargs.setdefault('symlinks', False)
        self.__upgrade = kwargs.setdefault('upgrade', False)
        self.__withPip = kwargs.setdefault('withPip', True)
        
    def activate(self):
        '''
        Activate the virtual environment
        '''
        envPath = self.__envPath()
        if os.path.exists(envPath):
            activatePath = os.path.join(envPath, 'bin', 'activate')
            enablerFile = os.path.join(envPath, 'bin', 'enabler.sh')
            if not os.path.exists(enablerFile):
                with open(enablerFile, 'w') as f:
                    f.write('{sheban}{sep}{cmd}'.format(sheban='--!/bin/bash'.replace('--','#'),
                            sep= os.linesep,
                            cmd='. ' + activatePath
                        ))
                    f.close()
                subprocess.call(['chmod', '+x', enablerFile])
            if not self.__isVirtualenv():
                os.system('/bin/bash --rcfile ' + enablerFile)
    
    def create(self):
        '''
        Build virtual environment 
        '''        
        envPath = self.__envPath()
        if not os.path.exists(envPath):
            builder = venv.EnvBuilder(
                system_site_packages=False, 
                clear=True, 
                symlinks=self.__symlinks, 
                upgrade=self.__upgrade, 
                with_pip=self.__withPip
            )
            builder.create(envPath)
    
    def __envPath(self)->str:
        return os.path.join(self.__envDir, self.__envName)
    
    def PipInstall(self, packages)->None:
        '''
        Install python libraries within the activated virtual environment
        '''
        try:
            if self.__isVirtualenv():
                if isinstance(packages, str):
                    packages = packages.split(' ')
                for package in packages:
                    subprocess.call(['pip', 'install', package], cwd=self.__envPath())
        except RuntimeError as e:
            sys.exit(e)

    def __isVirtualenv(self)->str:
        return (self.__basePrefixcompat() != sys.prefix )

    def __basePrefixcompat(self)->str:
        return (getattr(sys,'base_prefix',None) or 
                getattr(sys,'real_prefix',None) or 
                sys.prefix )
        
if __name__ == '__main__':
    print('Direct access to {} not allowed'.format(__file__))
    sys.exit(0)
