
import os
import sys

"""
TO BE DELETED


Actual transcode pipeline

"""
from reporting import ErrorObject
from config import WorkerSetup
WS = WorkerSetup()
if os.path.exists(WS.instance_yaml):
    WS.run()
settings = WS.settings_dict



# from reporting import ErrorObject
# from abstractions import AbstractionLayer, Encode
# from config import Settings
# import generate_apitoken

# sys.path.append(os.path.join(os.path.dirname(__file__), 'pipeline'))
# from pipeline_ingest import Ingest
# from pipeline_qa import QAVideo
# from pipeline_val import VALData
# from pipeline_veda import VEDAData
# from pipeline_encode_generate import CommandGenerate
# from pipeline_encode_execute import CommandExecute
# from pipeline_deliver import Deliverable


class Pipeline():

    def __init__(self, video_id, **kwargs):
        # self.Settings = Settings

        """can be ID or full filepath"""
        # self.mezz_video = mezz_video
        self.encode_profile = kwargs.get('encode_profile', None)
        # self.encode_library = kwargs.get('encode_library', None)

        # self.AbstractionLayer = AbstractionLayer()
        # self.ingest = False
        # self.hotstore = False
        # self.passing = False


    def activate(self):
        """
        TODO: Make this fail if a false is returned
        """
        # self._CONFIG()
        # self._INGEST()
        # self.AbstractionLayer.valid = self._QA(mezz_file=True)
        # """
        # Update API Video Status
        # """
        # self.AbstractionLayer.VideoObject.valid = self.AbstractionLayer.valid
        # self._UPDATE_API()
        """
        Generate and Fire Encode
        """
        # self._GENERATE_ENCODES()
        # self._EXECUTE_ENCODES()
        """
        QA and Deliver Files
        """
        # for E in self.AbstractionLayer.Encodes:
        #     Q1 = QAVideo(
        #         filepath=E.output_file, 
        #         VideoObject=self.AbstractionLayer.VideoObject,
        #         mezz_file=False
        #         )
        #     """
        #     This should continue, even if one file is missing
        #     """
        #     E.complete = Q1.activate()

        for E in self.AbstractionLayer.Encodes:
            E.delivered = self._DELIVER_FILE(E)

        """
        determine completion, send final data
        """
        self.AbstractionLayer.complete = True
        for E in self.AbstractionLayer.Encodes:
            if E.complete is False:
                self.AbstractionLayer.complete = False

        self.AbstractionLayer.delivered = True
        for E in self.AbstractionLayer.Encodes:
            if E.delivered is False:
                self.AbstractionLayer.delivered = False
    
        for E in self.AbstractionLayer.Encodes:
            self._UPDATE_API(E)        

        return self.AbstractionLayer.delivered


    # def _CONFIG(self):
    #     """
    #     Clean This up 
    #     """
    #     if len(self.Settings.MEZZ_INGEST_LOCATION) > 0:
    #         self.ingest = True
    #     if len(self.Settings.MEZZ_HOTSTORE_LOCATION) > 0:
    #         self.hotstore = True


    # def _INGEST(self):

    #     FI = Ingest(
    #         Settings = self.Settings, 
    #         mezz_video=self.mezz_video,
    #         hotstore=self.hotstore,
    #         ingest=self.ingest
    #         )
    #     FI.activate()
    #     self.AbstractionLayer.VideoObject = FI.VideoObject


    # def _QA(self, mezz_file):

    #     QA = QAVideo(
    #         filepath=self.AbstractionLayer.VideoObject.mezz_filepath, 
    #         VideoObject=self.AbstractionLayer.VideoObject,
    #         mezz_file=mezz_file
    #         )
    #     return QA.activate()


    # def _UPDATE_API(self, E=None):

    #     if self.Settings.VAL_ATTACH is True:
    #         V1 = VALData(
    #             Settings=self.Settings,
    #             VideoObject=self.AbstractionLayer.VideoObject, 
    #             EncodeObject=E
    #             ).activate()

    #     if self.Settings.NODE_VEDA_ATTACH is True:
    #         V2 = VEDAData(
    #             video_status=True,
    #             Settings=self.Settings,
    #             VideoObject=self.AbstractionLayer.VideoObject, 
    #             EncodeObject=E
    #             ).activate()


    # def _GENERATE_ENCODES(self):
    #     """
    #     Generate the (shell) command / Encode Object
    #     and tack it into the AbstractionLayer Object
    #     """
    #     if self.Settings.NODE_VEDA_ATTACH is True \
    #     and self.encode_profile is None:
    #         ErrorObject(
    #             method = self,
    #             message = 'Encode Gen Fail\nNo Encode Profile'
    #             )
    #         return False

    #     if self.Settings.NODE_VEDA_ATTACH is True:
    #         """
    #         If this is a VEDA-Attached Node, it'll only receive one enc command
    #         """
    #         E1 = Encode(
    #             Settings = self.Settings,
    #             VideoObject = self.AbstractionLayer.VideoObject,
    #             profile_name = self.encode_profile
    #             )
    #         E1.activate()
    #         self.AbstractionLayer.Encodes.append(E1)
    #     else:
    #         """
    #         Get all the NODE_ENCODE_PROFILES from node_config
    #         """
    #         for key, entry in self.Settings.NODE_ENCODE_PROFILES.iteritems():
    #             E1 = Encode(
    #                 Settings = self.Settings,
    #                 VideoObject = self.AbstractionLayer.VideoObject,
    #                 profile_name = key
    #                 )
    #             E1.activate()
    #             self.AbstractionLayer.Encodes.append(E1)

    #     for E in self.AbstractionLayer.Encodes:
    #         CG = CommandGenerate(
    #             Settings = self.Settings,
    #             VideoObject = self.AbstractionLayer.VideoObject,
    #             EncodeObject = E
    #             )
    #         CG.activate()
    #         E.ffcommand = CG.ffcommand

    #     for E in self.AbstractionLayer.Encodes:
    #         if E.ffcommand == None:
    #             ErrorObject(
    #                 method = self,
    #                 message = 'Encode Gen Fail\nCommand Gen Fail'
    #                 )
    #             return False

    #     return True


    # def _EXECUTE_ENCODES(self):
        # """
        # Run the commands, which tests for a file and returns
        # a bool and the filename
        # """
        # for E in self.AbstractionLayer.Encodes:
        #     FF = CommandExecute(
        #         ffcommand = E.ffcommand, 
        #         )
        #     E.complete = FF.activate()
        #     E.output_file = FF.output
        #     """just polite"""
        #     print('')
        #     """"""
        #     if E.complete is False:
        #         return False
        
        # self.AbstractionLayer.complete = True
        # return True


    # def _DELIVER_FILE(self, E):
        # if not os.path.exists(E.output_file):
        #     return False
        # if E.complete is False:
        #     return False
        # """
        # Deliver Here
        # """
        # # if len(self.Settings.DELIVERY_ENDPOINT) > 0:
        # D1 = Deliverable(
        #     Settings=self.Settings,
        #     VideoObject=self.AbstractionLayer.VideoObject, 
        #     EncodeObject=E
        #     )
        # passed = D1.activate()
        # # else:
        #     # passed = True

        # if passed is False: 
        #     return False
            
        # E.upload_filesize = D1.upload_filesize
        # E.hash_sum = D1.hash_sum
        # E.endpoint_url = D1.endpoint_url
        # return True



def main():
    pass


if __name__ == '__main__':
    sys.exit(main())

