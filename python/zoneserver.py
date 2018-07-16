import struct
import time

from constants import *


class ZoneServer:
    def __init__(self):
        self.pktType = b'\x0e'
        self.channelType = struct.pack("B", CHANNEL_ZONESERVER)
        
        
    def process(self, gateway, packet):
        functionID = packet[1]
        if (functionID == FUNC_ZONESERVER_LOADED):
            self.ready(gateway)
            self.instanceCount(gateway)
            gateway.entityManager.interval(gateway)
            gateway.entityManager.randomSeed(gateway)
            gateway.entityManager.entityCreateInit(gateway)
            gateway.entityManager.componentCreate(gateway)
            gateway.entityManager.connect(gateway)


    def connect(self, gateway, zoneToLoad):
        data = self.channelType + struct.pack("B", FUNC_ZONESERVER_CONNECT)
        data += zoneToLoad.encode('utf-8') + b'\x00'
        data += b'\x00\x00\x00\x1e'[::-1]
        data += b'\x00'                             # number of (something)
        data += b'\x00\x00\x00\x01'[::-1]           # Townston (2)
        gateway.send_zlib1(self.pktType, data)
        

    def ready(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_ZONESERVER_READY)
        data += struct.pack("<I", CHAR_ID)
        gateway.send_zlib1(self.pktType, data)
        
        
    def instanceCount(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_ZONESERVER_INSTANCECOUNT)
        data += b'\x00\x00\x00\x01'[::-1] + b'\x00\x00\x00\x01'[::-1]
        gateway.send_zlib1(self.pktType, data)
        
