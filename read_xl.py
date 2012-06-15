import glob
import os

from openpyxl import load_workbook

import results

class Predictions(object):

    def fix_name(self, name):
        if name == u'Republic of Ireland':
            return  u'R. of Ireland'
        if name == u'Czech Republic':
            return u'Czech Rep.'
        return name

    def __init__(self, xl_file):
        book = load_workbook(xl_file)
        sheet = book.get_active_sheet()
        data = sheet.range("d2:g25")
        results = []
        for row in data:
            team1, s1, s2, team2 = (cell.value for cell in row)
            team1 = self.fix_name(team1)
            team2 = self.fix_name(team2)
            results.append((u'%s-%s'%(team1, team2), (s1, s2)))
        self.data = results

# the prediction all come from the same template so the should be in
# the same order - we'll ignore the team names except for testing.

    def score(self, results):
        """results is an dictionary mapping team1-team2 strings to 
        score1, score2 tuples"""
        total = 0
        exact = 0
        correct = 0
        for pred in self.data:
            teams, p = pred
            if teams in results:
                p1, p2 = p
                s1, s2 = results[teams]
                if p1 == s1 and p2 == s2:
                    exact +=1
                    total += 3
                elif ( (p1 > p2 and s1 > s2) or
                       (p1 == p2 and s1 == s2) or
                       (p1 < p2 and s1 < s2)):
                    correct += 1
                    total += 1
        return total, exact, correct


class AllPredictions(object):

    def __init__(self, data_dir = 'data'):
        this_dir = os.path.dirname(__file__)
        data_dir = os.path.join(this_dir, data_dir)
        prediction_sheets = glob.glob(os.path.join(data_dir, '*.xlsx'))
        preds = {}
        for fname in prediction_sheets:
            base = os.path.basename(fname)
            name, ext = os.path.splitext(base)
            pred = Predictions(fname)
            preds[name] = pred
        self.predictions = preds
     
    def score(self, results):
        return [(name, pred.score(results)) for 
                name, pred in self.predictions.iteritems()]

if __name__=='__main__':
    import pprint
    p = AllPredictions()
    scores = results.Results().read_data()
    pprint.pprint( p.score(scores))
