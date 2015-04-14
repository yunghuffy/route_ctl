#!/usr/bin/python2

from RosAPI import Core
from optparse import OptionParser
import sys


# OptionParser is the best bet to make this usable on the cli

usage = "usage: %prog hostname username [options]"
parser = OptionParser()
parser.add_option("-o", "--host",
                action="store", type="string", dest="host",
                help="The IP or hostname of the RouterOS box")
parser.add_option("-u", "--user",
                action="store", type="string", dest="user",
                help="Login username")
parser.add_option("-p", "--password",
                action="store", type="string", dest="pw",
                help="The user's password")

(opts, args) = parser.parse_args()
if not opts.host:
    parser.error("No hostname provided")
else:
    host = opts.host

if not opts.user:
    parser.error("User not provided")
else:
    user = opts.user
pw = opts.pw

try:
    a = Core(host)
except:
    print "Can't connect. Check your connection."
    sys.exit()

try:
    a.login(user, pw)
except:
    print "Unable to log in. Check your credentials."
    sys.exit()

# Simple connection tester to make sure you can hit the API

def check_api():
    try:
        z = a.response_handler(a.talk(["/system/resource/print"]))
        return z
    except:
        print 'Unable to connect properly.\nKilling myself.'
        sys.exit()

def data_printer(data):
    for i in data:
        for j in i.keys():
            print "%s: %s" % (j, i[j])

if __name__ == "__main__":
    data_printer(check_api())
