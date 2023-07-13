#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
import os
import sys
import subprocess
sys.path.append(os.getcwd())
from libs import compat, painters, queries, robots, utils
# from libs import builder

os.setpgrp()

class PERCCLIWrapper(object):
    
    def __init__(self, options: list=[], **kwargs) -> None:
        try: 
            # env=builder.envBuilder()
            # env.create()
            # env.activate()
            self.System = compat.SystemValidator(**kwargs)
            if not self.System.isCompliant():
                raise ValueError('Exiting cperccli program!')
            self.__options = options if options else ['help']
            self.__sOptions = ['help','-help','h','-h','v','-v','?']
            self.runner = queries.Runner(command=self.__setPrefix(), options=self.__options, **kwargs)
        except ValueError as e:
            exit(e) 

    def __setPrefix(self, default: str='perccli') -> str:
        daemons = ['perccli64', 'perccli']
        for deamon in daemons:
            process = subprocess.run(['which', deamon], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if process.returncode == 0:
                return str(deamon)
        return default

    def run(self)->str:
        self.runner.start()
        out = self.runner.getResult()
        if len(utils.Array.intersect(self.__sOptions, self.__options)) <= 0:
            parser = robots.PERCParser(data=out)
            return parser.render()
        else:
            namespace = self.__setPrefix()
            sys.stdout.write(out.replace(namespace, painters.ColorObject.normalize(
                '{reset}{color}{line}{reset}',
                color=next(painters.Colors.All()),
                line='c'+ namespace)
            ))

if __name__ == '__main__':

    args = sys.argv
    args.pop(0)
    wrapper = PERCCLIWrapper(options=args)
    wrapper.run()
