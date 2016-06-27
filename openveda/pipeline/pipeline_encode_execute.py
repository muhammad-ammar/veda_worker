
import os
import sys
from time import sleep
import subprocess

"""
Handling to actually run ffmpeg, collect data, and log approprately

- i made this class as dumb as possible, but that might not be the right answer
at any rate, all it really takes in is the command and it tries to run it against ffmpeg

TODO: Error finding and handling for actual execution step (which is buried in the subprocess)
TODO: A display during encoding that isn't dumb

LATER: fork ffmpeg and actually tap into the cpp
"""

root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(root_dir)
from reporting import ErrorObject


class CommandExecute():

    def __init__(self, ffcommand, **kwargs):
        self.ffcommand = ffcommand
        self.source = None
        self.output = None
        self.fps = None
        self.duration = None
        ##KWARGS
        self.show_progress = kwargs.get('show_progress', True)


    def activate(self):
        files_array = [f for f in self.ffcommand.split(' ') if '/' in f]
        self.source = files_array[0]
        self.output = files_array[1]

        """
        if this is just a filepath, this should just work
        --no need to move the source--
        """
        if not os.path.exists(self.source):
            return False

        process = subprocess.Popen(
            self.ffcommand, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            shell=True, 
            universal_newlines=True
            )
        if self.show_progress is True:
            """ 
            get vid info, gen status
            """
            self.status_bar(process=process)
            # print('\n')

        else:
            """
            Just ditch the output
            """
            for line in iter(process.stdout.readline, b''):
                tmp = line

        if not os.path.exists(self.output):
            return False

        return True


    def status_bar(self, process):
        """
        This is a little gross, but it'll get us a status bar thingy

        """
        while True:
            line = process.stdout.readline().strip()

            if line == '' and process.poll() is not None:
                break
            if self.fps == None or self.duration == None:
                if "Stream #" in line and " Video: " in line:
                    self.fps = [s for s in line.split(',') if "fps" in s][0].strip(' fps')

                if "Duration: " in line:
                    dur = line.split('Duration: ')[1].split(',')[0].strip()
                    self.duration = self._seconds_from_string(duration=dur)

            else:
                if 'frame=' in line:

                    cur_frame = line.split('frame=')[1].split('fps=')[0].strip()
                    end_frame = float(self.duration) * float(self.fps.strip())
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


    def _seconds_from_string(self, duration):

        hours = float(duration.split(':')[0])
        minutes = float(duration.split(':')[1])
        seconds = float(duration.split(':')[2])
        duration_seconds = (((hours * 60) + minutes) * 60) + seconds
        return duration_seconds



def main():
    pass

if __name__ == '__main__':
    sys.exit(main())

