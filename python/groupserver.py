import struct

from constants import *


class GroupServer:
    def __init__(self):
        self.pktType = b'\x0e'
        self.channelType = struct.pack("B", CHANNEL_GROUPSERVER)
        
        
    def process(self, gateway, packet):
        functionID = packet[1]
        if (functionID == FUNC_GROUPSERVER_CLIENTCONNECT):
            self.connect(gateway)
            gateway.zoneServer.connect(gateway, ZONE_TOWNSTON)


    def connect(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_GROUPSERVER_CONNECT)
        data += struct.pack("<I", CHAR_ID)
        data += b'\x01'
        data += b'\x01'
        gateway.send_zlib1(self.pktType, data)
