import struct

from constants import *


class UserManager:
    def __init__(self):
        self.pktType = b'\x0e'
        self.channelType = struct.pack("B", CHANNEL_USERMANAGER)
        
        
    def process(self, gateway, packet):
        functionID = packet[1]
        if (functionID == FUNC_USERMANAGER_CONNECT):
            self.connect(gateway)
        elif (functionID == FUNC_USERMANAGER_ROSTER):
            self.roster(gateway)


    def connect(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_USERMANAGER_CONNECT)
        data += 'plzwork'.encode('utf-8') + b'\x00'
        gateway.send_zlib1(self.pktType, data)


    def roster(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_USERMANAGER_ROSTER)
        data += b'\x00' + b'\x00'
        data += b'\x00'*4
        data += b'\x00'*4
        gateway.send_zlib1(self.pktType, data)
