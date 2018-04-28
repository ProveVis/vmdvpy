

import sys
sys.path.append('..')
import vmdv
import session
from affects import affect

def handle():
    while True:
        a = vmdv.fetchAffect()
        a.affect()
        print('performed an affect')