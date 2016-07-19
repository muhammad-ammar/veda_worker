
import os
import sys

"""
Let's do some quick and dirty error handling & logging

"""

from global_vars import *

"""
Unspecified errors with a message
"""

class ErrorObject(object):

    @staticmethod
    def print_error(message):
        decorator = "***************E*R*R*O*R*******************"
        outgoing = '\n%s \n\n%s \n\n%s\n' % (
            NODE_COLORS_BLUE + decorator + NODE_COLORS_END, 
            message, 
            NODE_COLORS_BLUE + decorator + NODE_COLORS_END, 
            )
        print outgoing



class Output(object):
    """
    Various reporting methods
    """
    @staticmethod
    def _seconds_from_string(duration):

        hours = float(duration.split(':')[0])
        minutes = float(duration.split(':')[1])
        seconds = float(duration.split(':')[2])
        duration_seconds = (((hours * 60) + minutes) * 60) + seconds
        return duration_seconds

    @staticmethod
    def status_bar(process):
        """
        This is a little gross, but it'll get us a status bar thingy

        """
        fps = None
        duration = None
        while True:
            line = process.stdout.readline().strip()

            if line == '' and process.poll() is not None:
                break
            if fps == None or duration == None:
                if "Stream #" in line and " Video: " in line:
                    fps = [s for s in line.split(',') if "fps" in s][0].strip(' fps')

                if "Duration: " in line:
                    dur = line.split('Duration: ')[1].split(',')[0].strip()
                    duration = Output()._seconds_from_string(duration=dur)

            else:
                if 'frame=' in line:
                    cur_frame = line.split('frame=')[1].split('fps=')[0].strip()
                    end_frame = float(duration) * float(fps.strip())
                    pctg = (float(cur_frame) / float(end_frame))
                    sys.stdout.write('\r')
                    i = int(pctg * 20.0)
                    sys.stdout.write("%s : [%-20s] %d%%" % ('Transcode', '='*i, int(pctg * 100)))
                    sys.stdout.flush()
        """
        Just for politeness
        """
        sys.stdout.write('\r')
        sys.stdout.write("%s : [%-20s] %d%%" % ('Transcode', '='*20, 100))
        sys.stdout.flush()




"""Just to sneak a peek"""
def main():
    test_error = "This is a test"
    E1 = ErrorObject.print_error(
        message = test_error, 
        )



if __name__ == '__main__':
    sys.exit(main())

