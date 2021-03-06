import sys
import vmdv
import affect
from PyQt5.QtCore import QThread
from PyQt5 import QtCore
import abc
import json
import socket
import logging


class FileReader(QThread):
    def __init__(self, v, filename, parent=None):
        super(FileReader, self).__init__(parent)
        self.v = v
        self.filename = filename


    initSessionSignal = QtCore.pyqtSignal(str, str, list, str)
    affectSignal = QtCore.pyqtSignal(str, affect.Affect)

    def run(self):
        f = open(self.filename, 'r')
        while True:
            line = f.readline()
            data = None
            try:
                data = json.loads(line)
            except json.decoder.JSONDecodeError:
                print('cannot decode this into a json:', line)
                break
            t = data['type']
            # print('Received a json object:', t)
            if t == 'create_session':
                if data['graph_type'] == 'Tree':
                    attris = []
                    if 'attributes' in data:
                        attris = data['attributes']
                    self.initSessionSignal.emit(
                        data['session_id'], data['session_descr'], attris, 'Tree')
                elif data['graph_type'] == 'DiGraph':
                    attris = []
                    if 'attributes' in data:
                        attris = data['attributes']
                    self.initSessionSignal.emit(data['session_id'], data['session_descr'], attris, 'DiGraph')
                else:
                    print('Unknown graph type:',
                            data['graph_type'])
            elif t == 'remove_session':
                self.v.sessions.pop(data['session_id'])
            elif t == 'add_node':
                nodeProps = data['node']
                a = affect.AddNodeAffect(nodeProps)
                # a = affect.AddNodeAffect(data['node']['id'], data['node']['label'], data['node']['state'])
                # self.v.putAffect(data['session_id'], a)
                self.affectSignal.emit(data['session_id'], a)
            elif t == 'add_edge':
                a = None
                if 'label' in data:
                    a = affect.AddEdgeAffect(data['from_id'], data['to_id'], data['label'])
                else:
                    a = affect.AddEdgeAffect(data['session_id'], data['from_id'], data['to_id'])
                # self.v.putAffect(data['session_id'], a)
                self.affectSignal.emit(data['session_id'], a)
            elif t == 'highlight_node':
                sid = data['session_id']
                nid = data['node_id']
                self.affectSignal.emit(sid, affect.HighlightNodeAffect(nid))
            elif t == 'clear_color':
                sid = data['session_id']
                self.affectSignal.emit(sid, affect.ClearColorAffect())
            elif t == 'request':
                print('VMDV received a request message')
            elif t == 'response':
                sid = data['session_id']
                rid = data['request_id']
                result = data['result']

                pr = self.v.pendingRequests
                if rid not in pr:
                    print('There is no pending request', rid)
                else:
                    rname, rargs = pr[rid]
                    pr.pop(rid)
                    self.affectSignal.emit(sid, affect.ParseResponseAffect(rname, rargs, result))
                    self.v.reponseCache[(rname, rargs['zone'])] = result
            elif t == 'feedback':
                if data['status'] == 'OK':
                    print('Session received feedback from the prover:', data['session_id'], ',', data['status'])
                else:
                    print('Session received feedback from the prover:', data['session_id'], ',', data['status'], ',', data['error_msg'])
            else:
                print('Unknown type of message:', data['type'])


def matchJSONStr(toBeMatched):
    if toBeMatched.startswith('{\"type\":'):
        flag = 0
        length = len(toBeMatched)
        for i in range(length):
            if toBeMatched[i] == '{':
                flag += 1
            elif toBeMatched[i] == '}':
                flag -= 1
            elif toBeMatched[i] == '\n' and flag == 0 and i != 0:
                return (toBeMatched[:i], toBeMatched[i+1:])
        return ('', toBeMatched)
    elif toBeMatched[0] == '\n':
        if len(toBeMatched) == 1:
            return ('', '')
        else:
            return matchJSONStr(toBeMatched[1:])
    else:
        return ('', toBeMatched)


class Receiver(QThread):
    def __init__(self, v, parent=None):
        super(Receiver, self).__init__(parent)
        self.v = v
        self.sock = None
        self.v.jsonThread = self

    initSessionSignal = QtCore.pyqtSignal(str, str, list, str)
    affectSignal = QtCore.pyqtSignal(str, affect.Affect)

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 3333))
        s.listen()
        connSock, address = s.accept()
        self.sock = connSock
        print('Connection established with a prover: ', address)
        msgThread = Sender(self.v, connSock)
        msgThread.start()
        try:
            unmatchedStr = ''
            while True:
                recvdBytes = connSock.recv(40960)
                if not recvdBytes:
                    print('network receiving data error')
                    connSock.close()
                    msgThread.stop()
                    sys.exit(1)
                    break
                
                # print(recvdBytes)

                # logging.getLogger('file').info('Received JSON:'+recvdBytes.decode('utf-8'))
                recvdStrs = []
                m, r = matchJSONStr(
                    unmatchedStr + (recvdBytes.decode('utf-8')))
                while m != '':
                    recvdStrs.append(m)
                    if r == '':
                        break
                    else:
                        m, r = matchJSONStr(r)
                unmatchedStr = r
                for recvdStr in recvdStrs:
                    try:
                        data = json.loads(recvdStr)
                        t = data['type']
                        # print('Received a json object:', t)
                        if t == 'create_session':
                            if data['graph_type'] == 'Tree':
                                attris = []
                                if 'attributes' in data:
                                    attris = data['attributes']
                                self.initSessionSignal.emit(
                                    data['session_id'], data['session_descr'], attris, 'Tree')
                            elif data['graph_type'] == 'DiGraph':
                                attris = []
                                if 'attributes' in data:
                                    attris = data['attributes']
                                self.initSessionSignal.emit(data['session_id'], data['session_descr'], attris, 'DiGraph')
                            else:
                                print('Unknown graph type:',
                                      data['graph_type'])
                        elif t == 'remove_session':
                            self.v.sessions.pop(data['session_id'])
                        elif t == 'add_node':
                            nodeProps = data['node']
                            # print('adding node', nodeProps['id'], 'to', data['session_id'])
                            a = affect.AddNodeAffect(nodeProps)
                            # a = affect.AddNodeAffect(data['node']['id'], data['node']['label'], data['node']['state'])
                            # self.v.putAffect(data['session_id'], a)
                            self.affectSignal.emit(data['session_id'], a)
                        elif t == 'add_edge':
                            # print('adding edge', data['from_id'], '-->', data['to_id'], 'to', data['session_id'])
                            a = None
                            if 'label' in data:
                                a = affect.AddEdgeAffect(data['from_id'], data['to_id'], data['label'])
                            else:
                                a = affect.AddEdgeAffect(data['session_id'], data['from_id'], data['to_id'])
                            # self.v.putAffect(data['session_id'], a)
                            self.affectSignal.emit(data['session_id'], a)
                        elif t == 'highlight_node':
                            sid = data['session_id']
                            nid = data['node_id']
                            self.affectSignal.emit(sid, affect.HighlightNodeAffect(nid))
                        elif t == 'clear_color':
                            sid = data['session_id']
                            self.affectSignal.emit(sid, affect.ClearColorAffect())
                        elif t == 'request':
                            print('VMDV received a request message')
                        elif t == 'response':
                            print('vmdv received response', data['request_name'])
                            sid = data['session_id']
                            rid = data['request_id']
                            result = data['result']

                            pr = self.v.pendingRequests
                            if rid not in pr:
                                print('There is no pending request', rid)
                            else:
                                rname, rargs = pr[rid]
                                pr.pop(rid)
                                if rname == 'zone_aircraft_number':
                                    self.affectSignal.emit(sid, affect.ParseResponseAffect(rname, rargs, result))
                                    self.v.responseCache[(rname, rargs['zone'])] = result
                                elif rname == 'sub_formula':
                                    self.affectSignal.emit(sid, affect.SubFormulaAffect(rname, rargs, result))
                                    self.v.responseCache[(rname, rargs['nid'])] = result
                                elif rname == 'show_rule':
                                    self.affectSignal.emit(sid, affect.ShowRuleAffect(rname, rargs, result))
                                    self.v.responseCache[(rname, rargs['rule'])] = result
                                else:
                                    print('unknown response', rname)
                        elif t == 'set_proof_rule':
                            sid = data['session_id']
                            nid = data["node_id"]
                            rule = data["rule"]
                            self.affectSignal.emit(sid, affect.SetProofRuleAffect(nid, rule))
                        elif t == 'remove_subproof':
                            sid = data['session_id']
                            nid = data['node_id']
                            self.affectSignal.emit(sid, affect.RemoveSubproofAffect(nid))
                        elif t == 'change_node_state':
                            sid = data['session_id']
                            nid = data['node_id']
                            new_state = data['new_state']
                            self.affectSignal.emit(sid, affect.ChangeNodePropAffect(nid, 'state', new_state))
                        elif t == 'feedback':
                            if data['status'] == 'OK':
                                print('Session received feedback from the prover:', data['session_id'], ',', data['status'])
                            else:
                                print('Session received feedback from the prover:', data['session_id'], ',', data['status'], ',', data['error_msg'])
                        else:
                            print('Unknown type of message:', data['type'])
                    except json.decoder.JSONDecodeError:
                        if recvdStr != '':
                            print('json loads error:', recvdStr)
                        pass
        except socket.error:
            msgThread.stop()

    def stop(self):
        self.sock.close()
        self.terminate()

class Message:
    @abc.abstractmethod
    def toStr(self):
        pass

class ClearColorMessage(Message):
    def __init__(self, sid):
        self.sid = sid

    def toStr(self):
        return (json.dumps({'type': 'clear_color', 'session_id': self.sid}))+'\n'

class HighlightNodeMessage(Message):
    def __init__(self, sid, nid):
        self.sid = sid
        self.nid = nid

    def toStr(self):
        data = {
            'type': 'highlight_node',
            'session_id': self.sid,
            'node_id': self.nid
        }
        return (json.dumps(data))+'\n'

class RemoveSubproofMessage(Message):
    def __init__(self, sid, nid):
        self.sid = sid
        self.nid = nid
    def toStr(self):
        data = {
            'type': 'remove_subproof',
            'session_id': self.sid,
            'node_id': self.nid
        }
        return (json.dumps(data))+'\n'

class ExpandCutMessage(Message):
    def __init__(self, sid, nid, cutname):
        self.sid = sid
        self.nid = nid
        self.cutname = cutname
    def toStr(self):
        data = {
            'type': 'expand_cut',
            'session_id': self.sid,
            'node_id': self.nid,
            'cut_name': self.cutname
        }
        return (json.dumps(data))+'\n'


class RequestMessage(Message):
    def __init__(self, sid, rname, rid, args):
        self.sid = sid
        self.rname = rname
        self.rid = rid
        self.args = args

    def toStr(self):
        data = {
            'type': 'request',
            'session_id': self.sid,
            'request_id': self.rid,
            'request_name': self.rname,
            'args': self.args
        }
        return (json.dumps(data))+'\n'

class ResponseMessage(Message):
    def __init__(self, sid, rid, result):
        self.sid = sid
        self.rid = rid
        self.result = result
    def toStr(self):
        data = {
            'type': 'response',
            'session_id': self.sid,
            'request_id': self.rid,
            'result': self.result
        }
        return (json.dumps(data))+'\n'

class Sender(QThread):
    def __init__(self, v, sock, parent=None):
        QThread.__init__(self, parent)
        self.v = v
        self.sock = sock
        self.sockFile = self.sock.makefile(mode='w')

    def run(self):
        print('Sender thread start...')
        while True:
            m = self.v.fetchMsg()
            self.sockFile.write(m.toStr())
            # self.sock.sendall(m.toStr().encode('utf-8'))
            self.sockFile.flush()

    def stop(self):
        # self.sock.stop()
        self.sockFile.close()
        self.terminate()
