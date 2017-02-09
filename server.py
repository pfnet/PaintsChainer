#!/usr/bin/env python

import http.server

import os
import sys
import time
import re

import argparse

from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs


# sys.path.append('./cgi-bin/wnet')
sys.path.append('./cgi-bin/paint_x2_unet')
import cgi_exe
sys.path.append('./cgi-bin/helpers')
from platformAdapter import OSHelper

class MyHandler(http.server.CGIHTTPRequestHandler):

    t = []

    def __init__(self, req, client_addr, server):
        OSHelper.detect_environment()
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

    def log_t(self):
        if( args.debug ):
            self.t.append(time.time())
        return

    def print_log(self):
        if( args.debug ):
            for i, j in zip(self.t, self.t[1:]):
                print("time [sec]", j - i)
                self.t = []
        return



    def do_POST(self):
        self.log_t()
        form = self.parse_POST()
        self.log_t()

        if "id" in form:
            id_str = form["id"][0]
            id_str = re.sub(r'\W+', '', id_str.decode())
        else:
            self.ret_result(False)
            return

        if( re.search('/post/*', self.path) != None ):
            self.post_process( form, id_str )
        elif ( re.search('/paint/*', self.path) != None ):
            self.paint_process( form, id_str )
        else:
            self.ret_result(False)
        return

    def post_process(self, form, id_str):

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

        self.log_t()
        self.ret_result(True)
        self.log_t()
        self.print_log()

        return

    def paint_process(self, form, id_str):

        blur = 0
        if "blur" in form:
            blur = form["blur"][0].decode()
            try:
                blur = int(blur)
            except ValueError:
                blur = 0

        self.log_t()
        painter.colorize(id_str, form["step"][0].decode() if "step" in form else "C", blur=blur)

        self.log_t()
        self.ret_result(True)
        self.log_t()
        self.print_log()

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
        self.send_header("Access-Control-Allow-Origin", "*")  # hard coding...
        self.end_headers()
        self.wfile.write(content)
        self.log_t()

# set args 

parser = argparse.ArgumentParser(
    description='chainer line drawing colorization server')
parser.add_argument('--gpu', '-g', type=int, default=0,
                    help='GPU ID (negative value indicates CPU)')
parser.add_argument('--mode', '-m', default="stand_alone",
                    help='set process mode')
# other mode "post_server" "paint_server"

parser.add_argument('--port', '-p', type=int, default=8000,
                    help='using port')
parser.add_argument('--debug', dest='debug', action='store_true')
parser.set_defaults(feature=False)

parser.add_argument('--host', '-ho', default='localhost',
                    help='using host')

args = parser.parse_args()

if( args.mode == "stand_alone" or args.mode == "paint_server" ):
    print('GPU: {}'.format(args.gpu))
    painter = cgi_exe.Painter(gpu=args.gpu)

httpd = http.server.HTTPServer((args.host, args.port), MyHandler)
print('serving at', args.host, ':', args.port, )
httpd.serve_forever()
