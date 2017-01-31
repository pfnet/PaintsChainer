#!/usr/bin/env python


import numpy as np
import chainer
import chainer.functions as F
import chainer.links as L
import six
import os
import cv2

from chainer import cuda, optimizers, serializers, Variable
from chainer import training
from chainer.training import extensions
#from train import Image2ImageDataset
from img2imgDataset import ImageAndRefDataset

import unet
import lnet


class Painter:

    def __init__(self, gpu=0):

        print("start")
        self.root = "./images/"
        self.batchsize = 1
        self.outdir = self.root + "out/"
        self.outdir_min = self.root + "out_min/"
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
        lnn = lnet.LNET()
        #serializers.load_npz("./cgi-bin/wnet/models/model_cnn_128_df_4", cnn_128)
        #serializers.load_npz("./cgi-bin/paint_x2_unet/models/model_cnn_128_f3_2", cnn_128)
        serializers.load_npz(
            "./cgi-bin/paint_x2_unet/models/unet_128_standard", self.cnn_128)
        #serializers.load_npz("./cgi-bin/paint_x2_unet/models/model_cnn_128_ua_1", self.cnn_128)
        #serializers.load_npz("./cgi-bin/paint_x2_unet/models/model_m_1.6", self.cnn)
        serializers.load_npz(
            "./cgi-bin/paint_x2_unet/models/unet_512_standard", self.cnn)
        #serializers.load_npz("./cgi-bin/paint_x2_unet/models/model_p2_1", self.cnn)
        #serializers.load_npz("./cgi-bin/paint_x2_unet/models/model_10000", self.cnn)
        #serializers.load_npz("./cgi-bin/paint_x2_unet/models/liner_f", lnn)

    def save_as_img(self, array, name):
        array = array.transpose(1, 2, 0)
        array = array.clip(0, 255).astype(np.uint8)
        array = cuda.to_cpu(array)
        img = cv2.cvtColor(array, cv2.COLOR_YUV2RGB)
        cv2.imwrite(name, img)

    def liner(self, id_str):
        if self.gpu >= 0:
            cuda.get_device(self.gpu).use()

        image1 = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)
        image1 = np.asarray(image1, self._dtype)
        if image1.ndim == 2:
            image1 = image1[:, :, np.newaxis]
        img = image1.transpose(2, 0, 1)
        x = np.zeros((1, 3, img.shape[1], img.shape[2]), dtype='f')
        if self.gpu >= 0:
            x = cuda.to_gpu(x)

        y = lnn.calc(Variable(x, volatile='on'), test=True)

        self.save_as_img(y.data[0], self.root + "line/" + id_str + ".jpg")

    def colorize_s(self, id_str, blur=0, s_size=128):
        if self.gpu >= 0:
            cuda.get_device(self.gpu).use()

        dataset = ImageAndRefDataset(
            [id_str + ".png"], self.root + "line/", self.root + "ref/")
        test_in_s, test_in = dataset.get_example(
            0, minimize=True, blur=blur, s_size=s_size)
        x = np.zeros((1, 4, test_in_s.shape[1], test_in_s.shape[2]), dtype='f')

        x[0, :] = test_in_s

        if self.gpu >= 0:
            x = cuda.to_gpu(x)
        y = self.cnn_128.calc(Variable(x, volatile='on'), test=True)

        self.save_as_img(y.data[0], self.outdir_min + id_str + ".png")

    def colorize_l(self, id_str):
        if self.gpu >= 0:
            cuda.get_device(self.gpu).use()

        dataset = ImageAndRefDataset(
            [id_str + ".png"], self.root + "line/", self.root + "out_min/")
        test_in, test_in_ = dataset.get_example(0, minimize=False)
        x = np.zeros((1, 4, test_in.shape[1], test_in.shape[2]), dtype='f')
        x[0, :] = test_in

        if self.gpu >= 0:
            x = cuda.to_gpu(x)
        y = self.cnn.calc(Variable(x, volatile='on'), test=True)

        self.save_as_img(y.data[0], self.outdir + id_str + ".jpg")

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

        # self.save_as_img(output, self.outdir_min + id_str + "_0.png")

        for ch in range(3):
            input_bat[0, 1 + ch, :] = cv2.resize(
                output[ch, :], (line2.shape[2], line2.shape[1]), interpolation=cv2.INTER_CUBIC)

        if self.gpu >= 0:
            x = cuda.to_gpu(input_bat, cuda.Stream.null)
        else:
            x = input_bat
        y = self.cnn.calc(Variable(x, volatile='on'), test=True)
        del x  # release memory

        self.save_as_img(y.data[0], self.outdir + id_str + "_0.jpg")


if __name__ == '__main__':
    for n in range(1):
        print(n)
        colorize(n * batchsize)
