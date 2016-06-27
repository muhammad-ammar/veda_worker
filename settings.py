#! user/bin/env python

import os
import sys
"""
Globals


*************************************************

** YOU PROBABLY DON'T NEED ANYTHING UNDER HERE **

*************************************************
"""

## TODO: Logging
NODE_LOGGING = False
## Print to Terminal?
NODE_STDIO = True

"""
Initially set to 16:9, can be changed
We can also just ignore this, and push through video at original res/ar 
but you probably shouldn't ##
"""
ENFORCE_TARGET_ASPECT = True
TARGET_ASPECT_RATIO = float(1920) / float(1080)

"""
For BOTO Multipart uploader
"""
MULTI_UPLOAD_BARRIER = 2000000000

"""
Settings for testing
"""
TEST_VIDEO_DIR = os.path.join(os.path.dirname(__file__), 'VEDA_TESTFILES')
TEST_VIDEO_FILE = 'OVTESTFILE_01.mp4'
TEST_VIDEO_ID = 'XXXXXXXX2016-V00TEST'
TEST_ENCODE_PROFILE = 'desktop_mp4'
TEST_VAL_ID = '760ba4421d'

"""
TERM COLORS
"""
NODE_COLORS_BLUE = '\033[94m'
NODE_COLORS_GREEN = '\033[92m'
NODE_COLORS_RED = '\033[91m'
NODE_COLORS_END = '\033[0m'

