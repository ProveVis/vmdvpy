import sys
sys.path.append('..')
import vmdv
import session
from affects.affectImpl import *

def parseJSON():
    print('Messenger thread start...')
    while True:
        data = vmdv.fetchJSON()
        print('Fetched an Affect object')
        t = data['type']
        if t == 'create_session':
            if data['graph_type'] == 'Tree':
                attris = []
                if 'attributes' in data:
                    attris = data['attributes']
                s = session.TreeSession(data['session_descr'], attris)
                vmdv.sessions[data['session_id']] = s
                s.showViewer()
            elif data['graph_type'] == 'DiGraph':
                attris = []
                if 'attributes' in data:
                    attris = data['attributes']
                s = session.DiGraphSession(data['session_descr'], attris)
                vmdv.sessions[data['session_id']] = s
                s.showViewer()
            else:
                print('Unknown graph type:', data['graph_type'])
        elif t == 'remove_session':
            vmdv.sessions.pop(data['session_id'])
        elif t == 'add_node':
            vmdv.putAffect(AddNodeAffect(data['session_id'], data['node']['id'], data['node']['label'], data['node']['state']))
        elif t == 'add_edge':
            if 'label' in data:
                vmdv.putAffect(AddEdgeAffect(data['session_id'], data['from_id'], data['to_id'], data['label']))
            else:
                vmdv.putAffect(AddEdgeAffect(data['session_id'], data['from_id'], data['to_id']))
        elif t == 'feedback':
            if data['status'] == 'OK':
                print('Session received feedback from the prover:', data['session_id'], ',', data['status'])
            else:
                print('Session received feedback from the prover:', data['session_id'], ',', data['status'], ',', data['error_msg'])