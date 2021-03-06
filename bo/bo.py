#!/usr/bin/env python

"""
Copyright 2016 Udey Rishi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import subprocess
import signal
import logging
import sys
import os
from threading import Timer
from time import sleep

from bo.settings import BO_MANAGER_SETTINGS

BO_LAUNCH_COMMAND = 'scrapy crawl bo'


class BoManager:
    """
    The main manager class for Bo that runs the scrapy crawler as a subprocess repeatedly indefinitely until SIGINT is
    received.
    """

    def __init__(self, logger, force_kill_delay_seconds=10):
        self.__last_output = ''
        self.__sigint_received = False
        self.__bo_pid = None
        self.__logger = logger
        self.__final_kill_timer = Timer(force_kill_delay_seconds, self.__force_kill_bo)
        self.__killed = False
        signal.signal(signal.SIGINT, lambda sig, frame: self.__sigint_handler(sig, frame))

    def run(self):
        while not self.__sigint_received:
            self.__logger.log(logging.CRITICAL, 'Starting Bo...')
            rc = self.__run_command(BO_LAUNCH_COMMAND)
            if rc == 0:
                if self.__sigint_received:
                    break

                delay = BO_MANAGER_SETTINGS.get('retry_delay_seconds', 10)
                self.__logger.log(logging.CRITICAL, 'Restarting Bo in {0} seconds...'.format(delay))
                sleep(delay)
            else:
                break

        # Cancel the SIGINT call if properly terminated
        self.__final_kill_timer.cancel()
        self.__logger.log(logging.CRITICAL, 'Bo successfully shut down')

    def __run_command(self, command):
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, preexec_fn=os.setpgrp)
        self.__bo_pid = process.pid
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output)
                self.__last_output = output
        return process.poll()

    def __sigint_handler(self, sig, frame):
        if not self.__killed:
            self.__killed = True
            self.__logger.log(logging.CRITICAL, 'SIGINT received. Shutting down scrapy')
            self.__sigint_received = True
            if self.__bo_pid is not None:
                self.__kill_bo()
                self.__final_kill_timer.start()

    def __force_kill_bo(self):
        self.__logger.log(logging.CRITICAL, 'Scrapy shut down not responding. Trying force kill')
        self.__kill_bo()

    def __kill_bo(self):
        subprocess.call(['kill', '-SIGINT', str(self.__bo_pid)])


def configure_logger():
    root = logging.getLogger()
    root.setLevel(logging.getLevelName(BO_MANAGER_SETTINGS.get('log_level')))
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s [BO MANAGER] [%(name)s] [%(levelname)s]: %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    return root


def main():
    logger = configure_logger()
    bo_manager = BoManager(logger, BO_MANAGER_SETTINGS.get('force_kill_delay_seconds', 10))
    bo_manager.run()


if __name__ == '__main__':
    main()
