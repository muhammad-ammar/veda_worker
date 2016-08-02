
import os
import sys

"""
alg. to determine ffmpeg command based on video and encode information

-resolution (frame size)
-CRF (increase for lower bitrate videos)

This is built to generate commands for a very small number of encodes and is not a substitute 
for knowledgable use of ffmpeg if one's intention is to broaden use beyond the very limited set of 
endpoints the edX platform provides

input, via two classes, encode and video, which can be generated either via the node independently
or via celery connection to VEDA (VEDA will send video_id and encode_profile via Celery queue)

"""
from global_vars import *
from reporting import ErrorObject, Output
from config import WorkerSetup
WS = WorkerSetup()
if os.path.exists(WS.instance_yaml):
    WS.run()
settings = WS.settings_dict




class CommandGenerate():

    def __init__(self, VideoObject, EncodeObject, **kwargs):
        self.VideoObject = VideoObject
        self.EncodeObject = EncodeObject
        self.jobid = kwargs.get('jobid', None)
        self.ffcommand = []

        if self.jobid is None:
            self.workdir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'VEDA_WORKING'
                )
        else:
            self.workdir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'VEDA_WORKING',
                self.jobid
                )

        # self.workdir = os.path.join(
        #     os.path.dirname(
        #         os.path.dirname(os.path.abspath(__file__))
        #         ),
        #     'VEDA_WORKING'
        #     )


    def generate(self):
        """
        Generate command for ffmpeg lib
        """
        if self.VideoObject == None:
            ErrorObject().print_error(
                message = 'Command Gen Fail: No Video Object'
                )

            return None
        if self.EncodeObject == None:
            ErrorObject().print_error(
                message = 'Command Gen Fail: No Encode Object'
                )

            return None
        """
        These build the command, and, unfortunately, must be in order
        """
        self._call()
        self._codec()

        if ENFORCE_TARGET_ASPECT is True:
            self._scalar()

        self._bitdepth()
        self._passes()
        self._destination()
        return " ".join(self.ffcommand)


    def _call(self):
        """
        Begin Command Proper
        """
        self.ffcommand.append(settings['ffmpeg_compiled'])
        self.ffcommand.append("-hide_banner")
        self.ffcommand.append("-y")
        self.ffcommand.append("-i")
        self.ffcommand.append(os.path.join(
            self.workdir, 
            '.'.join((
                self.VideoObject.veda_id, 
                self.VideoObject.mezz_extension
                ))
            ))

        if self.EncodeObject.filetype != 'mp3':
            self.ffcommand.append("-c:v")
        else:
            self.ffcommand.append("-c:a")


    def _codec(self):
        """
        This, as an addendum to the relatively simple deliverables to edX, is only intended to 
        work with a few filetypes (see config)
        """
        if self.ffcommand == None: return None

        if self.EncodeObject.filetype == "mp4":
            self.ffcommand.append("libx264")
        elif self.EncodeObject.filetype == "webm":
            self.ffcommand.append("libvpx")
        elif self.EncodeObject.filetype == "mp3":
            self.ffcommand.append("libmp3lame")


    def _scalar(self):
        if self.ffcommand == None: return None
        if ENFORCE_TARGET_ASPECT is False: return None
        if self.EncodeObject.filetype == 'mp3': return None

        """
        Padding (if requested and needed)
        letter/pillarboxing Command example: -vf pad=720:480:0:38 
        (target reso, x, y)
        """
        horiz_resolution = int(float(self.EncodeObject.resolution) * TARGET_ASPECT_RATIO)

        """BITRATE as int"""
        if self.VideoObject.mezz_bitrate != 'Unparsed' and len(self.VideoObject.mezz_bitrate) > 0:
            mezz_parse_bitrate = self.VideoObject.mezz_bitrate.strip().split(' ')[0]
        else:
            mezz_parse_bitrate = None
        """RESOLUTION as int"""
        if self.VideoObject.mezz_resolution != 'Unparsed' and len(self.VideoObject.mezz_resolution) > 0:
            mezz_vert_resolution = int(self.VideoObject.mezz_resolution.strip().split('x')[1])
            mezz_horiz_resolution = int(self.VideoObject.mezz_resolution.strip().split('x')[0])
        else:
            mezz_vert_resolution = None
            mezz_horiz_resolution = None
        """Aspect Ratio as float"""
        if mezz_vert_resolution != None and mezz_horiz_resolution != None:
            mezz_aspect_ratio = float(mezz_horiz_resolution) / float(mezz_vert_resolution)
        else:
            mezz_aspect_ratio = None

        """Append commands"""
        ##let's make this a little cleaner than it was
        if mezz_aspect_ratio == None or float(mezz_aspect_ratio) == float(TARGET_ASPECT_RATIO):
            aspect_fix = False
        elif mezz_vert_resolution == 1080 and mezz_horiz_resolution == 1440:
            aspect_fix = False
        else:
            aspect_fix = True

        if int(self.EncodeObject.resolution) == int(mezz_vert_resolution):
            resolution_fix = False
        else:
            resolution_fix = True

        if aspect_fix is False and resolution_fix is False:
            return None

        if aspect_fix is False and resolution_fix is True:
            self.ffcommand.append("-vf")
            self.ffcommand.append("scale=" + str(horiz_resolution) + ":" + str(self.EncodeObject.resolution))

        elif aspect_fix is True:
            if mezz_aspect_ratio > self.Settings.TARGET_ASPECT_RATIO:
                ## LETTERBOX ##
                scalar = (int(self.EncodeObject.resolution) - (horiz_resolution / mezz_aspect_ratio)) / 2
                
                self.ffcommand.append("-vf")
                scalar_command = "scale=" + str(horiz_resolution)
                scalar_command += ":" + str(int(self.EncodeObject.resolution) - (int(scalar) * 2))
                scalar_command += ",pad=" + str(horiz_resolution) + ":" + str(self.EncodeObject.resolution) 
                scalar_command += ":0:" + str(int(scalar))
                self.ffcommand.append(scalar_command)


            if mezz_aspect_ratio < self.Settings.TARGET_ASPECT_RATIO:
                ## PILLARBOX ##
                scalar = (horiz_resolution - (mezz_aspect_ratio * int(self.EncodeObject.resolution))) / 2

                self.ffcommand.append("-vf")
                scalar_command = "scale=" + str(horiz_resolution - (int(scalar) * 2)) 
                scalar_command += ":" + str(self.EncodeObject.resolution)
                scalar_command += ",pad=" + str(horiz_resolution) + ":" + str(self.EncodeObject.resolution) 
                scalar_command += ":" + str(int(scalar)) + ":0"
                self.ffcommand.append(scalar_command)


    def _bitdepth(self):
        """
        TODO: add tables translating CRF to bitrate,
        some experimenting is needed - a lossless solution
        to low bitdepth videos can be in the offing, but for now,
        stock
        
        """
        return None


    def _passes(self):
        """
        Passes / 2 for VBR
        1 for CRF
        1 for WEBM
        """
        if self.EncodeObject.filetype == "webm":
            self.ffcommand.append("-b:v")
            if self.EncodeObject.rate_factor > self.VideoObject.mezz_bitrate:
                self.ffcommand.append(str(self.VideoObject.mezz_bitrate) + "k")
                self.ffcommand.append("-minrate")
                self.ffcommand.append("10k")
                self.ffcommand.append("-maxrate")
                self.ffcommand.append(str(int(float(self.VideoObject.mezz_bitrate) * 1.25)) + "k")
                self.ffcommand.append("-bufsize")
                self.ffcommand.append(str(int(self.VideoObject.mezz_bitrate) - 24) + "k")
            else:
                self.ffcommand.append(str(self.EncodeObject.rate_factor) + "k")
                self.ffcommand.append("-minrate")
                self.ffcommand.append("10k")
                self.ffcommand.append("-maxrate")
                self.ffcommand.append(str(int(float(self.EncodeObject.rate_factor) * 1.25)) + "k")
                self.ffcommand.append("-bufsize")
                self.ffcommand.append(str(int(self.EncodeObject.rate_factor) - 24) + "k")

        elif self.EncodeObject.filetype == "mp4":
            crf = str(self.EncodeObject.rate_factor)
            self.ffcommand.append("-crf")
            self.ffcommand.append(crf)

        elif self.EncodeObject.filetype == "mp3":
            self.ffcommand.append("-b:a")
            self.ffcommand.append(str(self.EncodeObject.rate_factor) + "k")

        """
        for a possible state of two-pass encodes : 
        need: two-pass global bool
            ffmpeg -y -i -pass 1 -c:a libfdk_aac -b:a 128k -passlogfile ${LOGFILE} \
            -f mp4 /dev/null && ${FFCOMMAND} -pass 2 -c:a libfdk_aac -b:a 128k ${DESTINATION}
        """


    def _destination(self):
        
        if self.EncodeObject.filetype == "mp4":
            self.ffcommand.append("-movflags")
            self.ffcommand.append("faststart")

        elif self.EncodeObject.filetype == "webm":
            """This is WEBM = 1 Pass"""
            self.ffcommand.append("-c:a")
            self.ffcommand.append("libvorbis")

        self.ffcommand.append(
            os.path.join(
                self.workdir,
                self.VideoObject.veda_id + "_" + self.EncodeObject.encode_suffix + "." + self.EncodeObject.filetype
                )
            )



def main():
    pass


if __name__ == "__main__":
    sys.exit(main())
