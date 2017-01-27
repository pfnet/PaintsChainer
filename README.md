# Paints Chainer
Paints Chainer is line drawing colorizer using chainer.

## Usage of UI
UI is html based. using wPaint.js

boot local server
`python server.py`

access to localhost
`localhost:8000/static/`



## Learning
main code of colorization is in `cgi-bin/paint_x2_unet`

to train 1st layer using GPU 0 `python train_128.py -g 0`
to train 2nd layer using GPU 0 `python train_x2.py -g 0`

to copy models `cp -rf /mnt/sakura201/taizan/PaintChainerModels ./cgi-bin/paint_x2_unet/models`
