
import os
import sys
import subprocess

"""

Quick QA for video file

will not catch all errors (in particular, freezing video/audio problem)
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

from reporting import ErrorObject

class QAVideo():
    
    def __init__(self, filepath, VideoObject=None, mezz_file=False):
        self.filepath = filepath
        self.VideoObject = VideoObject
        self.mezz_file = mezz_file


    def _seconds_from_string(self, duration):
        hours = float(duration.split(':')[0])
        minutes = float(duration.split(':')[1])
        seconds = float(duration.split(':')[2])
        duration_seconds = (((hours * 60) + minutes) * 60) + seconds
        return duration_seconds


    def activate(self):
        """
        First: a general file test 
            -size > 0, 
            -file exists
        """
        if 'http' not in self.filepath:
            """LOCAL"""
            if not os.path.exists(self.filepath):
                ErrorObject(
                    method = self,
                    message = 'File QA fail: File is not found\n' + \
                        self.filepath
                    )
                return False
            
            if os.stat(self.filepath).st_size == 0:
                ErrorObject(
                    method = self,
                    message = 'File QA fail: Filesize is 0\n\
                        Check ffmpeg config'
                    )
                return False

        else:
            """URL"""
            try:
                f = requests.head(self.filepath)
            except:
                ErrorObject(
                    method = self,
                    message = 'File QA fail: File URL not resolving\n\
                        Check config/filepath\n' + \
                        self.filepath
                    )
                return False
               
            if f.status_code > 399: 
                ErrorObject(
                    method = self,
                    message = 'File QA fail: File URL incorrect\n\
                        Check config\n' + \
                        f.url
                    )
                return False

            header_dict = ast.literal_eval(str(f.headers))
            try:
                filesize = header_dict['content-length']
            except:
                ## protect for AWS headers
                try:
                    filesize = header_dict['Content-Length']
                except:
                    ## could make a fail here, but won't for now
                    filesize = None

            if filesize != None:
                if filesize == 0:
                    ErrorObject(
                        method = self,
                        message = 'File QA fail: Filesize is 0\n\
                            Check ffmpeg config'
                        )
                    return False


        """
        ffprobe file information
        """
        ffcommand = 'ffprobe -hide_banner '
        if 'http' in self.filepath:  
            ffcommand += '-print_format json '

        seek_path = self.filepath.replace('https://', 'http://')
        ffcommand += '\"' + seek_path + '\"'
        p = subprocess.Popen(
            ffcommand, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            shell=True
            )

        for line in iter(p.stdout.readline, b''):

            if 'No such file or directory' in line:
                ErrorObject(
                    method = self,
                    message = 'File QA fail: ffprobe: File not found\n' + \
                        self.filepath
                    )
                return False

            if 'Invalid data found when processing input' in line:
                ErrorObject(
                    method = self,
                    message = 'File QA fail: DATA: File is not video or is corrupt\n' + \
                        self.filepath
                    )
                return False

            if "multiple edit list entries, a/v desync might occur, patch welcome" in line:
                ErrorObject(
                    method = self,
                    message = 'File QA fail: METADATA: desync\n' + self.filepath
                    )
                return False

            if "Duration: " in line:
                """Get and Test Duration"""
                if "Duration: 00:00:00.0" in line:
                    ErrorObject(
                        method = self,
                        message = 'File QA fail: DURATION: Duration is zero\n' + \
                            self.filepath
                        )
                    return False
                elif "Duration: N/A, " in line:
                    ErrorObject(
                        method = self,
                        message = 'File QA fail: DURATION: File is not playable\n' + \
                            self.filepath
                        )
                    return False
                vid_duration = line.split('Duration: ')[1].split(',')[0].strip()
                duration = self._seconds_from_string(duration=vid_duration)

                if duration < 1.05:
                    ErrorObject(
                        method = self,
                        message = 'File QA fail: DURATION: Duration is zero\n' + \
                            self.filepath
                        )
                    return False

        try:
            duration
        except:
            ErrorObject(
                method = self,
                message = 'File QA fail: DATA: File is corrupt\n' + self.filepath
                )
            return False

        """
        duration test (if not mezz, is equal to mezz)
        """
        if self.VideoObject != None and self.mezz_file is False:
            ## within five seconds
            if not (self.VideoObject.mezz_duration - 5) <= duration <= (self.VideoObject.mezz_duration + 5):
                ErrorObject(
                    method = self,
                    message = 'File QA fail: MEZZ/PROD Duration mismatch\n' + \
                        self.VideoObject.mezz_duration + '/' + duration
                    )
                return False

        return True



def main():
    pass


if __name__ == '__main__':
    sys.exit(main())

