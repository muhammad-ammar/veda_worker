
import os
import sys
import unittest

"""
test Encode Abstraction and Command Gen 

"""
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
from reporting import ErrorObject
from config import WorkerSetup


class Test_Encode_Command(unittest.TestCase)

    def setUp(self):
        self.WS = WorkerSetup()
        if os.path.exists(self.WS.instance_yaml):
            self.WS.run()
        self.settings = self.WS.settings_dict
        self.encode_profile = 'desktop_mp4'



    def test_generate_command(self):
        if not os.path.exists(self.WS.instance_yaml):
            self.assertTrue(True)
            return None

        """
        Generate the (shell) command / Encode Object
        """
        VW = VedaWorker(
            veda_id='XXXXXXXX2016-V00TEST', 
            encode_profile='desktop_mp4'
            )

        VW.VideoObject = Video(
            veda_id=self.veda_id
            )
        self.VideoObject.activate()
        self.assertTrue(self.VideoObject.valid is True)

        """
        Pipeline Steps :
          I. Intake
            Ib. Validate Mezz
          II. change status in APIs
          III. Generate Encode Command
          IV. Execute Encodes
            IVa. Validate Products
          (*)V. Deliver Encodes (sftp and others?), retrieve URLs
          (*)VI. Change Status in APIs, add URLs
          VII. Clean Directory

        """
        self._ENG_INTAKE()
        self.assertTrue(self.VideoObject.valid is True)

        self._GENERATE_ENCODE()



        # print VW.test()
        # VW.run()
        # V = VideoObject()

        # E = Encode(
            # VideoObject=self.VideoObject,
            # profile_name=self.encode_profile
            # )
        # E.pull_data()
        # print E.filetype