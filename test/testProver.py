import sys
import socket
import json

nodes = {}
edges = {}
rules = {}


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


def send(jsonfile, sock):
    jsons = open(jsonfile, 'r')
    while True:
        jsonline = jsons.readline()
        if not jsonline:
            break
        data = json.loads(jsonline)
        if data["type"] == 'add_node':
            nodes[data['node']['id']] = data['node']['label']
        elif data['type'] == 'add_edge':
            edges[data['from_id']] = data['to_id']
            rules[data['from_id']+'->'+data['to_id']] = data['label']
        sock.send(jsonline.encode('utf-8'))


if __name__ == "__main__":
    ip = sys.argv[1]
    jsonfile = sys.argv[2]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, 3333))
    send(jsonfile, sock)
    # starting receiving from vmdv
    unmatchedStr = ''
    sockFile = sock.makefile(mode='w')
    while True:
        recvdBytes = sock.recv(4096)
        recvdStrs = []
        m, r = matchJSONStr(unmatchedStr + (recvdBytes.decode('utf-8')))
        while m != '':
            recvdStrs.append(m)
            if r == '':
                break
            else:
                m, r = matchJSONStr(r)
        unmatchedStr = r
        for recvdStr in recvdStrs:
            data = json.loads(recvdStr)
            if data['type'] == 'request':
                sid = data['session_id']
                rid = data['request_id']
                rname = data['request_name']
                if rname == 'sub_formula':
                    nid = data['args']['nid']
                    nlabel = nodes[nid]
                    responseNids = []
                    for tmpNid in nodes:
                        tmpNlabel = nodes[tmpNid]
                        index = tmpNlabel.find('{')
                        if nlabel.find(tmpNlabel[0:index-1]) != -1:
                            responseNids.append(tmpNid)
                    responseStr = ''
                    for rnid in responseNids:
                        responseStr = responseStr + rnid + ','
                    if responseStr != '':
                        responseStr = responseStr[0:len(responseStr)-1]
                    response = {
                        'type': 'response',
                        'session_id': sid,
                        'request_id': rid,
                        'request_name': rname,
                        'result': {'nids': responseStr}
                    }
                    sentStr = json.dumps(response)+'\n'
                    sock.send(sentStr.encode('utf-8'))
                    # sockFile.write(json.dumps(response))
                    # sockFile.flush()
                    print(json.dumps(response))