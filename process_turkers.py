#!/dev/null

### Don't just run this file! It's set up to run chunks (e.g., by sending to ipython from vim)

'''process_turkers.py - Assign qualifications, send reminders / "bonuses"

NOTE: You need to have your (or our) AWS keys in a ~/.boto file. If you don't
know how to do this, please ask.

Currently this is using anaconda (which includes boto 2.8.0)
installed to /opt. It should be fine to change it.

Note that I mostly use unicode below for interacting with AWS, as it's what we
should be doing for all strings these days (especially when dealing with web
services). Strings are ALL unicode in Python 3.
'''

### If you do this again, it should be done with a class that aggregates
### information from MTurk, and provides makefile like functionality via
### memoization

# If you end up using this paradigm a lot, it could go in whatever boto config
# you're using (probably ~/.boto if you're not specifying it as an argument)
# Currently, these are Dav's, and they won't be available from other accounts
PERSONAL_WORKER_ID = 'A2DLTP7A10KG4T'
PERSONAL_DAY1_ASSIGNMENT_ID = '2F3MJTUHYW2GZE5TB8J54M16TP7OJQ'

import json
from warnings import warn

from . import mturk
# It's unclear I need this - currently just using for to_datetime
import pandas as pd

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

        # self.qual = qual

    def search_hits(self, criteria={}, assert_complete=False):
        '''Get assignments for a given HIT, filtering for matches in `criteria`.

        criteria : dict
            e.g. {'Title': u'Politics, science, and attitudes.'} will search for
            all hits where `h.Title` is that exact string.
        assert_complete : bool
            Raise an exception if the HIT is not finished.'''
        # Note - "search"_hits doesn't do any filtering
        hit_search =self.conn.request('SearchHITs')
        result = hit_search['SearchHITsResponse']['SearchHITsResult']
        assert(result['Request']['IsValid'] == 'True',
            'Problem searching HITs\n' +
                 json.dumps(result, indent=2))

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

        qual_response = self.conn.request('CreateQualificationType',
                                 {'Name': qual_name,
                                  'Description': qual_description,
                                  'QualificationTypeStatus': active_txt} )

        # Check that everything seems OK
        qual_data = qual_response['CreateQualificationTypeResponse']['QualificationType']
        if qual_data['Request']['IsValid'] != 'True':
            warn('Problem creating %s:\n' % qual_name,
                 json.dumps(qual_data, indent=2))

        self.qual_data = qual_data
        return qual_data

    # def get_qual(self):
    #     # We need to grab the existing qualification now
    #     qual = self.conn.search_qualification_types(self.qual)
    #     if len(qual) == 1:
    #         return qual[0]
    #     elif len(qual) == 0:
    #         return self.create_qual()
    #     else:
    #         raise 'Found more than 1 qualification for %s' % self.qual

    # def bonus_price(self):
    #     return self.conn.get_price_as_price(0.05)

    # def assign_qual_and_bonus(self, bonus_text, check_day=lambda x: x <=29,
    #                           qual_val=29, assign_qual=True):
    #     '''Assign the qualification and send a bonus with bonus_text'''
    #     price = self.bonus_price()
    #     qual = self.get_qual()
    #     for i, a in enumerate(self.assignments):
    #         print i
    #         day = pd.to_datetime(a.SubmitTime).day
    #         if check_day(day):
    #             if assign_qual:
    #                 resp = self.conn.assign_qualification(qual.QualificationTypeId,
    #                                                 a.WorkerId, qual_val)
    #                 assert resp.status, 'Problem with qualification assignment'
    #             resp = self.conn.grant_bonus(a.WorkerId, a.AssignmentId, price, bonus_text)
    #             assert resp.status, 'Problem with granting bonus'

# if __name__ == '__main__':
#     mw = MyWorkers()
# 
#     ### Initial qualification and bonus
# 
#     # Note, included a literal \n to avoid ipython magic on the %s
#     BONUS_TEXT = '''***
#     Thanks for completing the first part of our climate change science survey!
# 
#     You should now have a "mech_2013_03" qualification to complete the $2
#     followup (click "Accept HIT" if you're not signed in):\n%s
# 
#     It will expire in about a week, so please complete it as soon as you can!
#     And if you have any trouble, contact me at davclark@berkeley.edu.
# 
#     I'll be sending one final reminder via the bonus system on the last day of
#     the survey. And, if you gave your e-mail, thanks! But, I decided it doesn't
#     make much sense to send you a message that way too.
# 
#     Thanks again,
#     Dav Clark
#     ***'''
# 
#     ## We run this on on April 2
# 
#     april2_url = 'https://www.mturk.com/mturk/preview?groupId=2HGWQIHPCGJ2JRXQ4XWXP0JTUXK17Z'
# 
#     # mw.assign_qual_and_bonus(BONUS_TEXT % april2_url)
# 
#     ## And this one on April 3
# 
#     april3_url = 'https://www.mturk.com/mturk/preview?groupId=25MSIHPCGJ2D8QK5X6OH8JPTXO2284'
# 
#     # mw.assign_qual_and_bonus(BONUS_TEXT % april3_url, lambda x: x >= 30, 30)
# 
# 
#     ### Final bonus / reminder
# 
#     ## Run mid-day April 7
# 
#     FINAL_BONUS_TEXT = '''***
#     Thanks again for completing the first part of our climate change science survey.
#     If you haven't already, PLEASE finish the followup portion of the survey as soon
#     as you can (and if you have, you rock!). It will expire in a little over a day!
# 
#     You should have a "mech_2013_03" qualification, and you can complete the $2
#     followup at this link (click "Accept HIT" if you're not signed in):\n%s
# 
#     And if you have any trouble, contact me at davclark@berkeley.edu.
# 
#     Thanks again,
#     Dav Clark
#     ***'''
# 
#     # mw.assign_qual_and_bonus(FINAL_BONUS_TEXT % april2_url, assign_qual=False)
# 
#     ## Run mid-day April 9
# 
#     FINAL_BONUS_TEXT_2 = '''***
#     Thanks again for completing the first part of our climate change science survey.
#     If you haven't already, PLEASE finish the followup portion of the survey as soon
#     as you can (and if you have, you rock!). It will expire in a little over a day!
# 
#     You should have a "mech_2013_03" qualification, and you can complete the $2
#     followup at this link (click "Accept HIT" if you're not signed in):\n%s
# 
#     It should take less than 10 minutes! And if you have any trouble, contact me
#     at davclark@berkeley.edu.
# 
#     Thanks again,
#     Dav Clark
#     ***'''
# 
#     # mw.assign_qual_and_bonus(FINAL_BONUS_TEXT_2 % april3_url, lambda x: x >= 30, assign_qual=False)
# 
