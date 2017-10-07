#!/usr/bin/env python3

import asyncio
import binascii
import struct
import time
import zlib

from constants import *
from charactermanager import CharacterManager
from entitymanager import EntityManager
from groupserver import GroupServer
from usermanager import UserManager
from zoneserver import ZoneServer


characterManager = CharacterManager()
entityManager = EntityManager()
groupServer = GroupServer()
userManager = UserManager()
zoneServer = ZoneServer()


class GatewayServer(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.client = (transport.get_extra_info('peername')[0] + ":"    # IP
            + str(transport.get_extra_info('peername')[1]))             # port
        print("Connection from: " + self.client)
        
        self.msgSource = b'\xdd' + b'\x00\x7b'[::-1]
        self.msgDest = b'\x01' + b'\x00\x32'[::-1]
        
        self.characterManager = characterManager
        self.entityManager = entityManager
        self.groupServer = groupServer
        self.userManager = userManager
        self.zoneServer = zoneServer


    def connection_lost(self, exc):
        print("Connection closed: " + self.client)

    
    def close_socket(self, reason):
        print(reason)
        self.transport.close()


    def data_received(self, data):
        print("[R] Data: " + data.hex())
        zlibSplit = data.rpartition(b'\x78\x9c')
        zlibData = zlibSplit[1] + zlibSplit[2]
        #print("Compressed:   " + zlibData.hex())
        
        decompressed = zlib.decompress(zlibData)
        print("Decompressed: " + decompressed.hex())
        if len(decompressed) == 0: return
        channelType = decompressed[0]
        functionID = decompressed[1]
        
        if (channelType == CHANNEL_INIT):
            self.sessionKey = decompressed[1:5]
            self.initPacket()
        elif (channelType == CHANNEL_USERMANAGER):
            userManager.process(self, decompressed)
        elif (channelType == CHANNEL_CHARACTERMANAGER):
            characterManager.process(self, decompressed)
        elif (channelType == CHANNEL_GROUPSERVER):
            groupServer.process(self, decompressed)
        elif (channelType == CHANNEL_ZONESERVER):
            zoneServer.process(self, decompressed)


    def send_zlib1(self, pktType, data):
        packet = pktType                            # byte
        packet += self.msgDest                  # unknown
        zlibMsg = zlib.compress(data)
        packet += struct.pack("!I", len(zlibMsg)+12)[1:][::-1]# compressed size
        packet += b'\x00'
        packet += self.msgSource
        packet += b'\x01\x00\x01\x00\x00' # ??
        packet += struct.pack("<I", len(data))
        packet += zlibMsg                           # compressed zlib data
        print("[S-Z1] Data: " + packet.hex())
        print("Decompressed: " + data.hex())
        self.transport.write(packet)


    def send_zlib2(self, pktType, data):
        packet = pktType                            # byte
        packet += self.msgDest                   # unknown
        zlibMsg = zlib.compress(data)
        packet += struct.pack("<I", len(zlibMsg)+4) # compressed size
        packet += zlibMsg                           # compressed zlib data
        packet += struct.pack("<I", len(data))      # uncompressed size
        print("[S-Z2] Data: " + packet.hex())
        self.transport.write(packet)


    def send_zlib3(self, pktType, data):
        packet = pktType                            # byte
        packet += self.msgDest                   # unknown
        zlibMsg = zlib.compress(data)
        packet += struct.pack("<I", len(zlibMsg)+7) # compressed size
        if (pktType == b'\x0a'):
            packet += b'\x00\x03\x00'
        else:
            packet += self.msgSource
        packet += struct.pack("<I", len(data))      # uncompressed size
        packet += zlibMsg                           # compressed zlib data
        print("[S-Z3] Data: " + packet.hex())
        print("Decompressed: " + data.hex())
        self.transport.write(packet)
        

    def sendPacket(self, pktType, data):
        packet = pktType
        packet += self.msgDest
        packet += struct.pack("<I", len(data))
        packet += data
        print("[S] Data: " + packet.hex())
        print("Decompressed: " + data[3:].hex())
        self.transport.write(packet)


    def initPacket(self):
        # GatewayClient::UpdateAuthorize
        pktType = b'\x0a'
        data = b'\x03'
        self.send_zlib3(pktType, data)

        # DFCMessageClient::processConnected
        data = b'\x01' + b'\x32\x00'
        self.send_zlib3(pktType, data)


def main():
    loop = asyncio.get_event_loop()
    coroutine = loop.create_server(GatewayServer, host=None, port=GATEWAY_PORT)
    server = loop.run_until_complete(coroutine)
    
    for socket in server.sockets:
        print("Listening on: " + socket.getsockname()[0] + ":" +
            str(socket.getsockname()[1]))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == "__main__":
    main()

