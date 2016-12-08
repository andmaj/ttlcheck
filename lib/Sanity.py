import os
import sys
import logging
import json
import datetime
from pymongo import MongoClient
from bunch import *

sys.path.append("utils")
import utils
import lib

sample = None


def tests():
    link_filter = {} # {"datetime": float(1445110472.9883)}

    def duple_test(link):
        global sample

        del link["_id"]
        if sample is None:
            sample = json.dumps(link)
        elif sample == json.dumps(link):
            print "Duplication!"
        else:
            print "Nothing interesting..."

    def as_from_test(link):
        link = bunchify(link)
        last = Bunch(ip=link["from"].ip, asn=link["from"].asn)
        error = False
        print "measure from asn: %s" % link["from"].asn

        for akt in link.links:
            if akt["from"].ip != last.ip:
                print "IP hiba: %s != %s" % (last.ip, akt["from"].ip)
                error = True

            if int(akt["from"].asn) != int(last.asn):
                print "AS Hiba: %s != %s" %\
                     (akt["from"].asn, last.asn)
                error = True
            # else:
                # print "Nincs AS hiba"

            last.ip = akt.to.ip
            last.asn = akt.to.asn

        if error:
            print "error!"
        print "--------"

    lib.mongoMap("links2", as_from_test, link_filter, limit=5)


if __name__ == '__main__':
    pass