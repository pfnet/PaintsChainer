# Paints Chainer
Paints Chainer is a line drawing colorizer using chainer.
Using CNN, you can colorize your sketch semi-automatically .

![image](https://github.com/pfnet/PaintsChainer/blob/open/sample.png)

## DEMO
http://paintschainer.preferred.tech/


## Requirement
If not specified, versions are assumed to be recent LTS version.
- A Nvidia graphic card supporting cuDNN i.e. compute capability >= 3.0 (See https://developer.nvidia.com/cuda-gpus)
- Linux: gcc/ g++ 4.8
- Windows: "Microsoft Visual C++ Build Tools 2015" (NOT "Microsoft Visual Studio Community 2015")
- Python 3 (3.5 recommended) ( Python 2.7 needs modifying web host (at least) )
- Numpy
- openCV "cv2" (Python 3 support possible, see installation guide)
- Chainer 2.0.0 or later
- CUDA / cuDNN (If you use GPU)

## Installation Guide
check wiki page
https://github.com/pfnet/PaintsChainer/wiki/Installation-Guide


## Starting web host
UI is html based. using wPaint.js
Server side is very basic python server

boot local server
`python server.py`

access to localhost
`localhost:8000/`


## Learning
main code of colorization is in `cgi-bin/paint_x2_unet`

to train 1st layer using GPU 0 `python train_128.py -g 0`
to train 2nd layer using GPU 0 `python train_x2.py -g 0`

## License
Source code : MIT License

Pre-trained Model : All Rights Reserved

## Pre-Trained Models
Download following model files to  cgi-bin/paint_x2_unet/models/

http://paintschainer.preferred.tech/downloads/

(Copyright 2017 Taizan Yonetsuji All Rights Reserved.)

## Developer Community
Feel free to request an invitation!

https://paintschainerdev.slack.com/

## Acknowledgements
This project is powered by Preferred Networks.

Thanks a lot for rezoolab, mattya, okuta, ofk . This project could not be achived without their great support.

Line drawing of top image is by ioiori18.
