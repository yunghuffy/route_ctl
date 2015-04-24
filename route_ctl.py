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
parser.add_option("-g", "--gateway",
                action="store", dest="gw",
                help="a gateway for routes to add")
parser.add_option("-a", "--ipvg-gateway",
                action="store", dest="ipv6_gw",
                help="Set the IPv6 gateway")

(opts, args) = parser.parse_args()

# Require a hostname
if not opts.host:
    parser.error("No hostname provided")
else:
    host = opts.host

# Require a user
if not opts.user:
    parser.error("User not provided")
else:
    user = opts.user

# Set the gateway if not given on 'enable'
if opts.enable and not opts.gw:
    gw = "127.0.0.1"
else:
    gw = opts.gw

if opts.enable and not opts.ipv6_gw:
    ipv6_gw = "2001:dead:beef::1"
else:
    ipv6_gw = opts.ipv6_gw

# Password store
pw = opts.pw

# Routes list
routes = []

# IPv6 routes list
ipv6_routes = []

# Simple parser to sort the addresses
if opts.all_routes:
    for i in opts.all_routes.split(","):
        if ":" in i:
            ipv6_routes.append(i)
        else:
            routes.append(i)

if opts.ipv4:
    routes.append("0.0.0.0")

if opts.ipv6:
    ipv6_routes.append("::0")

# Instantiating the session and loggin in
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
        f = z[0]['.id']
        route_id = f
        return route_id
    except:
        print "Route %s not found." % ip

# We need to get the route id in order to make changes to it
def get_ipv6_route_id(ip):
    try:
        z = a.response_handler(a.talk(["/ipv6/route/print", "?=dst-address=" + ip]))
        f = z[0]['.id']
        route_id = f
        return route_id
    except:
        print "Route %s not found." % ip

# Issues enable to the device for ipv4 routes
def enable_routes(routes, gateway):
    for route in routes:
        x = a.response_handler(a.talk(["/ip/route/add", "=dst-address=" + route, "=gateway=" + gw]))
        print "Route %s enabled" % route

# Issues enable to the device for ipv6 routes
def enable_ipv6_routes(routes, gateway):
    for route in routes:
        x = a.response_handler(a.talk(["/ipv6/route/add", "=dst-address=" + route, "=gateway=" + ipv6_gw]))
        print "IPv6 route %s enabled" % route

# Issues disable to the device for all routes
def disable_routes(routes):
    for route in routes:
        i = get_route_id(route)
        x = a.response_handler(a.talk(["/ip/route/remove", "=.id=" + i]))
        print "Route %s disabled" % route

# Issues disable to the device for all routes
def disable_ipv6_routes(routes):
    for route in routes:
        i = get_ipv6_route_id(route)
        x = a.response_handler(a.talk(["/ipv6/route/remove", "=.id=" + i]))
        print "IPv6 route %s disabled" % route

if __name__ == "__main__":
    if opts.enable:
        print "Enabling the following routes: %s" % (opts.all_routes)
        if len(ipv6_routes) > 0 and len(routes) > 0:
            enable_ipv6_routes(ipv6_routes, ipv6_gw)
            enable_routes(routes, gw)
        elif len(ipv6_routes) > 0 and not len(routes) > 0:
            enable_ipv6_routes(ipv6_routes, ipv6_gw)
        else:
            enable_routes(routes, gw)
    
    elif opts.disable:
        print "Disabling the following routes: %s" % (opts.all_routes)
        if len(ipv6_routes) > 0 and len(routes) > 0:
            disable_ipv6_routes(ipv6_routes)
            disable_routes(routes)
        elif len(ipv6_routes) > 0 and not len(routes) > 0:
            disable_ipv6_routes(ipv6_routes)
        else:
            disable_routes(routes)
    
    else:
        data_printer(check_api())
