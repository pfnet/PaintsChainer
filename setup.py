'''
This is the setup script for cxfreeze

cxfreeze does not support pkg_resource, to compile,
please modify chainer to hardcode version name and remove pkg_resources

track cxfreeze branch https://github.com/grahamrjuk/cx_Freeze/tree/process_import
for process support

Process.pyc is to be renamed to process.pyc

cupy testing has to be modified to prevent pkg_resources require function
'''
#cx_freeze Dependencies
import sys

#Post-process
import os
import shutil

from cx_Freeze import setup, Executable
sys.path.append('./cgi-bin/paint_x2_unet')
sys.path.append('./cgi-bin/helpers')

# Dependencies fine tuning

MODS = [
    'cupy',
    'numpy.core._methods', 'numpy.lib.format',
    'chainer',
    'cgi_exe',
    'platformAdapter'
]
BUILD_OPTIONS = {"packages": ["os"], "excludes": ["tkinter"], 'includes': MODS}


# GUI applications require a different base on Windows (the default is for a console application).
BASE = None
#if sys.platform == "win32":
#    base = "Win32GUI"

setup(
    name="PaintsChainer",
    version="0.1",
    description="PaintsChainer Executable Version!",
    options={"build_exe": BUILD_OPTIONS},
    executables=[Executable("server.py", base=BASE)]
)

#POST building patching
def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
os.chdir("./build/exe.win-amd64-3.5/")
#todo: other platform path

undetected_dirs = ["wPaint", "models", "images"]
for directory in undetected_dirs:
    shutil.copytree(os.getcwd()+"/../../"+directory, os.getcwd()+"/"+directory)

undetected_files = [
    "index.html",
    "index_ja.html",
    "paints_chainer.js",
    "manifest.json",
    "browserconfig.xml"
]
for file in undetected_files:
    shutil.copyfile(os.getcwd()+"/../../"+file, os.getcwd()+"/"+file)

os.rename("multiprocessing/Process.pyc", "multiprocessing/process.pyc")
