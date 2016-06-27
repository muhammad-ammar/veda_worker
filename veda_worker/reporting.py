
import os
import sys

"""
Let's do some quick and dirty error handling & logging

"""

from node_config import *

"""
Unspecified errors with a message
"""

class ErrorObject():
    
    def __init__(self, message, method):
        self.message = message
        self.method = method

        """Just run w/o call"""
        if NODE_LOGGING is True:
            self.log_error()
        if NODE_STDIO is True:
            self.print_error()


    def log_error(self):
        pass


    def print_error(self):
        decorator = "***************E*R*R*O*R*******************"
        outgoing = '\n%s \n\n%s \n\n%s \n\n%s\n' % (
            NODE_COLORS_BLUE + decorator + NODE_COLORS_END, 
            self.method, 
            self.message, 
            NODE_COLORS_BLUE + decorator + NODE_COLORS_END, 
            )
        print outgoing


class TestReport():

    def __init__(self, passed, test_name):
        self.passed = passed
        self.test_name = test_name
        self.PASSED_MESSAGE = '[ PASSED ]'
        self.FAILED_MESSAGE = '[ -Failed- ]'

        """
        Simple reporting
        """
        if passed is True:
            message = self.PASSED_MESSAGE
            color = NODE_COLORS_GREEN
        else: 
            message = self.FAILED_MESSAGE
            color = NODE_COLORS_RED

        print '%s : %s %s' % (color + message + NODE_COLORS_END, test_name, '')


class LogFile():
    def __init__(self):
        self.passed = passed
        self.test_name = test_name
        self.PASSED_MESSAGE = '[ PASSED ]'
        self.FAILED_MESSAGE = '[ -Failed- ]'

        pass




"""Just to sneak a peek"""
def main():
    test_error = "This is a test"
    E1 = ErrorObject(
        message = test_error, 
        method = os.path.basename(__file__).split('.')[0]
        )

if __name__ == '__main__':
    sys.exit(main())

