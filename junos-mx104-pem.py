#!/usr/bin/python

from __future__ import print_function
from __future__ import unicode_literals
from builtins import input
from datetime import datetime
import getpass
import os
from jnpr.junos import Device
from jnpr.junos.utils.scp import SCP
from jnpr.junos.utils.fs import FS
from jnpr.junos.utils.config import Config

os.system('cls' if os.name == 'nt' else 'clear')

print('''
+--------------------------------------------------------------------------+
|                                                                          |
| add-mx104-pem-fix.py                                                     |
|                                                                          |
| Applies PEM fix script for Junper PR1064039                              |
|                                                                          |
| Written by: Chris Jones (cjones6@semprautilities.com)                    |
|                                                                          |
+--------------------------------------------------------------------------+
''')

def get_credentials():

    juniper_username = input("\nEnter Juniper Username: ")
    juniper_password = getpass.getpass("\nEnter Juniper Password: ") 

    return [ juniper_username, juniper_password ]

def grabhosts():

    inputfile = "mx104-list.input.txt"

    try:
        print("\n>>> Importing list of hosts from " + inputfile + " ...", end="")
        hostlist = open(inputfile,'r').read().split('\n')
        print("SUCCESS!")
        return hostlist
    except: 
        print("FAILED! \n\n>>> Exiting.\n")
        quit()

def processhosts(hostlist,juniper_username,juniper_password):

    print("\n======================================================================\n\nTrying ", str(len(hostlist)), " hosts.\n")
    
    config_set = """
set event-options generate-event 10MIN_PERIODIC time-interval 600
set event-options policy monitoring-pem events 10MIN_PERIODIC
set event-options policy monitoring-pem then event-script monitoring-pem.slax
set event-options event-script file monitoring-pem.slax
"""
    count = 0
    for host in hostlist:
        count += 1
        print("(",count,"/",str(len(hostlist)),") ",host, end="")
        try:
            dev = Device(host=host, user=juniper_username, password=juniper_password, port=22, timeout=30)
            dev.open()
            dev.timeout = 300
            print(" - CONNECTED", end="")
            active_re = dev.facts['master']
            if active_re == "RE0":
                backup_re = "RE1"
            else:
                backup_re = "RE0"
            with SCP(dev, progress=False) as scp:
                scp.put("monitoring-pem.slax", remote_path="/var/run/scripts/event/")  
            print(" - monitoring-pem.slax Transferred", end="")   
            if active_re == "RE0":
                dev.rpc.file_copy(source="/var/run/scripts/event/monitoring-pem.slax", destination="re1:/var/run/scripts/event/monitoring-pem.slax")
                print (" - File also copied to other RE:", backup_re)
            elif active_re == "RE1":
                dev.rpc.file_copy(source="/var/run/scripts/event/monitoring-pem.slax", destination="re0:/var/run/scripts/event/monitoring-pem.slax")
                print (" - File also copied to other RE:", backup_re)
            else:
                print("Can't determine master RE! Skipping Copy.")
            cu = Config(dev)
            cu.rollback()
            cu.load(config_set, format="set")
            if cu.commit_check():
                cu.commit(comment='CHG123010',sync=True)
            else:
                cu.rollback()
            dev.close()     
        except Exception as err: 
            print(" - FAILED: ", err)
            continue

def main():

    hostlist = grabhosts()
    juniper_username, juniper_password = get_credentials()
    processhosts(hostlist,juniper_username,juniper_password)


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCTRL+C Pressed. Exiting.\n\n")
        pass

print("\n")

exit()