#!/usr/bin/env python3

import stomp
import sys, getopt
import time
import os.path

USAGE = sys.argv[0] + " -q queue | -t topic -f filetosend | message [message ...] "


def parse():
    options, arguments = getopt.getopt(
        sys.argv[1:],  # Arguments
        "q:t:f:h",  # Short option definitions
        ["queue=", "topic=", "help"],
    )  # Long option definitions
    dest = ""
    msgfile = ""
    for o, a in options:
        if o in ("-h", "--help"):
            print(USAGE)
            sys.exit()
        elif o in ("-q", "--queue"):
            dest = "/queue/" + a
        elif o in ("-f", "--file"):
            msgfile = a
        elif o in ("-t", "--topic"):
            dest = "/topic/" + a
    if dest == "" or (not arguments and msgfile == ""):
        raise SystemExit(USAGE)
    return dest, msgfile, arguments


# class SampleListener(object):
#     def on_message(self, headers, msg):
#         print(msg)
#         print(headers["message-id"])

#         conn.ack(headers["message-id"], 4)


def readfile(filename):
    data = ""
    if not os.path.isfile(filename):
        raise SystemExit("File '{0}' not found".format(filename))

    f = open(filename, "r")
    data = f.read()

    return data


dest, filename, args = parse()

print(dest, args)
#l = SampleListener()
conn = stomp.Connection()
#conn.set_listener("SampleLister", l)
#conn.start()
conn.connect()
filedata = ""
if filename:
    filedata = readfile(filename)
    print("filedata: ", filedata)
    conn.send(body=filedata, destination=dest, headers={"message-id": "test", "timestamp": "1632233012"})

else:
    print("Args: ", args)
    for message in args:
        conn.send(body=message, destination=dest)

time.sleep(1)
conn.disconnect()
