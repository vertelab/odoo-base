#!/usr/bin/env python3

import configparser
import os.path
import signal
import sys
import time
from parsecmdline import parse
from asoklistener import AsokListener

lstnr = None

def exit_gracefully(signal, frame):
    signals = {signal.SIGINT: "SIGINT", signal.SIGTERM: "SIGTERM", signal.SIGHUP: "SIGHUP"}
    print("\nReceived {} signal. Cleaning up resources.".format(signals[signal]))
    lstnr.stop()

# main program
def main():
    # Default configuration
    DEFAULTS = {
        "mqhost": "localhost",
        "mqport": "61616",
        "mqtarget": None,
        "mquser": None,
        "mqpwd": None,
        "usessl": 0,
        "dbglevel": "0",
    }

    etcConf = "/etc/odoo/mqlisten.conf"

    # read config file
    parser = configparser.ConfigParser(defaults=DEFAULTS)

    if os.path.isfile(etcConf):
        configFilePath = etcConf
    else:
        configFilePath = "./mqlisten.conf"

    if os.path.isfile(configFilePath):
        print("Found config file: %s" % configFilePath)

    parser.read(configFilePath)
    lstnr = AsokListener(
        host=parser.get("options", "mqhost"),
        port=parser.get("options", "mqport"),
        target=parser.get("options", "mqtarget"),
        user=parser.get("options", "mquser"),
        pwd=parser.get("options", "mqpwd"),
        ssl=parser.get("options", "usessl"),
    )

    lstnr.dbglevel = parser.get("options", "dbglevel")

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGHUP, exit_gracefully)

    # listen won't return until stop() is called
    lstnr.listen()


if __name__ == "__main__":
    main()

