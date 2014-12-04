#  Copyright 2008-2014 Nokia Solutions and Networks
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from contextlib import contextmanager
import logging

from robot import utils

from . import librarylogger


LEVELS = {'TRACE': logging.NOTSET,
          'DEBUG': logging.DEBUG,
          'INFO': logging.INFO,
          'WARN': logging.WARNING}


# TODO: Remove in RF 2.9 because register_handler used instead since 2.8.7.
# https://github.com/robotframework/robotframework/issues/1821
def initialize(level):
    logging.raiseExceptions = False
    logging.getLogger().addHandler(RobotHandler())
    set_level(level)


@contextmanager
def register_handler(level, handler=None):
    root = logging.getLogger()
    handler = handler or RobotHandler()
    old_raise = logging.raiseExceptions
    root.addHandler(handler)
    logging.raiseExceptions = False
    set_level(level)
    try:
        yield
    finally:
        root.removeHandler(handler)
        logging.raiseExceptions = old_raise


def set_level(level):
    try:
        level = LEVELS[level.upper()]
    except KeyError:
        return
    logging.getLogger().setLevel(level)


class RobotHandler(logging.Handler):

    def emit(self, record):
        message, error = self._get_message(record)
        method = self._get_logger_method(record.levelno)
        method(message)
        if error:
            librarylogger.debug(error)

    def _get_message(self, record):
        try:
            return record.getMessage(), None
        except:
            message = 'Failed to log following message properly: %s' \
                        % utils.unic(record.msg)
            error = '\n'.join(utils.get_error_details())
            return message, error

    def _get_logger_method(self, level):
        if level >= logging.WARNING:
            return librarylogger.warn
        if level >= logging.INFO:
            return librarylogger.info
        if level >= logging.DEBUG:
            return librarylogger.debug
        return librarylogger.trace