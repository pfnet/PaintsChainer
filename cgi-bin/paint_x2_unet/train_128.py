#!/usr/bin/env python

import numpy as np
import chainer
import chainer.functions as F
import chainer.links as L
import chainer.datasets.image_dataset as ImageDataset
import six
import os
from PIL import Image

from chainer import cuda, optimizers, serializers, Variable
from chainer import training
from chainer.training import extensions

import argparse

import unet
import lnet

#from images_dict import img_dict
from img2imgDataset import Image2ImageDataset

chainer.cuda.set_max_workspace_size(1024 * 1024 * 1024)
os.environ["CHAINER_TYPE_CHECK"] = "0"


def main():
    parser = argparse.ArgumentParser(
        description='chainer line drawing colorization')
    parser.add_argument('--batchsize', '-b', type=int, default=16,
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

    dis = unet.DIS()
    #serializers.load_npz("result/model_dis_iter_20000", dis)

    l = lnet.LNET()
    serializers.load_npz("models/liner_f", l)

    dataset = Image2ImageDataset(
        "dat/images_color_train.dat", root + "line/", root + "color/", train=True)
    # dataset.set_img_dict(img_dict)
    train_iter = chainer.iterators.SerialIterator(dataset, args.batchsize)

    if args.gpu >= 0:
        chainer.cuda.get_device(args.gpu).use()  # Make a specified GPU current
        cnn.to_gpu()  # Copy the model to the GPU
        dis.to_gpu()  # Copy the model to the GPU
        l.to_gpu()

    # Setup optimizer parameters.
    opt = optimizers.Adam(alpha=0.0001)
    opt.setup(cnn)
    opt.add_hook(chainer.optimizer.WeightDecay(1e-5), 'hook_cnn')

    opt_d = chainer.optimizers.Adam(alpha=0.0001)
    opt_d.setup(dis)
    opt_d.add_hook(chainer.optimizer.WeightDecay(1e-5), 'hook_dec')

    # Set up a trainer
    updater = ganUpdater(
        models=(cnn, dis, l),
        iterator={
            'main': train_iter,
            #'test': test_iter
        },
        optimizer={
            'cnn': opt,
            'dis': opt_d},
        device=args.gpu)

    trainer = training.Trainer(updater, (args.epoch, 'epoch'), out=args.out)

    snapshot_interval = (args.snapshot_interval, 'iteration')
    snapshot_interval2 = (args.snapshot_interval * 2, 'iteration')
    trainer.extend(extensions.dump_graph('cnn/loss'))
    trainer.extend(extensions.snapshot(), trigger=snapshot_interval2)
    trainer.extend(extensions.snapshot_object(
        cnn, 'cnn_128_iter_{.updater.iteration}'), trigger=snapshot_interval)
    trainer.extend(extensions.snapshot_object(
        dis, 'cnn_128_dis_iter_{.updater.iteration}'), trigger=snapshot_interval)
    trainer.extend(extensions.snapshot_object(
        opt, 'optimizer_'), trigger=snapshot_interval)
    trainer.extend(extensions.LogReport(trigger=(10, 'iteration'), ))
    trainer.extend(extensions.PrintReport(
        ['epoch', 'cnn/loss', 'cnn/loss_rec', 'cnn/loss_adv', 'cnn/loss_tag', 'cnn/loss_l', 'dis/loss']))
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
        self.cnn, self.dis, self.l = kwargs.pop('models')
        self._iter = 0
        super(ganUpdater, self).__init__(*args, **kwargs)

    def loss_cnn(self, cnn, x_out, t_out, y_out, lam1=1, lam2=1, lam3=10):
        loss_rec = lam1 * (F.mean_absolute_error(x_out, t_out))
        loss_adv = lam2 * y_out
        l_t = self.l.calc((t_out - 128) / 128)
        l_x = self.l.calc((x_out - 128) / 128)
        loss_l = lam3 * (F.mean_absolute_error(l_x, l_t))
        loss = loss_rec + loss_adv + loss_l
        chainer.report({'loss': loss, "loss_rec": loss_rec,
                        'loss_adv': loss_adv, "loss_l": loss_l}, cnn)

        return loss

    def loss_dis(self, dis, y_in, y_out):
        L1 = y_in
        L2 = y_out
        loss = L1 + L2
        chainer.report({'loss': loss}, dis)
        return loss

    def update_core(self):
        xp = self.cnn.xp
        self._iter += 1

        batch = self.get_iterator('main').next()
        batchsize = len(batch)

        w_in = 128
        w_out = 128

        x_in = xp.zeros((batchsize, 4, w_in, w_in)).astype("f")
        t_out = xp.zeros((batchsize, 3, w_out, w_out)).astype("f")

        for i in range(batchsize):
            x_in[i, :] = xp.asarray(batch[i][0])
            t_out[i, :] = xp.asarray(batch[i][1])
        x_in = Variable(x_in)
        t_out = Variable(t_out)

        x_out = self.cnn.calc(x_in)

        cnn_optimizer = self.get_optimizer('cnn')
        dis_optimizer = self.get_optimizer('dis')

        y_target = self.dis(x_out, Variable(
            xp.zeros(batchsize, dtype=np.int32)))

        cnn_optimizer.update(self.loss_cnn, self.cnn, x_out, t_out, y_target)

        x_out.unchain_backward()
        y_fake = self.dis(x_out,  Variable(
            xp.ones(batchsize, dtype=np.int32)))
        y_real = self.dis(t_out,  Variable(
            xp.zeros(batchsize, dtype=np.int32)))
        dis_optimizer.update(self.loss_dis, self.dis, y_real, y_fake)

if __name__ == '__main__':
    main()
