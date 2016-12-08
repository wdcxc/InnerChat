#!/bin/env python
#coding:utf-8
import socket
import threading
sendMsgLock = threading.Semaphore(value=1)

class Server(object):
    def __init__(self,serverPort=6666,connsNum=5,invCode='zzzz'):
        self.__serverHost = '127.0.0.1'
        self.__serverPort = serverPort
        self.connsNum  = connsNum
        self.whiteIps = []
        self.blockIps = []
        self.__msgQueue = []
        self.__aliveConns = {}
        self.__invCode = invCode

    def run(self):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.bind((self.__serverHost,self.__serverPort))
        sock.listen(self.connsNum)
        print "[init]server startup"
        threading.Thread(target=self.sendMsg).start()
        while True:
            conn,clientAddr = sock.accept()
            print "[+]new connection:",clientAddr
            aliveConnKey = clientAddr[0]+":"+str(clientAddr[1])
            if aliveConnKey not in self.__aliveConns:
                if self.validConn(conn,aliveConnKey):
                    threading.Thread(target=self.connClient,args=(conn,aliveConnKey,)).start()
        sock.close()

    def validConn(self,conn,aliveConnKey):
        recvData = conn.recv(1024)
        print "recv:" + aliveConnKey + ":" +recvData
        recvData = recvData.split("#")
        msgCode = recvData[0]
        if msgCode == "0001":
            if recvData[1] != self.__invCode:
                conn.sendall("sorry,invcode error")
                conn.close()
                print "refuse conn:" + aliveConnKey
                return False
            else:
                self.__aliveConns[aliveConnKey] = {"conn": conn}
                self.showAliveConns()
                conn.sendall("welcome")
                print "accept conn:" + aliveConnKey
                return True

    def connClient(self,conn,aliveConnKey):
        while True:
            try:
                recvData = conn.recv(1024)
                print "recv:" + aliveConnKey + ":" + recvData
                recvData = recvData.split("#")
                msgCode = recvData[0]
                if msgCode == "0002":
                    self.__aliveConns[aliveConnKey]['uname'] = recvData[1]
                    conn.sendall("setup uname success.")
                elif msgCode == "0003":
                    sendMsgLock.acquire()
                    self.__msgQueue.append(aliveConnKey+"#"+self.__aliveConns[aliveConnKey]['uname']+"#"+recvData[1])
                    sendMsgLock.release()
                else:
                    print "msg code error:"
            except Exception,e:
                print e
                conn.close()
                del self.__aliveConns[aliveConnKey]
                print "[-]"+aliveConnKey+" disconnect"
                self.showAliveConns()
                break

    def sendMsg(self):
        while True:
            if self.__aliveConns and self.__msgQueue:
                for aAddr,aConn in self.__aliveConns.items():
                    aConn['conn'].sendall(self.__msgQueue[0])
                del self.__msgQueue[0]

    def showAliveConns(self):
        print "alive connection(%s):%s"%(len(self.__aliveConns.keys()),self.__aliveConns.keys())

if __name__ == "__main__":
    serverPort = int(raw_input("setup server listen port:"))
    connsNum = int(raw_input("setup server max keepalive:"))
    invCode = raw_input("setup server invcode:")
    Server(serverPort,connsNum,invCode).run()
