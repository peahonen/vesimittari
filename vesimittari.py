#!/usr/bin/python3

import argparse
import urllib.request
import binascii
import os

def encode_multipart_formdata(fields):
    boundary = binascii.hexlify(os.urandom(16)).decode('ascii')

    body = (
        b''.join(bytes("--%s\r\n"
                       "Content-Disposition: form-data; name=\"%s\"; filename=\"foo\"\r\n"
                       "\r\n" % (boundary, field) ,'ascii')+value+bytes("\r\n", 'ascii') for field,value in fields.items()) +
        bytes("--%s--\r\n" % boundary, 'ascii')
    )

    content_type = "multipart/form-data; boundary=%s" % boundary

    return body, content_type

parser = argparse.ArgumentParser(description='Send image for analysis')
parser.add_argument('command',
                    help='operation to run - meter')

parser.add_argument('imageurl',
                    help='url of image to process')

parser.add_argument('--verbose', '-v',
    action='store_true',
    help='verbose flag' )

parser.add_argument('--graphical', '-g',
    action='store_true',
    help='<ignored>' )

parser.add_argument('-f', type=argparse.FileType('r'),
    help='<ignored>' )

parser.add_argument('-c', type=argparse.FileType('r'),
    help='<ignored>' )

parser.add_argument('--result', '-r',
    action='store_true',
    help='<ignored>' )

parser.add_argument('--disable-shake', '-d',
    action='store_true',
    help='<ignored>' )

parser.add_argument('--url', '-u',
    action='store_true',
    help='<ignored>' )

parser.add_argument('--user')
parser.add_argument('--password')
parser.add_argument('--server', '-S', help='endpoint url at the server')

args = parser.parse_args()
if args.server:
    endpoint = args.server
else:
    endpoint = "http://vesimittari.ahonen.net:8080/v1/image"

if args.url:
    imageurl = args.imageurl
else:
    imageurl = urllib.parse.urljoin("file://%s/" % os.getcwd() ,args.imageurl)

password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, args.imageurl, args.user, args.password)
handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
opener = urllib.request.build_opener(handler)

urllib.request.install_opener(opener)

if args.command == "meter":
    with urllib.request.urlopen(imageurl) as response:
        image = response.read()
        request_body, content_type = encode_multipart_formdata({"image": image})
        request = urllib.request.Request(endpoint, \
                                         data=request_body)
        request.add_header("Content-Type",content_type)
        with urllib.request.urlopen(request) as result:
            print(result.read().decode("utf-8"))
else:
    print("no such command %s" % args.command)
