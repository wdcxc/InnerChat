#coding:utf-8

import socket
import threading

class Client(object):
    def __init__(self,serverHost,serverPort):
        self.__clientHost = socket.gethostbyname(socket.gethostname())
        self.clientPort = None
        self.serverHost = serverHost
        self.serverPort = serverPort
        self.__userName = None

    def run(self):
        print "client ip:",self.__clientHost
        clientSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        clientSock.connect((self.serverHost,self.serverPort))
        if self.createConn(clientSock):
            while True:
                if self.__userName is None:
                    self.__userName = raw_input("enter your username:")
                    sendData = "0002#"+self.__userName
                else:
                    msg = raw_input()
                    sendData = "0003#"+msg
                clientSock.sendall(sendData)
            clientSock.close()

    def createConn(self,clientSock):
        invCode = raw_input("show your invcode:")
        sendData = "0001#" + invCode
        clientSock.sendall(sendData)
        recvData = clientSock.recv(1024)
        print "server:"+recvData
        if recvData != "welcome":
            clientSock.close()
            return False
        else:
            threading.Thread(target=self.recvMsg, args=(clientSock,)).start()
            return True

    def recvMsg(self,clientSock):
        while True:
            recvData = clientSock.recv(1024)
            if recvData:
                if recvData.find("#") != -1:
                    recvData = recvData.split("#")
                    print "\n"+recvData[1]+":"+recvData[2]
                else:
                    print recvData

if __name__ == "__main__":
    serverHost = raw_input("connect server:")
    serverPort = int(raw_input("connect port:"))
    Client(serverHost=serverHost,serverPort=serverPort).run()