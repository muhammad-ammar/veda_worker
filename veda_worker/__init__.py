
import os
import sys
import argparse

"""
Generate a serial transcode stream from either an 
open edx studio instance upload or VEDA instance via Celery

"""
from reporting import ErrorObject, TestReport
from config import Settings
from pipeline import Pipeline

class OpenVeda():

    def __init__(self, veda_id, **kwargs):
        """
        Init settings / 
        """
        self.workdir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'VEDA_WORKING'
            )
        self.veda_id = veda_id
        self.mezz_video = kwargs.get('mezz_video', None)
        
        # kwargs.get('mezz_video', None)
        # workdir = kwargs.get('workdir', os.path.join(os.getcwd(), 'VEDA_WORKING'))
        # settings_file = kwargs.get('settings_file', None)

        # self.mezz_video = 
        # encode_library = kwargs.get('encode_library', None)
        # # self.encode_profile = kwargs.get('encode_profile', None)
        # self.Settings = Settings(
        #     node_config=settings_file, 
        #     encode_library=encode_library
        #     )
        # self.Settings.activate()




        # self.Pipeline = None
        ## Yeah, I know
        # for key, value in kwargs.items():
            # if key != 'settings':
                # setattr(self.Settings, key, value)


    def activate(self):
        """
        First some basic kwarg checking, then we're off to the races
        """
        if self.mezz_video == None:
            raise ErrorObject(
                message = 'No File Specified',
                method = self,
                )
            return None

        if self.Settings.NODE_VEDA_ATTACH is True and self.encode_profile is None:
            raise ErrorObject(
                message = 'No Encode Profile Specified',
                method = self,
                )
            return None

        if self.Settings.NODE_VEDA_ATTACH is True:
            """
            For a node attached instance
            """
            self.Pipeline = Pipeline(
                Settings=self.Settings,
                mezz_video=self.mezz_video,
                encode_profile=self.encode_profile
                )
            self.Pipeline.activate()
            return None
        else:
            """
            Single stream
            """
            self.Pipeline = Pipeline(
                Settings=self.Settings,
                mezz_video=self.mezz_video
                )
            self.Pipeline.activate()
            return None


    def test(self):
        """
        Run end-to-end test of openveda config
        """
        sys.path.append(os.path.join(os.path.dirname(__file__), 'tests'))
        import test_end_to_end
        test_end_to_end.main(
            Settings=self.Settings, 
            mezz_video=self.mezz_video
            )


    def complete(self):
        """
        Determine, reportback completion
        """
        TestReport(self.Pipeline.AbstractionLayer.complete, 'Complete')
        TestReport(self.Pipeline.AbstractionLayer.delivered, 'Delivered')

        if self.Pipeline.AbstractionLayer.complete is True and \
        self.Pipeline.AbstractionLayer.delivered is True:
            return True
        else:
            return False



def main():
    pass

if __name__ == '__main__':
    sys.exit(main())

