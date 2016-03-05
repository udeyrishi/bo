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

BO_LAUNCH = 'scrapy crawl bo'
SHUTDOWN_MESSAGE = 'Spider closed (shutdown)'


class BoManager:
    """
    The main manager class for Bo that runs the scrapy crawler as a subprocess repeatedly indefinitely until SIGINT is
    received.
    """

    def __init__(self, launch_command, shutdown_message, logger):
        self.__launch_command = launch_command
        self.__shutdown_message = shutdown_message
        self.__last_output = ''
        self.__sigint_received = False
        self.__bo_pid = None
        self.__logger = logger
        signal.signal(signal.SIGINT, lambda sig, frame: self.sigint_handler(sig, frame))

    def run(self):
        while not self.__sigint_received:
            rc = self.__run_command(self.__launch_command)
            if rc == 0 and self.__last_output.find(self.__shutdown_message) != -1:
                break

        self.__logger.log(logging.INFO, 'Bo successfully shut down')

    def __run_command(self, command):
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, preexec_fn=lambda: os.setpgrp())
        self.__bo_pid = process.pid
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output)
                self.__last_output = output
        return process.poll()

    def sigint_handler(self, sig, frame):
        print('')
        self.__logger.log(logging.INFO, 'SIGINT received. Shutting down scrapy')
        self.__sigint_received = True
        if self.__bo_pid is not None:
            for i in range(2):
                subprocess.call(['kill', '-SIGINT', str(self.__bo_pid)])


def configure_logger():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s [BO MANAGER] [%(name)s] [%(levelname)s]: %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    return root


def main():
    logger = configure_logger()
    bo_manager = BoManager(BO_LAUNCH, SHUTDOWN_MESSAGE, logger)
    bo_manager.run()


if __name__ == '__main__':
    main()
