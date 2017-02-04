#!/usr/bin/env python

import numpy as np
import numpy
import chainer
import chainer.functions as F
import chainer.links as L
from chainer import cuda, optimizers, serializers, Variable


from chainer import function
from chainer.utils import type_check


class MeanAbsoluteError(function.Function):

    """Mean absolute error function."""

    def check_type_forward(self, in_types):
        type_check.expect(in_types.size() == 2)
        type_check.expect(
            in_types[0].dtype == numpy.float32,
            in_types[1].dtype == numpy.float32,
            in_types[0].shape == in_types[1].shape
        )

    def forward_cpu(self, inputs):
        x0, x1 = inputs
        self.diff = x0 - x1
        diff = self.diff.ravel()
        return numpy.array(abs(diff).sum() / diff.size, dtype=diff.dtype),

    def forward_gpu(self, inputs):
        x0, x1 = inputs
        self.diff = x0 - x1
        diff = self.diff.ravel()
        return abs(diff).sum() / diff.dtype.type(diff.size),

    def backward(self, inputs, gy):
        xp = cuda.get_array_module(*inputs)
        coeff = gy[0] * gy[0].dtype.type(1. / self.diff.size)
        gx0 = coeff * xp.sign(self.diff)
        return gx0, -gx0


def mean_absolute_error(x0, x1):
    """Mean absolute error function.
    This function computes mean absolute error between two variables. The mean
    is taken over the minibatch.
    """
    return MeanAbsoluteError()(x0, x1)


class LNET(chainer.Chain):

    def __init__(self):
        super(LNET, self).__init__(
            c0=L.Convolution2D(3, 32, 3, 1, 1),
            c1=L.Convolution2D(32, 64, 4, 2, 1),
            c2=L.Convolution2D(64, 64, 3, 1, 1),
            c3=L.Convolution2D(64, 128, 4, 2, 1),
            c4=L.Convolution2D(128, 128, 3, 1, 1),
            c5=L.Convolution2D(128, 256, 4, 2, 1),
            c6=L.Convolution2D(256, 256, 3, 1, 1),
            c7=L.Convolution2D(256, 512, 4, 2, 1),
            c8=L.Convolution2D(512, 512, 3, 1, 1),

            dc8=L.Deconvolution2D(1024, 512, 4, 2, 1),
            dc7=L.Convolution2D(512, 256, 3, 1, 1),
            dc6=L.Deconvolution2D(512, 256, 4, 2, 1),
            dc5=L.Convolution2D(256, 128, 3, 1, 1),
            dc4=L.Deconvolution2D(256, 128, 4, 2, 1),
            dc3=L.Convolution2D(128, 64, 3, 1, 1),
            dc2=L.Deconvolution2D(128, 64, 4, 2, 1),
            dc1=L.Convolution2D(64, 32, 3, 1, 1),
            dc0=L.Convolution2D(64, 1, 3, 1, 1),

            bnc0=L.BatchNormalization(32),
            bnc1=L.BatchNormalization(64),
            bnc2=L.BatchNormalization(64),
            bnc3=L.BatchNormalization(128),
            bnc4=L.BatchNormalization(128),
            bnc5=L.BatchNormalization(256),
            bnc6=L.BatchNormalization(256),
            bnc7=L.BatchNormalization(512),
            bnc8=L.BatchNormalization(512),

            bnd8=L.BatchNormalization(512),
            bnd7=L.BatchNormalization(256),
            bnd6=L.BatchNormalization(256),
            bnd5=L.BatchNormalization(128),
            bnd4=L.BatchNormalization(128),
            bnd3=L.BatchNormalization(64),
            bnd2=L.BatchNormalization(64),
            bnd1=L.BatchNormalization(32)
            # l = L.Linear(3*3*256, 2)'
        )

    def enc(self, x, test=False):
        e0 = F.relu(self.bnc0(self.c0(x), test=test))
        e1 = F.relu(self.bnc1(self.c1(e0), test=test))
        e2 = F.relu(self.bnc2(self.c2(e1), test=test))
        e3 = F.relu(self.bnc3(self.c3(e2), test=test))
        e4 = F.relu(self.bnc4(self.c4(e3), test=test))
        e5 = F.relu(self.bnc5(self.c5(e4), test=test))
        e6 = F.relu(self.bnc6(self.c6(e5), test=test))
        e7 = F.relu(self.bnc7(self.c7(e6), test=test))
        e8 = F.relu(self.bnc8(self.c8(e7), test=test))
        return [e0, e2, e4, e6, e7, e8]

    def calc(self, x, test=False):
        e0, e2, e4, e6, e7, e8 = self.enc(x)

        d8 = F.relu(self.bnd8(self.dc8(F.concat([e7, e8])), test=test))
        del e7, e8
        d7 = F.relu(self.bnd7(self.dc7(d8), test=test))
        del d8
        d6 = F.relu(self.bnd6(self.dc6(F.concat([e6, d7])), test=test))
        del d7, e6
        d5 = F.relu(self.bnd5(self.dc5(d6), test=test))
        del d6
        d4 = F.relu(self.bnd4(self.dc4(F.concat([e4, d5])), test=test))
        del d5, e4
        d3 = F.relu(self.bnd3(self.dc3(d4), test=test))
        del d4
        d2 = F.relu(self.bnd2(self.dc2(F.concat([e2, d3])), test=test))
        del d3, e2
        d1 = F.relu(self.bnd1(self.dc1(d2), test=test))
        del d2
        d0 = self.dc0(F.concat([e0, d1]))

        return d0

    def __call__(self, x, t, test=False):
        h = self.calc(x, test)
        loss_c = mean_absolute_error(h, t)
        loss = loss_c
        chainer.report({'loss': loss, 'loss_c': loss_c}, self)
        return loss
