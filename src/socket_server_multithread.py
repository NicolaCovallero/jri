import socket
import sys
import threading
import time

# This is the server and it should be run into the raspberry
# THis is working fine, but I am not able to kill the threads and also make the program stop with CTRL-C
# I should try the multiprocessing module -> solved by adding the timeout in the socket and exiFlag

HOST = ''   # Symbolic name meaning all available interfaces
PORT = 12345 # Arbitrary non-privileged port
global exitFlag
exitFlag = False

class talkingToClient(threading.Thread): 
    def __init__(self, threadID, name, udp_server):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        global data_received
        #exitFlag = False
        #while 1 and not exitFlag:
        # receive data from client (data, addr)
        udp_server.s.settimeout(1)# 1 seconds
        try:    
            d = udp_server.s.recvfrom(1024)
            data = d[0]
            addr = d[1]
            #if not data: 
            #    break


            reply = 'Received...  ' + data
            udp_server.s.sendto(reply , addr)
            print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
        except socket.timeout:
            pass

        data_received = True
        #udp_server.s.close()
        #thread.exit()
    #def exitThread(self):

class counterThread(threading.Thread): # this is just another thread to show that you can do something else
                                       # while you are waiting to receive a signal from the socket
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = 0
    def run(self):
        global exitFlag
        while 1 and not exitFlag:
            try:
                self.counter = self.counter + 1
                print "Counter: ", self.counter
            except KeyboardInterrupt:
                print 'CTRL-C pressed ... exiting...'
                exitFlag = True
                sys.exit()
            time.sleep(0.5)

class UDPServer:

    def __init__(self):
        # Datagram (udp) socket
        try :
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print 'Socket created'
        except socket.error, msg :
            print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()
         
         
        # Bind socket to local host and port
        try:
            self.s.bind((HOST, PORT))
        except socket.error , msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()
             
        print 'Socket bind complete'
         
        

if __name__ == '__main__':
    try:

        global data_received
        udp_server = UDPServer()
        data_received = True

        other_thread = counterThread(2,'Counter')
        other_thread.start()
      
        while 1:                                                                   
            if data_received:
                data_received = False
                tc_thread = talkingToClient(1, "Thread-udp_talk_to_client", 1) # Talking to Client thread
                tc_thread.start()
                #print data_received
                                
    except KeyboardInterrupt:
        print 'CTRL-C pressed ... exiting...'
        exitFlag = True
        quit()
