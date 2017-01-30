#!/usr/bin/env python

import http.server
import socketserver

import os
import sys
import time
import json

import argparse

from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs


# sys.path.append('./cgi-bin/wnet')
sys.path.append('./cgi-bin/paint_x2_unet')
import cgi_exe


class MyHandler(http.server.CGIHTTPRequestHandler):

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
        t = []
        t.append(time.time())
        form = self.parse_POST()
        t.append(time.time())

        if "id" in form:
            id_str = form["id"][0]
            id_str = id_str.decode()
        else:
            id_str = "test"

        if "line" in form:
            bin1 = form["line"][0]
            fout1 = open("./static/images/line/" + id_str + ".png", 'wb')
            fout1.write(bin1)
            fout1.close()

        if "ref" in form:
            bin2 = form["ref"][0]
            fout2 = open("./static/images/ref/" + id_str + ".png", 'wb')
            fout2.write(bin2)
            fout2.close()

        blur = 0
        if "blur" in form:
            blur = form["blur"][0].decode()
            try:
                blur = int(blur)
            except ValueError:
                blur = 0

        t.append(time.time())
        if "step" in form:
            if form["step"][0].decode() == "S":
                painter.colorize_s(id_str, blur=blur)
            if form["step"][0].decode() == "L":
                painter.colorize_l(id_str)
        else:
            painter.colorize(id_str, blur=blur)

        t.append(time.time())
        content = bytes(
            "{ 'message':'The command Completed Successfully' , 'Status':'200 OK','success':true , 'used':" + str(args.gpu) + "}", "UTF-8")
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", len(content))
        self.end_headers()
        self.wfile.write(content)
        t.append(time.time())
        for i, j in zip(t, t[1:]):
            print("time [sec]", j - i)

        return

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
