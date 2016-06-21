#!/usr/bin/env python
import subprocess
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError
import re

@operation
def start(**kwargs):
    package_manager = ctx.node.properties['package_manager']

    ctx.logger.info('Installing ntp')
    install_proc = subprocess.Popen(['sudo', package_manager, 'install', 'ntp'], stdout=subprocess.PIPE)

    which_proc = subprocess.Popen(['which', 'yum'], stdout=subprocess.PIPE)
    while True:
        line = which_proc.stdout.readline()
        if line != '' or r'\n':
            #the real code does filtering here
            
            # we're adding a property which is set during runtime to the runtime
            # properties of that specific node instance
            ctx.instance.runtime_properties['ntp_path'] = line.rstrip()
        else:
            break
    
    systemctl_enable_proc = subprocess.Popen(['systemctl', 'start', 'ntp' ])
    
    #check if ntp is running, otherwise throw error
    
    systemctl_status_proc = subprocess.Popen(['systemctl', 'start', 'ntp' ],  stdout=subprocess.PIPE)
    
    for line in systemctl_status_proc.stdout.readlines():
        if re.search('inactive (dead)', line):
            raise NonRecoverableError("Failed to start NTP")
    else:
        ctx.logger.info('NTP installed')
