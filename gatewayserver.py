#!/usr/bin/env python3

import asyncio
import binascii
import struct
import zlib

gatewayPort = 7777
randomDataBlob = b'\xa4\x61\xb8\x29\xa2\xae\xf4\xf8\xf1\xe0\x63\xa0\x27\x05\x62\xb0\x4e\xed\x8e\xa9'


class GatewayServer(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.client = (transport.get_extra_info('peername')[0] + ":"    # IP
            + str(transport.get_extra_info('peername')[1]))             # port
        print("Connection from: " + self.client)


    def connection_lost(self, exc):
        print("Connection closed: " + self.client)


    def data_received(self, data):
        # TODO check ADLER32 of zlib data
        print("[R] Data: " + data.hex())
        zlibSplit = data.rpartition(b'\x78\x9c')
        zlibData = zlibSplit[1] + zlibSplit[2]
        #print("Compressed:   " + zlibData.hex())
        decompressed = zlib.decompress(zlibData)
        print("Decompressed: " + decompressed.hex())
        if (len(decompressed) > 0):
            pktType = int(decompressed[0])
            secondByte = int(decompressed[1])
            if (pktType == 1):
                self.initPacket()
            if (pktType == 4):
                if (secondByte == 0):
                    self.pkt02()
                    #self.testPacket()
                if (secondByte == 2):
                    #self.testPacket()
                    pass
                if (secondByte == 3):
                    #self.testPacket2()
                    self.testPacket()
                    #self.testCharCreate()
                    #pass
            if (pktType == 9):
                #self.testPacket2()
                self.loadZone('Town')
            if (pktType == 13):
                self.pkt1a()
            else:
                pass
        else:
            pass
            #self.testPacket()
            #self.pkt1a()


    def sendZlibPacket1(self, pktType, data):
        packet = pktType                            # byte
        packet += b'\x99\x88\x77'                   # unknown
        zlibMsg = zlib.compress(data)
        packet += struct.pack("<I", len(zlibMsg)+4) # compressed size
        packet += struct.pack("<I", len(data))      # uncompressed size
        packet += zlibMsg                           # compressed zlib data
        print("[S-Z1] Data: " + packet.hex())
        self.transport.write(packet)


    def sendZlibPacket2(self, pktType, data):
        packet = pktType                            # byte
        packet += b'\x99\x88\x77'                   # unknown
        zlibMsg = zlib.compress(data)
        packet += struct.pack("<I", len(zlibMsg)+4) # compressed size
        packet += zlibMsg                           # compressed zlib data
        packet += struct.pack("<I", len(data))      # uncompressed size
        print("[S-Z2] Data: " + packet.hex())
        self.transport.write(packet)


    def sendZlibPacket3(self, pktType, data):
        packet = pktType                            # byte
        packet += b'\x99\x88\x77'                   # unknown
        zlibMsg = zlib.compress(data)
        packet += struct.pack("<I", len(zlibMsg)+7) # compressed size
        packet += b'\x66\x55\x44'
        packet += struct.pack("<I", len(data))      # uncompressed size
        packet += zlibMsg                           # compressed zlib data
        print("[S-Z3] Data: " + packet.hex())
        self.transport.write(packet)
        

    def sendPacket(self, pktType, data):
        packet = pktType
        packet += b'\x99\x88\x77'
        packet += struct.pack("<I", len(data))
        packet += data
        print("[S] Data: " + packet.hex())
        self.transport.write(packet)


    def closeSocket(self, reason):
        print(reason)
        self.transport.close()


    def initPacket(self):
        pktType = b'\x08'
        data = b'\x03\xBA\xAD\xF0\x0D'
        self.sendZlibPacket1(pktType, data)

        pktType = b'\x02'
        data = b'\x00\x03\x00'
        self.sendPacket(pktType, data)


    '''
    valid channelTypes: 03, 04, 06, 07, 09
    04 followed by 00: connected
    04 followed by 01: disconnected
    04 followed by 02: characterCreated
    04 followed by 03: gotCharacter
    04 followed by 04: character creation
    04 followed by 05: ?? (send 0900 packet)
    0a: TradeRequested
    0d: load into zone
    '''
    def pkt02(self):
        pktType = b'\x02'
        padding = b'\x55\x55\x55'
        channelType = b'\x04'
        data = padding + channelType + b'\x00'
        self.sendPacket(pktType, data)
        #self.sendZlibPacket1(pktType, data)


    # unknown, no idea if this is zlib or not
    def pkt04(self):
        pktType = b'\x04'
        data = b'\x00\x00'
        self.sendPacket(pktType, data)
        #self.sendZlibPacket1(pktType, data)


    # unknown, no idea if this is zlib or not
    def pkt06(self):
        pktType = b'\x06'
        data = b'\x00'
        self.sendPacket(pktType, data)
        #self.sendZlibPacket1(pktType, data)


    # playOk?
    def pkt08(self):
        pktType = b'\x08'
        data = b'\x03'
        self.sendZlibPacket1(pktType, data)


    '''
    Known valid channelTypes (tested through 0d)
    ---
    unknown purpose: 03, 04, 06, 07, 09
    0a: TradeRequested
    0d: load into zone
    '''
    def pkt0a(self):
        pktType = b'\x0a'
        channelType = b'\x0d'
        data = channelType + b'\x00'*50
        self.sendZlibPacket3(pktType, data)


    # unknown
    def pkt0c(self):
        pktType = b'\x0c'
        data = b'\x00'#randomDataBlob*3
        self.sendZlibPacket2(pktType, data)


    # unknown
    def pkt0e(self):
        pktType = b'\x0e'
        data = randomDataBlob
        self.sendZlibPacket1(pktType, data)


    # unknown
    def pkt10(self):
        pktType = b'\x10'
        data = b'\x00'
        self.sendPacket(pktType, data)
        #self.sendZlibPacket2(pktType, data) # both 2 and 3 work?


    # unknown
    def pkt12(self):
        pktType = b'\x12'
        data = randomDataBlob
        self.sendZlibPacket2(pktType, data) # might have different structure


    # unknown
    def pkt14(self):
        pktType = b'\x14'
        data = randomDataBlob
        self.sendZlibPacket2(pktType, data)


    # unknown
    def pkt16(self):
        pktType = b'\x16'
        data = randomDataBlob
        self.sendZlibPacket2(pktType, data)


    # unknown
    def pkt18(self):
        pktType = b'\x18'
        data = randomDataBlob
        self.sendZlibPacket1(pktType, data)


    '''
    Known valid channelTypes (tested through 1f)
    ---
    unknown purpose: 04, 06, 07, 09, 0f
    0a: TradeRequested
    0d: load into zone
    '''
    def pkt1a(self):
        pktType = b'\x1a'
        channelType = b'\x0d'
        data = channelType
        # valid: 01, 02, 05
        data += b'\x01' + 'Start'.encode('utf-8')
        self.sendZlibPacket3(pktType, data)

        data = channelType + b'\x05'
        self.sendZlibPacket3(pktType, data)
        
        data = channelType + b'\x02'
        self.sendZlibPacket3(pktType, data)


    # offshoot of pkt1a
    # valid zoneToLoad: Town, pvp_start
    # Spawnpoints(?): Start, Waypoint, Respawn
    def loadZone(self, zoneToLoad):
        pktType = b'\x1a'
        channelType = b'\x0d'
        data = channelType + b'\x00' + zoneToLoad.encode('utf-8')
        self.sendZlibPacket3(pktType, data)


    def testPacket(self):
        pktType = b'\x02'
        padding = b'\x66\x66\x66'
        channelType = b'\x04'
        data = padding + channelType + b'\x03'
        data += b'\x01\x02\x03\x04\x05'
        data += b'\x2D'                             # version number
        #data += "Equipment".encode('utf-8') + b'\x00'  # DFCClass name
        data += b'\xf2\xb1\xe0\x64'[::-1]           # native class -> Avatar
        data += b'\x00'*9                           # filler?
        data += b'\xf2\xb1\xe0\x64'[::-1]           # GCobject -> Avatar

        data += b'\x7C\x9D\xF4\x3A'[::-1]           # Property -> Skin
        data += b'\x00'*4

        data += b'\x7C\x96\xa7\xf4'[::-1]           # Property -> Face
        data += b'\x00'*4

        data += b'\x76\xdd\xcf\x80'[::-1]           # Property -> FaceFeature
        data += b'\x00'*4

        data += b'\x7c\x97\xc1\x89'[::-1]           # Property -> Hair
        data += b'\x00'*4

        data += b'\x6d\x69\x51\x48'[::-1]           # Property -> HairColor
        data += b'\x00'*4

        data += b'\x9b\xa4\x6f\x80'[::-1]           # Property -> TotalWorldTime
        data += b'\x00\x00\x00\x00'

        data += b'\x11\x01\xe4\xa3'[::-1]       # Property -> LastKnownQueueLevel
        data += b'\x00'*4

        data += b'\xc3\x4e\x12\xc3'[::-1]           # Property -> HasBlingGnome
        data += b'\x00'*4

        data += b'\x00'*4
        self.sendPacket(pktType, data)


    def testPacket2(self):
        pktType = b'\x02'
        padding = b'\x66\x66\x66'
        channelType = b'\x04'
        data = padding + channelType + b'\x03'
        data += b'\x01\x02\x03\x04\x05'
        data += b'\x29'
        className = 'HasBlingGnome'
        data += className.encode('utf-8') + b'\x00'
        data += b'\x00'*9
        data += b'\x29'
        data += 'Avatar'.encode('utf-8') + b'\x00'
        data += b'\x00'*9
        self.sendPacket(pktType, data)


    def testCharCreate(self):
        pktType = b'\x02'
        padding = b'\x66\x66\x66'
        channelType = b'\x04'
        data = padding + channelType + b'\x04'
        self.sendPacket(pktType, data)


def main():
    loop = asyncio.get_event_loop()
    coroutine = loop.create_server(GatewayServer, host=None, port=gatewayPort)
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

