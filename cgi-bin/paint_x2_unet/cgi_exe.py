#!/usr/bin/env python


import numpy as np
import chainer
import cv2

#import chainer.functions as F
#import chainer.links as L
#import six
#import os

from chainer import cuda, serializers, Variable  # , optimizers, training
#from chainer.training import extensions
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
        self._dtype = np.float32

        print("load model")
        if self.gpu >= 0:
            cuda.get_device(self.gpu).use()
            cuda.set_max_workspace_size(64 * 1024 * 1024)  # 64MB
            chainer.Function.type_check_enable = False
        self.cnn_128 = unet.UNET()
        self.cnn_512 = unet.UNET()
        if self.gpu >= 0:
            self.cnn_128.to_gpu()
            self.cnn_512.to_gpu()
        #lnn = lnet.LNET()
        #serializers.load_npz("./cgi-bin/wnet/models/model_cnn_128_df_4", cnn_128)
        #serializers.load_npz("./cgi-bin/paint_x2_unet/models/model_cnn_128_f3_2", cnn_128)
        serializers.load_npz(
            "./cgi-bin/paint_x2_unet/models/unet_128_standard", self.cnn_128)
        #serializers.load_npz("./cgi-bin/paint_x2_unet/models/model_cnn_128_ua_1", self.cnn_128)
        #serializers.load_npz("./cgi-bin/paint_x2_unet/models/model_m_1.6", self.cnn)
        serializers.load_npz(
            "./cgi-bin/paint_x2_unet/models/unet_512_standard", self.cnn_512)
        #serializers.load_npz("./cgi-bin/paint_x2_unet/models/model_p2_1", self.cnn)
        #serializers.load_npz("./cgi-bin/paint_x2_unet/models/model_10000", self.cnn)
        #serializers.load_npz("./cgi-bin/paint_x2_unet/models/liner_f", lnn)

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

        lnn = lnet.LNET()
        with chainer.no_backprop_mode():
            with chainer.using_config('train', False):
                y = lnn.calc(Variable(x))

        self.save_as_img(y.data[0], self.root + "line/" + id_str + ".jpg")

    def colorize(self, id_str, step='C', blur=0, s_size=128,colorize_format="jpg"):
        if self.gpu >= 0:
            cuda.get_device(self.gpu).use()

        _ = {'S': "ref/", 'L': "out_min/", 'C': "ref/"}
        dataset = ImageAndRefDataset(
            [id_str + ".png"], self.root + "line/", self.root + _[step])

        _ = {'S': True, 'L': False, 'C': True}
        sample = dataset.get_example(0, minimize=_[step], blur=blur, s_size=s_size)

        _ = {'S': 0, 'L': 1, 'C': 0}[step]
        sample_container = np.zeros(
            (1, 4, sample[_].shape[1], sample[_].shape[2]), dtype='f')
        sample_container[0, :] = sample[_]

        if self.gpu >= 0:
            sample_container = cuda.to_gpu(sample_container)

        cnn = {'S': self.cnn_128, 'L': self.cnn_512, 'C': self.cnn_128}
        with chainer.no_backprop_mode():
            with chainer.using_config('train', False):
                image_conv2d_layer = cnn[step].calc(Variable(sample_container))
        del sample_container

        if step == 'C':
            input_bat = np.zeros((1, 4, sample[1].shape[1], sample[1].shape[2]), dtype='f')
            print(input_bat.shape)
            input_bat[0, 0, :] = sample[1]

            output = cuda.to_cpu(image_conv2d_layer.data[0])
            del image_conv2d_layer  # release memory

            for channel in range(3):
                input_bat[0, 1 + channel, :] = cv2.resize(
                    output[channel, :], 
                    (sample[1].shape[2], sample[1].shape[1]), 
                    interpolation=cv2.INTER_CUBIC)

            if self.gpu >= 0:
                link = cuda.to_gpu(input_bat, None)
            else:
                link = input_bat
            with chainer.no_backprop_mode():
                with chainer.using_config('train', False):
                    image_conv2d_layer = self.cnn_512.calc(Variable(link))
            del link  # release memory

        image_out_path = {
            'S': self.outdir_min + id_str + ".png", 
            'L': self.outdir + id_str + ".jpg", 
            'C': self.outdir + id_str + "_0." + colorize_format}
        self.save_as_img(image_conv2d_layer.data[0], image_out_path[step])
        del image_conv2d_layer



if __name__ == '__main__':
    for n in range(1):
        p = Painter()
        print(n)
        p.colorize(n * p.batchsize)
