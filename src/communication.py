#!/usr/bin/python
"""
This module allows the communications between the pc and raspberry through UDP sockets.
The IP of the raspberry is useless. The important one is the IP of the PC to set into the raspberry
program.
To use the communications just initialize the class and closee the sentData method. Reading from the
raspberry is still not implemented.
"""



__author__ = "Nicola Covallero"



import socket               # Import socket module
import sys

global IP

IP = '192.168.1.3'  #raspberyr's IP


class Communication:
    def __init__(self,IP):

        self.IP = IP
        #self.client = socket.socket()  # Create a socket object
        self.port = 12345  # Reserve a port for your service.

        # refence: http://www.binarytides.com/programming-udp-sockets-in-python/
        # create dgram udp socket
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print 'Failed to create socket'
            sys.exit()

    def sentData(self, data):
        try:
            # Set the whole string
            self.client.sendto(str(data), (self.IP, self.port))

            # receive data from client (data, addr)
            #d = self.client.recvfrom(1024)
            #reply = d[0]
            #addr = d[1]
            #print 'Server reply : ' + reply
        except socket.error, msg:
            print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

    def closeSocket(self):
        self.client.close  # Close the socket when done


if __name__ == '__main__':
    com_ = Communication(IP)
    com_.sentData(3)
    com_.closeSocket()


