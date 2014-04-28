### Don't just run this file! It's set up to run chunks (e.g., by sending to ipython from vim)

'''process_turkers.py - Assign qualifications, send reminders / "bonuses"

I should really use unicode below for interacting with AWS, as it's what we
should be doing for all strings these days (especially when dealing with web
services). Strings are ALL unicode in Python 3.
'''

import json
from warnings import warn

from . import mturk
# Don't use this - currently just using for to_datetime in some commented code
# import pandas as pd

class MyTurkers:
    '''Stuff that needs doing any time we interface with this set of workers'''

    def __init__(self, config_file=None):
        '''Set up our connection, grab our day 1 assignments'''
        if config_file is not None:
            json_data = json.load(open(config_file))
            self.conn = mturk.MechanicalTurk(json_data)
        else:
            self.conn = mturk.MechanicalTurk()

        self.assignments = []

        self.qual_data = None

    def search_hits(self, criteria={}, assert_complete=False):
        '''Get assignments for a given HIT, filtering for matches in `criteria`.

        criteria : dict
            e.g. {'Title': u'Politics, science, and attitudes.'} will search for
            all hits where `h.Title` is that exact string.
        assert_complete : bool
            Raise an exception if the HIT is not finished.

        Note - "search" hits doesn't do any filtering. We also need to update
        this to account for when we have more than one "page" of HITs.'''

        hit_search = self.conn.request('SearchHITs')
        response = hit_search['SearchHITsResponse']
        result = response['SearchHITsResult']
        assert result['Request']['IsValid'] == 'True', \
            'Problem searching HITs\n' + json.dumps(response, indent=2)

        hits = [h for h in result['HIT'] if
                # All attributes match the values given in the
                # criteria dictionary
                all(h[key] == value for key, value in criteria.items())]

        self.hits = hits
        return hits

    # def load_assignments(self, criteria={}, assert_complete=False):
    #     # Load all assignments for matching HITs
    #     for h in hits:
    #         if assert_complete:
    #             assert h.NumberOfAssignmentsAvailable == \
    #                    h.NumberOfAssignmentsPending == '0', \
    #                    'HIT is not completely finished (pending or available remain)'
    #         # This gives us one flat list of assignments
    #         self.assignments.extend(
    #             self.conn.get_assignments(h.HITId, page_size = h.NumberOfAssignmentsCompleted) )

    #     # You don't need to capture this, it sticks around in self.assignments
    #     return self.assignments

    def create_qual(self, qual_name, qual_description, active=True):
        '''Set up a qualification type to restrice access to the question'''
        if active:
            active_txt = 'Active'
        else:
            active_txt = 'Inactive'

        command = 'CreateQualificationType'
        args = {'Name': qual_name,
                'Description': qual_description,
                'QualificationTypeStatus': active_txt}

        response = self.conn.request(command, args)[command + 'Response']

        qual_data = response['QualificationType']
        if qual_data['Request']['IsValid'] != 'True':
            warn('Problem creating %s:\n%s' % (qual_name,
                    json.dumps(response, indent=2) ))

        self.qual_data = qual_data
        return qual_data

    def get_qual(self, qual_name):
        '''Grab an existing qualification '''

        command = 'SearchQualificationTypes'
        args = {'Query': qual_name}
        response = self.conn.request(command, args)[command + 'Response']
        result = response[command + 'Result']

        if result['Request']['IsValid'] != 'True':
            warn('Problem searching %s:\n%s' % (qual_name,
                    json.dumps(response, indent=2) ))

        num_results = int(result['NumResults'])
        if num_results == 0:
            warn('Qualification does not exist!\n%s' %
                    json.dumps(response, indent=2) )
            qual_data = None
        else:
            if num_results > 1:
                # Data will be a LIST of dicts
                warn('Found more than 1 qualification for %s\n%s' % (args['Query'],
                    json.dumps(response, indent=2) ))

            qual_data =  result['QualificationType']

        self.qual_data = qual_data
        return qual_data

    def assign_qual(self, workerId, value):
        command = 'AssignQualification'
        args = {'QualificationTypeId': self.qual_data['QualificationTypeId'],
                'WorkerId': workerId,
                'IntegerValue': unicode(value)}
        response = self.conn.request(command, args)[command + 'Response']
        result = response[command + 'Result']

        if result['Request']['IsValid'] != 'True':
            warn('Problem assigning %s:\n%s' % (value,
                 json.dumps(response, indent=2) ))

    def grant_bonus(self, workerId, assignmentId, bonus_amt, reason):
        command = 'GrantBonus'
        args = {'WorkerId': workerId,
                'AssignmentId': assignmentId,
                'BonusAmount.1.Amount': bonus_amt,
                'BonusAmount.1.CurrencyCode': 'USD',
                'Reason': reason}

        response = self.conn.request(command, args)[command + 'Response']
        result = response[command + 'Result']

        if result['Request']['IsValid'] != 'True':
            warn('Problem granting bonus:\n%s' % json.dumps(response, indent=2) )
