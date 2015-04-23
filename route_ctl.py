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
parser.add_option("-r", "--routes",
                action="store", type="string", dest="all_routes",
                help="a comma-separated list of routes")
parser.add_option("-d", "--disable",
                action="store_true", dest="disable",
                help="disable routes")
parser.add_option("-e", "--enable",
                action="store_true", dest="enable",
                help="enable routes")
parser.add_option("-6", "--ipv6-default",
                action="store", dest="ipv6",
                help="Add the default IPv6 route to disable/enable")
parser.add_option("-4", "--ipv4-default",
                action="store", dest="ipv4",
                help="Add the default IPv4 route to disable/enable")


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

routes = []
if opts.all_routes:
    for i in opts.all_routes.split(","):
        routes.append(i)

if opts.ipv4:
    routes.append(opts.ipv4)

if opts.ipv6:
    routes.append(opts.ipv6)

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

# A pretty way to print output
def data_printer(data):
    for i in data:
        for j in i.keys():
            print "%s: %s" % (j, i[j])

# We need to get the route id in order to make changes to it
def get_route_id(ip):
    try:
        z = a.response_handler(a.talk(["/ip/route/print", "?=dst-address=" + ip]))
        route_id = z[0]['.id']
    except:
        print 'Route not found.'
        sys.exit()
    return route_id

# Issues enable to the device for all routes
def enable_routes(routes):
    for route in routes:
        i = get_route_id(route)
        x = a.response_handler(a.talk(["/ip/route/enable", "=.id" + i]))

# Issues disable to the device for all routes
def disable_routes(routes):
    for route in route:
        i = get_route_id(route)
        x = a.response_handler(a.talk(["/ip/route/disable", "=.id" + i]))

if __name__ == "__main__":
    if opts.enable:
        print "Enabling the following routes: %s" % (opts.all_routes)
        enable_routes(routes)
    elif opts.disable:
        print "Disabling the following routes: %s" % (opts.all_routes)
        disable_routes(routes)
    else:
        data_printer(check_api())
