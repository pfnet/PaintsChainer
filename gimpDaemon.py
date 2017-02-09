#!/usr/bin/env python

#This Daemon is for Gimp Plugin updated in https://github.com/opaai/PaintsChainer-Gimp
#`python gimpDaemon.py`

import sys
import os

sys.path.append('./cgi-bin/paint_x2_unet')
import cgi_exe

sys.path.append('./cgi-bin/helpers')
from platformAdapter import OSHelper

class GimpDaemon:

    def __init__(self, gpu=0):
        print("start")
        OSHelper.detect_environment()
        self.painter = cgi_exe.Painter(gpu=gpu)


    def run(self, id_str):
        pid_path = "./run/" + id_str + ".pid"
        if os.path.exists(pid_path):
            self.painter.colorize(id_str,step='C',colorize_format="png")
            os.remove(pid_path)


if __name__ == '__main__':
    import time
    daemon = GimpDaemon(gpu=0)
    while True:
        daemon.run('main')
        time.sleep(1)
