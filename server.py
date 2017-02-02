#!/usr/bin/env python

import http.server
import socketserver

import os
import sys
import errno
import platform
import time
import json
import re

import argparse

from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs


# sys.path.append('./cgi-bin/wnet')
sys.path.append('./cgi-bin/paint_x2_unet')
import cgi_exe

if os.name == 'nt':
    try:
        ARCH_ARR = ["arm64", "arm", "x64", "x86"]
        ARCH_INDEX0 = 0 if ("arm" in platform.machine().lower()) else 2
        ARCH_INDEX1 = 0 if ("64" in platform.architecture()[0]) else 1
        ARCH_PATH = ARCH_ARR [ARCH_INDEX0 + ARCH_INDEX1]
        ARCH_INJECT = " (x86)" if ("64" in platform.architecture()[0]) else ""
        WK_INC_ROOT = r'C:\Program Files' + ARCH_INJECT + r'\Windows Kits\10\Include'
        WK_FOUND_INC = WK_INC_ROOT + "\\" + os.listdir(path = WK_INC_ROOT)[0]
        WK_LIB_ROOT = r'C:\Program Files' + ARCH_INJECT + r'\Windows Kits\10\Lib'
        WK_FOUND_LIB = WK_LIB_ROOT + "\\" + os.listdir(path = WK_LIB_ROOT)[0]
        WK_INCLUDE = WK_FOUND_INC + r'\ucrt'
        WK_LIB_UM = WK_FOUND_LIB + r'\um'+ "\\" + ARCH_PATH
        WK_LIB_UCRT64 = WK_FOUND_LIB + r'\ucrt' + "\\" + ARCH_PATH
        
        if os.path.isdir(WK_INCLUDE):
            os.environ['INCLUDE'] = WK_INCLUDE
        else:
             raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), WK_INCLUDE)
        
        if os.path.isdir(WK_LIB_UM) and os.path.isdir(WK_LIB_UCRT64):
            os.environ['LIB'] = WK_LIB_UM + ';' + WK_LIB_UCRT64
        elif os.path.isdir(WK_LIB_UM):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), WK_LIB_UCRT64)
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), WK_LIB_UM)
        
    except Exception as e: print (e)


class MyHandler(http.server.CGIHTTPRequestHandler):

    t = []

    def __init__(self, req, client_addr, server):
        http.server.CGIHTTPRequestHandler.__init__(
            self, req, client_addr, server)

    def parse_POST(self):
        ctype, pdict = parse_header(self.headers['content-type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        if ctype == 'multipart/form-data':
            postvars = parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(
                self.rfile.read(length),
                keep_blank_values=1)
        else:
            postvars = {}
        return postvars

    def do_POST(self):
        
        self.t.append(time.time())
        form = self.parse_POST()
        self.t.append(time.time())

        if "id" in form:
            id_str = form["id"][0]
            id_str = re.sub(r'\W+', '', id_str.decode())
        else:
            self.ret_result(False)
            return

        if "line" in form:
            bin1 = form["line"][0]
            fout1 = open("./images/line/" + id_str + ".png", 'wb')
            fout1.write(bin1)
            fout1.close()
        else:
            self.ret_result(False)
            return

        if "ref" in form:
            bin2 = form["ref"][0]
            fout2 = open("./images/ref/" + id_str + ".png", 'wb')
            fout2.write(bin2)
            fout2.close()
        else:
            self.ret_result(False)
            return

        blur = 0
        if "blur" in form:
            blur = form["blur"][0].decode()
            try:
                blur = int(blur)
            except ValueError:
                blur = 0

        self.t.append(time.time())
        if "step" in form:
            if form["step"][0].decode() == "S":
                painter.colorize_s(id_str, blur=blur)
            if form["step"][0].decode() == "L":
                painter.colorize_l(id_str)
        else:
            painter.colorize(id_str, blur=blur)

        self.t.append(time.time())
        self.ret_result(True)
        self.t.append(time.time())
        for i, j in zip(self.t, self.t[1:]):
            print("time [sec]", j - i)

        return

    def ret_result(self, success):
        if success:
            content = bytes(
                "{ 'message':'The command Completed Successfully' , 'Status':'200 OK','success':true , 'used':" + str(args.gpu) + "}", "UTF-8")
            self.send_response(200)
        else:
            content = bytes(
                "{ 'message':'The command Failed' , 'Status':'503 NG','success':false , 'used':" + str(args.gpu) + "}", "UTF-8")
            self.send_response(503)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", len(content))
        self.send_header("Access-Control-Allow-Origin", "http://paintschainer.preferred.tech") # hard coding...
        self.end_headers()
        self.wfile.write(content)
        self.t.append(time.time())


parser = argparse.ArgumentParser(
    description='chainer line drawing colorization server')
parser.add_argument('--gpu', '-g', type=int, default=0,
                    help='GPU ID (negative value indicates CPU)')
parser.add_argument('--port', '-p', type=int, default=8000,
                    help='using port')
parser.add_argument('--host', '-ho', default='localhost',
                    help='using host')
args = parser.parse_args()

print('GPU: {}'.format(args.gpu))

painter = cgi_exe.Painter(gpu=args.gpu)

httpd = http.server.HTTPServer((args.host, args.port), MyHandler)
print('serving at', args.host, ':', args.port, )
httpd.serve_forever()
