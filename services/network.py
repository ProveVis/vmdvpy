import sys
sys.path.append('..')
import vmdv
import socket
import json


# s = None

def listen(port):
    print('Network thread start...')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('',port))
        s.listen()
        connection, address = s.accept()
        print('Connection established with a prover: ',address)
        with connection:
            while True:
                recvdStr = connection.recv(40960)
                if not recvdStr:
                    print('network receiving data error')
                    break
                # else:
                #     print('Received Json object:', recvdStr)
                try:
                    data = json.loads(recvdStr)
                    vmdv.putJSON(data)
                except json.decoder.JSONDecodeError:
                    pass
                    # print('Json decode error:', recvdStr)
                
    
            
# def exit():
#     s.close()