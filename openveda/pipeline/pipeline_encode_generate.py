
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

from reporting import ErrorObject, TestReport

class CommandGenerate():

    def __init__(self, Settings, VideoObject, EncodeObject):
        self.Settings = Settings
        self.VideoObject = VideoObject
        self.EncodeObject = EncodeObject

        self.ffcommand = None


    def activate(self):
        """
        Generate command for ffmpeg lib
        """
        if self.VideoObject == None:
            ErrorObject(
                method = self,
                message = 'Command Gen Fail\nNo Video Object'
                )

            return False
        if self.EncodeObject == None:
            ErrorObject(
                method = self,
                message = 'Command Gen Fail\nNo Encode Object'
                )

            return False

        """These build the command, and, unfortunately, must be in order"""
        self.call_ffmpeg()
        self.codec_commands()
        if self.Settings.ENFORCE_TARGET_ASPECT is True:
            self.scalar_commands()

        self.determine_bitdepth()
        self.determine_passes()
        self.destination_file()


    def call_ffmpeg(self):
        """
        Begin Command Proper
        """
        self.ffcommand = self.Settings.FFMPEG_COMPILED + " -hide_banner -y -i " + os.path.join(
            self.Settings.VEDA_WORK_DIR, 
            self.VideoObject.mezz_filepath.split('/')[-1]
            )

        if self.EncodeObject.filetype != 'mp3':
            self.ffcommand += ' -c:v '
        else:
            self.ffcommand += ' -c:a '


    def codec_commands(self):
        """
        This, as an addendum to the relatively simple deliverables to edX, is only intended to 
        work with a few filetypes (see config)
        """
        if self.ffcommand == None: return None
        if self.EncodeObject.filetype == "mp4":
            self.ffcommand += "libx264 "
        elif self.EncodeObject.filetype == "webm":
            self.ffcommand += "libvpx "
        elif self.EncodeObject.filetype == "mp3":
            self.ffcommand += "libmp3lame "
        # return True


    def scalar_commands(self):
        # print self.EncodeObject.filetype
        if self.ffcommand == None: return None
        if self.Settings.ENFORCE_TARGET_ASPECT is False: return None
        if self.EncodeObject.filetype == 'mp3': return None

        """
        Padding (if requested and needed)
        letter/pillarboxing Command example: -vf pad=720:480:0:38 
        (target reso, x, y)
        """
        horiz_resolution = int(float(self.EncodeObject.resolution) * self.Settings.TARGET_ASPECT_RATIO)

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
        if mezz_aspect_ratio == None or float(mezz_aspect_ratio) == float(self.Settings.TARGET_ASPECT_RATIO):
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
            self.ffcommand += "-vf scale=" + str(horiz_resolution) + ":" + str(self.EncodeObject.resolution) + " "

        elif aspect_fix is True: # and resolution_fix is False: (not needed)
            if mezz_aspect_ratio > self.Settings.TARGET_ASPECT_RATIO:
                ## LETTERBOX ##
                scalar = (int(self.EncodeObject.resolution) - (horiz_resolution / mezz_aspect_ratio)) / 2
                
                self.ffcommand += "-vf scale=" + str(horiz_resolution) 
                self.ffcommand += ":" + str(int(self.EncodeObject.resolution) - (int(scalar) * 2))
                self.ffcommand += ",pad=" + str(horiz_resolution) + ":" + str(self.EncodeObject.resolution) 
                self.ffcommand += ":0:" + str(int(scalar)) + " "

            if mezz_aspect_ratio < self.Settings.TARGET_ASPECT_RATIO:
                ## PILLARBOX ##
                scalar = (horiz_resolution - (mezz_aspect_ratio * int(self.EncodeObject.resolution))) / 2
                self.ffcommand += "-vf scale=" + str(horiz_resolution - (int(scalar) * 2)) 
                self.ffcommand += ":" + str(self.EncodeObject.resolution)
                self.ffcommand += ",pad=" + str(horiz_resolution) + ":" + str(self.EncodeObject.resolution) 
                self.ffcommand += ":" + str(int(scalar)) + ":0 "


    def determine_bitdepth(self):
        """

        TODO: add tables translating CRF to bitrate,
        some experimenting is needed - a lossless solution
        to low bitdepth videos can be in the offing, but for now,
        stock
        
        """
        return None


    def determine_passes(self):
        """
        Passes / 2 for VBR
        1 for CRF
        1 for WEBM
        """
        if self.EncodeObject.filetype == "webm":
            self.ffcommand += "-b:v "
            if self.EncodeObject.rate_factor > self.VideoObject.mezz_bitrate:
                self.ffcommand += str(self.VideoObject.mezz_bitrate) + "k -minrate 10k -maxrate "
                self.ffcommand += str(int(float(self.VideoObject.mezz_bitrate) * 1.25))
                self.ffcommand += "k -bufsize " + str(int(self.VideoObject.mezz_bitrate) - 24) + "k"
            else:
                self.ffcommand += str(self.EncodeObject.rate_factor) + "k -minrate 10k -maxrate " 
                self.ffcommand += str(int(float(self.EncodeObject.rate_factor) * 1.25))
                self.ffcommand += "k -bufsize " + str(int(self.EncodeObject.rate_factor) - 24) + "k"

        elif self.EncodeObject.filetype == "mp4":
            crf = str(self.EncodeObject.rate_factor)
            self.ffcommand += "-crf " + crf

        elif self.EncodeObject.filetype == "mp3":
            self.ffcommand += "-b:a " + str(self.EncodeObject.rate_factor) + 'k ' 

        """
        for a possiblestate of two-pass encodes : 
        need: two-pass global bool
            ffmpeg -y -i -pass 1 -c:a libfdk_aac -b:a 128k -passlogfile ${LOGFILE} \
            -f mp4 /dev/null && ${FFCOMMAND} -pass 2 -c:a libfdk_aac -b:a 128k ${DESTINATION}
        """


    def destination_file(self):
        
        if self.EncodeObject.filetype == "mp4":
            self.ffcommand +=  " -movflags faststart "

        elif self.EncodeObject.filetype == "webm":
            """This is WEBM = 1 Pass"""
            self.ffcommand += " -c:a libvorbis "

        if self.VideoObject.video_id != None:
            self.ffcommand += os.path.join(
                self.Settings.VEDA_WORK_DIR, 
                self.VideoObject.video_id
                )

        else:
            self.ffcommand += os.path.join(
                self.Settings.VEDA_WORK_DIR, 
                self.VideoObject.mezz_filepath.split('/')[-1].split('.')[0]
                )

        self.ffcommand += "_" + self.EncodeObject.encode_suffix + "." + self.EncodeObject.filetype



def main():
    pass


if __name__ == "__main__":
    sys.exit(main())

