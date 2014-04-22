#!/usr/bin/env python

'''Create a qualification in the account specified by rootkey.cfg'''

import yaml
from mturk_admin import MyTurkers

# This reads credentials from the current directory
my_turkers = MyTurkers('./mturkconfig.json')

# Get info from the message_info*.yml file
message_info = yaml.load(open('./message_info_a.yml'))

# For now just create a qualification
my_turkers.create_qual(message_info['qual_name'],
                       message_info['qual_description'])




