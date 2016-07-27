
import os
import sys
import subprocess

"""

Quick QA for video file

will not catch all errors
but will catch ~0.95 of them
@yro / 2016

This should do some basic testing on the intake or generated file:
    - general file test (exists, size > 0)
    - ffmpeg test (compatible, duration > 0)
    - duration test (if not mezz, is equal to mezz)

FUTURE:
    - size/score ratio
    - artifacting?

@yro / 2016

"""
from reporting import ErrorObject, Output
from config import WorkerSetup
WS = WorkerSetup()
if os.path.exists(WS.instance_yaml):
    WS.run()
settings = WS.settings_dict


class ValidateVideo():

    def __init__(self, filepath, VideoObject=None, **kwargs):
        self.filepath = filepath
        self.VideoObject = VideoObject
        self.product_file = kwargs.get('product_file', False)
        self.valid = self.validate()


    def validate(self):
        """
        First: a general file test 
            -size > 0, 
            -file exists
        """
        if not os.path.exists(self.filepath):
            ErrorObject().print_error(
                message = 'File QA fail: File is not found\n' + \
                    self.filepath
                )
            return False
        
        if os.stat(self.filepath).st_size == 0:
            ErrorObject().print_error(
                message = 'File QA fail: Filesize is 0'
                )
            return False

        """
        ffprobe file information
        """
        ffcommand = 'ffprobe -hide_banner '
        ffcommand += '\"' + self.filepath + '\"'

        p = subprocess.Popen(
            ffcommand, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            shell=True
            )

        for line in iter(p.stdout.readline, b''):

            if 'No such file or directory' in line:
                return False

            if 'Invalid data found when processing input' in line:
                return False

            if "multiple edit list entries, a/v desync might occur, patch welcome" in line:
                return False

            if "Duration: " in line:
                """Get and Test Duration"""
                if "Duration: 00:00:00.0" in line:
                    return False
                elif "Duration: N/A, " in line:
                    return False

                vid_duration = line.split('Duration: ')[1].split(',')[0].strip()
                duration = Output._seconds_from_string(duration=vid_duration)

                if duration < 1.05:
                    return False

        try:
            duration
        except:
            return False

        """
        duration test (if not mezz, is equal to mezz)
        """
        if self.VideoObject != None and self.product_file is True:
            ## within five seconds
            if not (self.VideoObject.mezz_duration - 5) <= duration <= (self.VideoObject.mezz_duration + 5):
                return False

        return True



def main():
    pass


if __name__ == '__main__':
    sys.exit(main())

