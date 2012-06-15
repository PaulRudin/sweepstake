"""
This module contains code to scrape results from the bbc web page
giving results
"""

import re
import time
import urllib2

from BeautifulSoup import BeautifulSoup

# http://code.activestate.com/recipes/325905-memoize-decorator-with-timeout/
# we use this so we don't keep hitting the Beeb with requests to get
# the results.

class MWT(object):
    """Memoize With Timeout"""
    _caches = {}
    _timeouts = {}
    
    def __init__(self,timeout=600):
        self.timeout = timeout
        
    def collect(self):
        """Clear cache of results which have timed out"""
        for func in self._caches:
            cache = {}
            for key in self._caches[func]:
                if (time.time() - self._caches[func][key][1]) < self._timeouts[func]:
                    cache[key] = self._caches[func][key]
            self._caches[func] = cache
    
    def __call__(self, f):
        self.cache = self._caches[f] = {}
        self._timeouts[f] = self.timeout
        
        def func(*args, **kwargs):
            kw = kwargs.items()
            kw.sort()
            key = (args, tuple(kw))
            try:
                v = self.cache[key]
                if (time.time() - v[1]) > self.timeout:
                    raise KeyError
            except KeyError:
                v = self.cache[key] = f(*args,**kwargs),time.time()
            return v[0]
        func.func_name = f.func_name
        
        return func


class Results(object):

    def __init__(self, 
                 url='http://www.bbc.co.uk/sport/football/european-championship/results'):
        
        self.url = url

    def get_html(self):

        return  urllib2.urlopen(self.url).read()

    @MWT()
    def read_data(self):
        ''' return a dictionary team1-team2 - (score1, score2)
        tuples by scraping the url
        '''
        html = self.get_html()

        soup = BeautifulSoup(html)
        reports = soup.findAll('tr', attrs={'class':'report'})
        results = {}
        score_re = re.compile(r'(\d+)-(\d+)')
        for report in reports:
            scores = report.find('abbr').text
            scores = score_re.match(scores)
            score1 = int(scores.groups(1)[0])
            score2 = int(scores.groups(1)[1])
            team1 = report.find('span', attrs={'class':'team-home teams'}).a.text
            team2 = report.find('span', attrs={'class':'team-away teams'}).a.text
            results['%s-%s'%(team1, team2)] = ( score1, score2)
        return results
        

if __name__ == '__main__':
    import pprint
    r = Results()
    pprint.pprint( r.read_data() ) 

        
        
