#!/usr/bin/env python

#This Daemon is for Gimp Plugin updated in https://github.com/opaai/PaintsChainer-Gimp
#`python gimpDaemon.py`

import sys
import os
import numpy as np
import chainer
import cv2

from chainer import cuda, serializers, Variable

sys.path.append('./cgi-bin/paint_x2_unet')
from img2imgDataset import ImageAndRefDataset
import unet

sys.path.append('./cgi-bin/helpers')
from platformAdapter import OSHelper

class GimpDaemon:

    def __init__(self, gpu=0):

        print("start")

        OSHelper.detect_environment()

        self.root = "./images/"
        self.gpu = gpu

        print("load model")
        if self.gpu >= 0:
            cuda.get_device(self.gpu).use()
            cuda.set_max_workspace_size(64 * 1024 * 1024)  # 64MB
            chainer.Function.type_check_enable = False
        self.cnn_128 = unet.UNET()
        self.cnn = unet.UNET()
        if self.gpu >= 0:
            self.cnn_128.to_gpu()
            self.cnn.to_gpu()

        serializers.load_npz(
            "./cgi-bin/paint_x2_unet/models/unet_128_standard", self.cnn_128)
        serializers.load_npz(
            "./cgi-bin/paint_x2_unet/models/unet_512_standard", self.cnn)

    def save_as_img(self, array, name):
        array = array.transpose(1, 2, 0)
        array = array.clip(0, 255).astype(np.uint8)
        array = cuda.to_cpu(array)
        (major, minor, _) = cv2.__version__.split(".")
        if major == '3':
            img = cv2.cvtColor(array, cv2.COLOR_YUV2RGB)
        else:
            img = cv2.cvtColor(array, cv2.COLOR_YUV2BGR)
        cv2.imwrite(name, img)

    def colorize(self, id_str, blur=0, s_size=128):
        if self.gpu >= 0:
            cuda.get_device(self.gpu).use()

        dataset = ImageAndRefDataset(
            [id_str + ".png"], self.root + "line/", self.root + "ref/")
        line, line2 = dataset.get_example(0, minimize=True)
        # 1st fixed to 128*128
        x = np.zeros((1, 4, line.shape[1], line.shape[2]), dtype='f')
        input_bat = np.zeros((1, 4, line2.shape[1], line2.shape[2]), dtype='f')
        print(input_bat.shape)

        x[0, :] = line
        input_bat[0, 0, :] = line2

        if self.gpu >= 0:
            x = cuda.to_gpu(x, cuda.Stream.null)
        y = self.cnn_128.calc(Variable(x, volatile='on'), test=True)
        del x  # release memory

        output = cuda.to_cpu(y.data[0])
        del y  # release memory

        for ch in range(3):
            input_bat[0, 1 + ch, :] = cv2.resize(
                output[ch, :], (line2.shape[2], line2.shape[1]),
                interpolation=cv2.INTER_CUBIC)

        if self.gpu >= 0:
            x = cuda.to_gpu(input_bat, cuda.Stream.null)
        else:
            x = input_bat
        y = self.cnn.calc(Variable(x, volatile='on'), test=True)
        del x  # release memory

        self.save_as_img(y.data[0], self.root + "out/" + id_str + "_0.png")

    def run(self, id_str):
        pid_path = "./run/" + id_str + ".pid"
        if os.path.exists(pid_path):
            self.colorize(id_str)
            os.remove(pid_path)


if __name__ == '__main__':
    import time
    daemon = GimpDaemon(gpu=0)
    while True:
        daemon.run('main')
        time.sleep(1)
