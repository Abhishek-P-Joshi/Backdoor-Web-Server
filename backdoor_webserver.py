import socket
import threading
import mimetools
from StringIO import StringIO
from urlparse import urlparse
import os
import commands
import sys
import atexit
import gzip
import StringIO
import subprocess
import urllib

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        #print 'listen entered'
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        size = 2048
        #print 'listen to client entered'
        while True:
            try:
                data1 = client.recv(size)

                if not data1:
                    break
                request, data= data1.split('\r\n',1)
                #print request
                get,fullstring,http1=request.split(' ',2)
                fullstring=urllib.unquote(fullstring)
                #print get
                #print fullstring
                #print http1
                if get!='GET' or http1!='HTTP/1.1':
                    client.send('HTTP/1.1 404 Not Found \r\n')
                    client.send('Content-Type: text/plain \n')
                    client.send('\r\n')
                else:
                    fullstring=urlparse(fullstring)
                    newpath=fullstring.path
                    if '/exec' in newpath:
                        allpath,onlypath=newpath.split('exec/',1)
                        onlypath=urllib.unquote(onlypath)
                        #print onlypath
                        if onlypath[0]=='v' and onlypath[1]=='i' and onlypath[2]=='m':
                            client.send('HTTP/1.1 200 OK \r\n')
                            client.send('Content-Type: text/plain \n')
                            #client.send('VIM')
                            client.send('\r\n')
                        else:
                            if 'curl' in onlypath:
                                curl,curlpath=onlypath.split(' ',1)
                                #print curlpath
                                #curlpath=urllib.quote(curlpath)
                                curlpath=curlpath.replace(" ", "%20")
                                #print curlpath
                                onlypath=curl+' '+curlpath
                                #nogzip=1
                                #print onlypath

                                op1 = subprocess.Popen(onlypath, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                                #if op1:
                                (output1,error1)=op1.communicate()

                                #else:
                                #    error1=str(op1.stderr.read())

                                client.send('HTTP/1.1 200 OK \r\n')
                                client.send('Content-Type: text/plain \n')
                                client.send('\r\n'+output1)
                                #client.send(str(output))
                            else:

                                op = subprocess.Popen(onlypath, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                                if op:
                                    output=str(op.stdout.read())
                                else:
                                    error=str(op.stderr.read())

                                #out=StringIO.StringIO()
                                #with gzip.GzipFile(fileobj=out, mode="w") as f:
                                #    f.write(output)
                                #out1=out.getvalue()
                                #out2=str(out1)
                                #content_length=len(out1)
                                #content_length=str(content_length)
                                client.send('HTTP/1.1 200 OK \r\n')
                                #client.send('Content-Encoding: gzip \r\n')
                                #client.send('Content-Length: '+content_length+'\r\n')
                                client.send('Content-Type: text/plain \n')
                                client.send('\r\n')
                                client.send(output)


                    else:
                        client.send('HTTP/1.1 404 Not Found \r\n')
                        client.send('Content-Type: text/plain \n')
                        client.send('\r\n')
                        client.send('INVALID COMMAND')
                        #client.send('\n')


                #print data
                #if data:
                    #response = data
                #client.send(data)
                #else:
                #client.send('Client disconnected')
                client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                client.close()
            except:
                client.close()
                client.close()
                #self.sock.shutdown(socket.SHUT_RDWR)
                #self.sock.close()
                return False

if __name__ == "__main__":
    port=sys.argv
    port=port[1]
    port=int(port)
    ThreadedServer('',port).listen()

