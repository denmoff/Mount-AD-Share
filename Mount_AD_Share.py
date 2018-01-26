#!/usr/bin/python

############ Mount_AD_Share.py ########################################
#
# Created by Dennis Moffett
# May, 6 2015
# Rutgers University
# Version 1.0.0
# Purpose: Mount user's AD share automatically. First checks to make 
#          sure the Mac is on Rutgers private ip space. Then it checks
#          the connection to AD. If those two things pass, it will 
#          attempt to mount the share using an AppleScript command.
######################################################################

import subprocess, os, sys, getpass, socket, time, commands
from subprocess import Popen, PIPE, call

user_name = getpass.getuser()
ru_ips = [] # put list of subnets in here: eg. ['123.45','234.34']
backup_dir = os.path.join('/Volumes/',user_name)
comp_name = Popen(['/usr/sbin/scutil', '--get', 'ComputerName']\
    ,stdout=PIPE,shell=False).communicate()[0].split('\n')[0]
server_name = '' # put fqdn in here
as_mount_cmd = 'mount volume "smb://%s/%s"' % (server_name,user_name)
mount_share_cmd = ['/usr/bin/osascript', '-e', as_mount_cmd]
###Mount the users share directories as well.
as_mount_cmd_shares = 'mount volume "smb://%s/users"' % server_name
mount_share_cmd_shares = ['/usr/bin/osascript', '-e', as_mount_cmd_shares]
###

def main():
    if os.path.isdir(backup_dir):
        print "The backup directory DOES exist. Checking if empty."
        try:
            dir_list = os.listdir(backup_dir)
        except OSError,e:
            if e.errno == 60:
                print "Waiting to disconnect. Exiting"
                sys.exit()
            else:
                raise

        if not dir_list:# If the directory is empty, try to delete it.
            print "Directory is empty. Trying to delete it."
            try:
                os.rmdir(backup_dir)
                print "Directory Deleted. Attempting mount..."
                mount_ad_share()
            except OSError,x:
                if x.errno == 66:
                    print 'Could not remove backup dir. Exiting'
                    sys.exit()
                else:
                    raise
        else:
            print "Backup directory is not empty. Exiting."
            sys.exit()
    else:
        print "The backup directory DOES NOT exist. Attempting mount..."
        mount_ad_share()


def mount_ad_share():
    DEVNULL = open(os.devnull, 'r+b', 0)
    comp_subnet = get_ip()
    if comp_subnet in ru_ips:
        print "This is a Rutgers subnet."
        if call(['/usr/bin/dscl', '/Search', 'read', '/Computers/%s$' % comp_name]\
            ,stdin=DEVNULL,stdout=DEVNULL,stderr=DEVNULL,shell=False) == 0: #If the command finds the computer, it will return 0.
            print "Connection to AD share is good. Attempting to mount..."
            call(mount_share_cmd,shell=False)
            call(mount_share_cmd_shares,shell=False)
        else:
            print "Could not connect to AD. Exiting."
            sys.exit()
    else:
        print "Not on a Rutgers Subnet. Exiting."
        sys.exit()


def get_ip():
    '''Get the computer's primary IP and return the subnet.'''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    cs = s.getsockname()[0]
    s.close()
    cs = cs.rsplit('.',2)[0]
    return cs

if __name__ == "__main__":
    main()
