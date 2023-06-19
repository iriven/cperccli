#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
import os
import sys
import subprocess
import shlex
import time

os.setpgrp()

class Runner(object):
    
    def __init__(
        self, 
        command: str, 
        options: list=[], 
        silent: bool=False,
        capture: bool=True,
        **kwargs
        ) -> None:
        self.__command = self.__prepareCommand(command, options)
        self.__encoding = kwargs.pop('encoding','unicode_escape')
        self.__silent = silent
        self.__capture = capture
        self.__result = list()

    def __prepareCommand(self, command:str, options: list=[])->list:
        try:      
            if not command:
                raise ValueError('Can not run empty command')
            if isinstance(command,str):
                command = shlex.split(command)
            if options:
                if isinstance(options,str):
                    options = shlex.split(options)
                command.extend(options)
            return command
        except ValueError as e:
            exit(e) 

    def getResult(self)->list: 
        return self.__result
    
    def start(self):
        try:   
            self.__command = ' '.join(self.__command)
            process = subprocess.Popen(
                shlex.split(self.__command), 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                encoding=self.__encoding)
            if self.__capture:
                output, err = process.communicate()
                self.__result = output
                return self.__result
            while True:
                retcode = process.poll()
                line = process.stdout.readline()
                if not line.strip():
                    continue
                if not self.__silent:
                    print(line.strip())
                self.__result.append(line.strip())
                if retcode is not None:
                    break
                else:
                    time.sleep(1)
            process.terminate()
            return self.__result
        except KeyboardInterrupt:
            sys.exit(0)
            
    def checkCommand(self, command)->bool:
        if isinstance(command, str):
            command = command.split(' ')
        for deamon in command:
            process = subprocess.run(['which', deamon], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if process.returncode == 0:
                return True
        return False 


if __name__ == '__main__':
    print('Direct access to {} not allowed'.format(__file__))
    sys.exit(0)
