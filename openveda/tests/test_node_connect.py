
import os
import sys
import subprocess
import time

"""
test connection to celery cluster


"""

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from reporting import ErrorObject, TestReport



class CeleryConnect():

    def __init__(self, Settings):
        self.Settings = Settings

        # self.cel_queue = self.Settings.CELERY_QUEUE
        ####

        self.passed = self.celery_credentials()
        test_name = 'Celery Connection Test'
        self.passed = self.celery_setup_test()
        TestReport(self.passed, test_name)


    def celery_setup_test(self):
        if self.Settings.NODE_VEDA_ATTACH is False:
            return False

        salient_variables = [
            'RABBIT_USER', 
            'RABBIT_PASS', 
            'RABBIT_BROKER',
            'CELERY_APP_NAME'
            ]

        for s in salient_variables:
            if len(eval('self.Settings.' + s)) == 0:
                raise SetupError(
                    method=self,
                    varbls=s
                    )
                return False
        return True

    def celery_credentials(self):
        setup = self.celery_setup_test()
        if setup is False: return False

        ###### This is yuck, but I am in a hurry ######

        os.chdir(os.path.dirname(os.path.dirname(__file__)))
        worker_call = 'python celeryapp.py worker --loglevel=info --concurrency=1 -Q ' + str(self.Settings.CELERY_QUEUE)
        a1 = subprocess.Popen(worker_call, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        print '** 10 sec of sleep while node connects to cluster **'
        time.sleep(10)
        a1.kill() ##Otherwise it's FOREVER

        for line in iter(a1.stdout.readline, b''):
            if 'Connected to amqp://'+self.Settings.RABBIT_USER+':**@'+self.Settings.RABBIT_BROKER+':5672//' in line:
                return True

        ######          ^^^GROSS^^^             ######

        return False


"""
Just for writing and testing
"""
def main():
    from config import Settings
    S1 = Settings(
        node_config = os.path.join(os.path.dirname(__file__), 'settings.py')
        )
    S1.activate()
    CCE1 = CeleryConnect(Settings=S1)


if __name__ == '__main__':
    sys.exit(main())

