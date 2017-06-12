
import os
import subprocess
import sys

from reporting import ErrorObject, Output
from config import WorkerSetup

"""

Quick QA for video file

will not catch all errors
but will catch ~0.95 of them

This should do some basic testing on the intake or generated file:
    - general file test (exists, size > 0)
    - ffmpeg test (compatible, duration > 0)
    - duration test (if not mezz, is equal to mezz)

FUTURE:
    - size/score ratio
    - artifacting?

"""
WS = WorkerSetup()
if os.path.exists(WS.instance_yaml):
    WS.run()
settings = WS.settings_dict


class ValidateVideo:

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
                message='File QA fail: File is not found\n' + self.filepath
            )
            return False

        if os.stat(self.filepath).st_size == 0:
            ErrorObject().print_error(
                message='File QA fail: Filesize is 0'
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
            print line
            if 'No such file or directory' in line:
                return False

            if 'Invalid data found when processing input' in line:
                return False

            if "multiple edit list entries, a/v desync might occur, patch welcome" in line:
                print 1
                return False

            if "Duration: " in line:
                """Get and Test Duration"""
                if "Duration: 00:00:00.0" in line:
                    print 2
                    return False
                elif "Duration: N/A, " in line:
                    print 3
                    return False

                vid_duration = line.split('Duration: ')[1].split(',')[0].strip()
                duration = Output.seconds_from_string(duration=vid_duration)

                if duration < 1.05:
                    print 'TOO SHORT'
                    return False

        try:
            duration
        except:
            print 'NO DUR'
            return False

        """
        duration test (if not mezz, is equal to mezz)
        """
        if self.VideoObject is not None and self.product_file is True:
            # within five seconds
            if not (self.VideoObject.mezz_duration - 5) <= duration <= (self.VideoObject.mezz_duration + 5):
                print 6
                return False

        return True

    def get_video_attributes(self):
        return_dict = {}
        """
        First: a general file test
            -size > 0,
            -file exists
        """
        if not os.path.exists(self.filepath):
            ErrorObject().print_error(
                message='File Vars fail: File is not found\n' + self.filepath
            )
            return None
        # Filesize
        return_dict.setdefault('duration', os.stat(self.filepath).st_size)

        # ffprobe file information
        ffcommand = 'ffprobe -hide_banner '
        ffcommand += '\"' + self.filepath + '\"'

        p = subprocess.Popen(
            ffcommand,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True
        )

        for line in iter(p.stdout.readline, b''):
            if "Duration: " in line:
                # Get duration
                if "Duration: 00:00:00.0" in line:
                    return False
                elif "Duration: N/A, " in line:
                    return False

                vid_duration = line.split('Duration: ')[1].split(',')[0].strip()
                return_dict.setdefault(
                    'duration',
                    Output.seconds_from_string(duration=vid_duration),
                )
            elif "Stream #" in line and 'Video: ' in line:
                # Resolution
                codec_array = line.strip().split(',')

                for c in codec_array:
                    if len(c.split('x')) == 2 and '/' not in c.split('x')[0]:
                        if '[' not in c:
                            return_dict.setdefault(
                                'resolution',
                                c.strip()
                            )
                        else:
                            return_dict.setdefault(
                                'resolution',
                                c.strip().split(' ')[0]
                            )
        return return_dict


def main():
    pass


if __name__ == '__main__':
    sys.exit(main())
