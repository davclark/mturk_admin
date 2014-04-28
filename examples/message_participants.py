#!/usr/bin/env python

'''Send a message to turkers to request participation in the followup'''

from string import Template

from csv import DictReader

import yaml
from mturk_admin import MyTurkers


def message_and_bonus(credential_file='./mturkconfig.json',
                      message_file='./message_info.yml',
                      csv_file='./assignments.csv'):
    # This reads credentials from the current directory
    my_turkers = MyTurkers(credential_file)

    # Get info from the message_info*.yml file
    message_info = yaml.load(open(message_file))
    msg_templ = Template(message_info['message'])

    my_turkers.get_qual(message_info['qual_name'])

    try:
        turker_info = DictReader(open(csv_file))
    except IOError:
        print "Can't open filename:", argv[1]
        return False

    for row in turker_info:
        group = row['Group']

        # Assigne qualification
        my_turkers.assign_qual(row['workerId'],
                               message_info['qual_value'][group] )

        # Fill in our template
        message = msg_templ.substitute(
                                qual_name=message_info['qual_name'],
                                amount=message_info['survey_amounts'][group],
                                time=message_info['survey_times'][group],
                                link=message_info['links'][group] )

        # Send a message w/ a bonus
        my_turkers.grant_bonus(row['workerId'], row['assignmentId'],
                               message_info['bonus_amt'], message)

    return True

if __name__ == "__main__":
    from sys import argv, exit

    try:
        csv_file = argv[1]
    except IndexError:
        print "Please provide a CSV file with workerId,assignmentId,Group"
        exit()

    if not message_and_bonus(csv_file=csv_file):
        print "Houston, we had a problem."
