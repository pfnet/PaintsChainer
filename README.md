# Paints Chainer
Paints Chainer is line drawing colorizer using chainer.
Using CNN, you can colorize your scketch automatically / semi-automatically .

![image](https://github.com/taizan/PaintsChainer/blob/open/sample.png)

## Requirement
If not specified, versions are assumed to be recent LTS version.
- A Nvidia graphic card supporting CUDA (6.5, 7.0, 7.5, 8.0)
- Linux: gcc/ g++ 4.8
- Windows: "Microsoft Visual C++ Build Tools 2015" (NOT "Microsoft Visual Studio Community 2015")
- Python 3 (3.5 recommended) (Python 2.7 needs modifying web host (at least) )
- Numpy 
- openCV "cv2" (Python 3 support possible, see installation guide)
- Chainer
- CUDA / cuDNN (If you use GPU)

## Installation Guide
#### Option: Docker user
If you have docker, you may check https://hub.docker.com/r/liamjones/paintschainer-docker/ 
(not supported officially but thanks for volunteering)

#### Option: Fresh install
If not specified, follow instruction from their official website.
- Chainer/ Linux gcc: See http://docs.chainer.org/en/stable/install.html
- Microsoft Visual C++ Build Tools 2015 (Windows): See http://landinghub.visualstudio.com/visual-cpp-build-tools
- Python: See https://www.python.org/downloads/
- Numpy: `pip install numpy`. Check installed version after that.
- openCV (Windows): See https://www.solarianprogrammer.com/2016/09/17/install-opencv-3-with-python-3-on-windows/ (Pre-built libraries)
- openCV (Linux): See http://stackoverflow.com/questions/20953273/install-opencv-for-python-3-3 (Build from source)
- openCV (Anaconda): `conda install -c menpo opencv3` (Pre-built libraries)

- Step by step guide for installing chainer (Windows):
(Tested on Win10 64-bit, python 3.5)
 - Step1: Install "Microsoft Visual C++ Build Tools". Uninstall "Visual Studio 2015" if you have it.
 - Step2: Install "Nvidia CUDA"
 - Step3: Register and download "NVIDIA Deep Learning SDK"
 - Step4: `pip install chainer --no-cache-dir -vvvv` (<- Do this AT LAST!)

If you failed to perform the following steps, you will see this message. Uninstall chainer and install it again.
```
 Running command python setup.py egg_info
    Options: {'profile': False, 'annotate': False, 'linetrace': False, 'no_cuda': False}
    Include directories: ['C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v8.0\\include']
    Library directories: ['C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v8.0\\bin', 'C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v8.0\\lib\\x64']
    Microsoft Visual C++ 14.0 is required. Get it with "Microsoft Visual C++ Build Tools": http://landinghub.visualstudio.com/visual-cpp-build-tools
```

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

Thanks a lot for rezoolab, mattya, okuta, ofk . This project could not be achived without their great support.

Line drawing of top image is by ioiori18.
