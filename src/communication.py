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

IP = '192.168.1.5'  #raspberyr's IP


class Communication:
    def __init__(self,IP=""):

        self.print_errors = False

        self.IP = IP
        #self.client = socket.socket()  # Create a socket object
        self.port = 2525  # Reserve a port for your service.

        # refence: http://www.binarytides.com/programming-udp-sockets-in-python/
        # create dgram udp socket
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print 'Failed to create socket'
            sys.exit()


    def sentData(self, data, IP = ""):

        if IP == "":
            IP = self.IP

        try:
            # Set the whole string
            self.client.sendto(str(data), (IP, self.port))
            return True

        except socket.error, msg:
            if self.print_errors:
                print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            return False

            # sys.exit()

    def receiveData(self, timeout = 0.1, bufferSize = 1024):
        self.client.settimeout(timeout)
        d = []
        try:
            d = self.client.recvfrom(bufferSize)
            return [True,d]
        except socket.error, msg:
            if self.print_errors:
                if msg[0] == "timed out":
                        print 'Error Code : ' + str(msg[0])
                else:
                        print 'Error Code : ' + str(msg[0])   + ' Message ' + msg[1]
            return [False,d]


    def closeSocket(self):
        self.client.close  # Close the socket when done

    def setPrintErrors(self,val):
        self.print_errors = val

if __name__ == '__main__':
    com_ = Communication(IP)
    com_.sentData(3)

    f = open('img/tux3.jpg', 'r+')
    jpgdata = f.read()
    #com_.sentData(jpgdata)
    f.close()

    # only for test - Show in cv2 window the image
    import cv2
    import numpy
    import matplotlib.image as mpimg
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.imshow('image', mpimg.imread('img/tux3.jpg'))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    com_.closeSocket()



