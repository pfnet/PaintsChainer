# Paints Chainer
Paints Chainer is line drawing colorizer using chainer.
Using CNN, you can colorize your scketch automatically / semi-automatically .

![image](https://github.com/taizan/PaintsChainer/blob/open/sample.png)

## Requirement
- Chainer
- CUDA / cudnn

## How to boot UI
UI is html based. using wPaint.js
Server side is very basic python server

boot local server
`python server.py`

access to localhost
`localhost:8000/static/`


## Learning
main code of colorization is in `cgi-bin/paint_x2_unet`

to train 1st layer using GPU 0 `python train_128.py -g 0`
to train 2nd layer using GPU 0 `python train_x2.py -g 0`

## DEMO
http://paintschainer.preferred.tech/

## License
Source code : MIT License

Pre-trained Model : All Rights Reserved 

## Pre-Trained Models
Download following model files to  cgi-bin/paint_x2_unet/models/

http://paintschainer.preferred.tech/downloads/

(Copyright 2017 Taizan Yonetsuji All Rights Reserved.)



## Acknowledgements
This project is powered by Preferred Networks.

Thanks a lot for rezoolab and mattya. This project could not be achived without their great support.

Line drawing of top image is by ioiori18.
