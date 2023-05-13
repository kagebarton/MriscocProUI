from SCons.Script import Import
from SCons.Script import DefaultEnvironment
env = DefaultEnvironment()
Import("env")

import os,datetime

FW_NAME = os.getenv('FIRMWARE_NAME')

# Check if FW_NAME is not empty
if FW_NAME:
    print("FIRMWARE_NAME: %s" % FW_NAME)
    env.Replace(PROGNAME="%s" % FW_NAME)
else:
    FW_NAME = datetime.now().strftime("firmware-%Y%m%d-%H%M%S")
    env.Replace(PROGNAME="%s" % FW_NAME)
    print("FIRMWARE_NAME: %s" % FW_NAME)