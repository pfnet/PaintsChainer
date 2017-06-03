#!/usr/bin/env python

import numpy as np
import chainer
import chainer.functions as F
import chainer.links as L
import chainer.datasets.image_dataset as ImageDataset
import six
import os
import cv2

from chainer import cuda, optimizers, serializers, Variable
from chainer import training
from chainer.training import extensions

import argparse

import unet
import lnet

#from images_dict import img_dict
from img2imgDataset import Image2ImageDatasetX2


# chainer.cuda.set_max_workspace_size(1024*1024*1024)
#os.environ["CHAINER_TYPE_CHECK"] = "0"


def main():
    parser = argparse.ArgumentParser(
        description='chainer line drawing colorization')
    parser.add_argument('--batchsize', '-b', type=int, default=4,
                        help='Number of images in each mini-batch')
    parser.add_argument('--epoch', '-e', type=int, default=20,
                        help='Number of sweeps over the dataset to train')
    parser.add_argument('--gpu', '-g', type=int, default=-1,
                        help='GPU ID (negative value indicates CPU)')
    parser.add_argument('--dataset', '-i', default='./images/',
                        help='Directory of image files.')
    parser.add_argument('--out', '-o', default='result',
                        help='Directory to output the result')
    parser.add_argument('--resume', '-r', default='',
                        help='Resume the training from snapshot')
    parser.add_argument('--seed', type=int, default=0,
                        help='Random seed')
    parser.add_argument('--snapshot_interval', type=int, default=10000,
                        help='Interval of snapshot')
    parser.add_argument('--display_interval', type=int, default=100,
                        help='Interval of displaying log to console')
    args = parser.parse_args()

    print('GPU: {}'.format(args.gpu))
    print('# Minibatch-size: {}'.format(args.batchsize))
    print('# epoch: {}'.format(args.epoch))
    print('')

    root = args.dataset
    #model = "./model_paint"

    cnn = unet.UNET()
    #serializers.load_npz("result/model_iter_10000", cnn)
    cnn_128 = unet.UNET()
    serializers.load_npz("models/model_cnn_128_dfl2_9", cnn_128)

    dataset = Image2ImageDatasetX2(
        "dat/images_color_train.dat", root + "linex2/", root + "colorx2/", train=True)
    # dataset.set_img_dict(img_dict)
    train_iter = chainer.iterators.SerialIterator(dataset, args.batchsize)

    if args.gpu >= 0:
        chainer.cuda.get_device(args.gpu).use()  # Make a specified GPU current
        cnn.to_gpu()  # Copy the model to the GPU
        cnn_128.to_gpu()  # Copy the model to the GPU

    # Setup optimizer parameters.
    opt = optimizers.Adam(alpha=0.0001)
    opt.setup(cnn)
    opt.add_hook(chainer.optimizer.WeightDecay(1e-5), 'hook_cnn')

    # Set up a trainer
    updater = ganUpdater(
        models=(cnn, cnn_128),
        iterator={'main': train_iter, },
        optimizer={'cnn': opt},
        device=args.gpu)

    trainer = training.Trainer(updater, (args.epoch, 'epoch'), out=args.out)

    snapshot_interval = (args.snapshot_interval, 'iteration')
    snapshot_interval2 = (args.snapshot_interval * 2, 'iteration')
    trainer.extend(extensions.dump_graph('cnn/loss'))
    trainer.extend(extensions.snapshot(), trigger=snapshot_interval2)
    trainer.extend(extensions.snapshot_object(
        cnn, 'cnn_x2_iter_{.updater.iteration}'), trigger=snapshot_interval)
    trainer.extend(extensions.snapshot_object(
        opt, 'optimizer_'), trigger=snapshot_interval)
    trainer.extend(extensions.LogReport(trigger=(10, 'iteration'), ))
    trainer.extend(extensions.PrintReport(
        ['epoch', 'cnn/loss', 'cnn/loss_rec']))
    trainer.extend(extensions.ProgressBar(update_interval=20))

    trainer.run()

    if args.resume:
        # Resume from a snapshot
        chainer.serializers.load_npz(args.resume, trainer)

    # Save the trained model
    chainer.serializers.save_npz(os.path.join(out_dir, 'model_final'), cnn)
    chainer.serializers.save_npz(os.path.join(out_dir, 'optimizer_final'), opt)


class ganUpdater(chainer.training.StandardUpdater):

    def __init__(self, *args, **kwargs):
        self.cnn, self.cnn_128 = kwargs.pop('models')
        self._iter = 0
        super(ganUpdater, self).__init__(*args, **kwargs)

    def loss_cnn(self, cnn, x_out, t_out, lam1=1):
        loss_rec = lam1 * (F.mean_absolute_error(x_out, t_out))
        loss = loss_rec
        chainer.report({'loss': loss, "loss_rec": loss_rec}, cnn)

        return loss

    def update_core(self):
        xp = self.cnn.xp
        self._iter += 1

        batch = self.get_iterator('main').next()
        batchsize = len(batch)

        w_in = 128
        w_in_2 = 512
        w_out = 512

        x_in = xp.zeros((batchsize, 4, w_in, w_in)).astype("f")
        x_in_2 = xp.zeros((batchsize, 4, w_in_2, w_in_2)).astype("f")
        t_out = xp.zeros((batchsize, 3, w_out, w_out)).astype("f")

        for i in range(batchsize):
            x_in[i, :] = xp.asarray(batch[i][0])
            x_in_2[i, 0, :] = xp.asarray(batch[i][2])
            for ch in range(3):
                color_ch = cv2.resize(
                    batch[i][1][ch], (w_out, w_out), interpolation=cv2.INTER_CUBIC).astype("f")
                x_in_2[i, ch + 1, :] = xp.asarray(color_ch)
            t_out[i, :] = xp.asarray(batch[i][3])

        x_in = Variable(x_in)
        t_out = Variable(t_out)

        x_out = self.cnn_128.calc(x_in)
        x_out = x_out.data.get()

        for j in range(batchsize):
            for ch in range(3):
                # randomly use src color ch
                if np.random.rand() < 0.8:
                    x_in_2[j, 1 + ch, :] = xp.asarray(cv2.resize(
                        x_out[j, ch, :], (w_in_2, w_in_2), interpolation=cv2.INTER_CUBIC))

        x_in_2 = Variable(x_in_2)
        x_out_2 = self.cnn.calc(x_in_2)

        cnn_optimizer = self.get_optimizer('cnn')

        cnn_optimizer.update(self.loss_cnn, self.cnn, x_out_2, t_out)


if __name__ == '__main__':
    main()
