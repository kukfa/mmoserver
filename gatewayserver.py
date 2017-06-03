#!/usr/bin/env python3

import asyncio
import binascii
import struct
import time
import zlib

gatewayPort = 7777


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

            if (pktType == 3):
                if (secondByte == 0):
                    self.connectUserManagerClient()
                if (secondByte == 1):
                    self.rosterUserManagerClient()
                    self.connectCharacterManagerClient()

            if (pktType == 4):
                if (secondByte == 0):
                    self.connectCharacterManagerClient()
                if (secondByte == 2):
                    pass
                if (secondByte == 3):
                    self.sendCharacter()
                    #self.clientHash()
                if (secondByte == 5):
                    self.confirmCharSelection(decompressed[2:])

            if (pktType == 9):
                if (secondByte == 0):
                    self.connectGroupClient()
                    #self.testPacket()
                    self.addUserGroupClient()
                    #self.loadZone('Town')

            if (pktType == 13):
                if (secondByte == 6):
                    """
                    self.zoneClientInit()
                    time.sleep(1)
                    self.pathManagerBudget()
                    time.sleep(1)
                    self.testPacket()
                    self.testEntityCreate()
                    time.sleep(1)
                    self.connectClientEntityManager()
                    #self.testPacket()
                    """
            else:
                pass
        else:
            pass


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
        print("Decompressed: " + data[3:].hex())
        self.transport.write(packet)


    def closeSocket(self, reason):
        print(reason)
        self.transport.close()


    def initPacket(self):
        pktType = b'\x02' #08
        padding = b'\x01' + b'\x00\x32'[::-1]
        data = padding + b'\x03'#\xBA\xAD\xF0\x0D'
        self.sendPacket(pktType, data)
        #self.sendZlibPacket1(pktType, data)

        pktType = b'\x02'
        data = b'\x00' + b'\x03\x00'
        data += b'\x01' + b'\x00\x32'[::-1]
        self.sendPacket(pktType, data)


    def connectCharacterManagerClient(self):
        pktType = b'\x02'
        padding = b'\x01' + b'\x00\x32'[::-1]
        channelType = b'\x04'
        data = padding + channelType + b'\x00'
        self.sendPacket(pktType, data)


    def confirmCharSelection(self, charID):
        pktType = b'\x02'
        padding = b'\x01' + b'\x00\x32'[::-1]
        channelType = b'\x04'
        data = padding + channelType + b'\x05'
        data += charID
        self.sendPacket(pktType, data)


    def connectGroupClient(self):
        pktType = b'\x02'
        channelType = b'\x09'
        data = b'\x01' + b'\x00\x32'[::-1]
        data += channelType + b'\x30'
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x01'
        data += b'\x01'
        self.sendPacket(pktType, data)


    def addUserGroupClient(self):
        pktType = b'\x02'
        channelType = b'\x09'
        data = b'\x01' + b'\x00\x32'[::-1]
        data += channelType + b'\x42'
        data += b'\x00'*4

        data += b'\x02\x03\x04\x05'[::-1]
        data += 'testchar'.encode('utf-8') + b'\x00'
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x00'
        self.sendPacket(pktType, data)


    def testPacket(self):
        pktType = b'\x02'
        channelType = b'\x06'
        data = b'\x01' + b'\x00\x32'[::-1]
        data += channelType + b'\x03'
        data += b'\x00'
        self.sendPacket(pktType, data)


    def connectUserManagerClient(self):
        pktType = b'\x02'
        padding = b'\x01' + b'\x00\x32'[::-1]
        channelType = b'\x03'
        data = padding + channelType + b'\x00'
        data += 'testString'.encode('utf-8') + b'\x00'
        self.sendPacket(pktType, data)


    def rosterUserManagerClient(self):
        pktType = b'\x02'
        padding = b'\x01' + b'\x00\x32'[::-1]
        channelType = b'\x03'
        data = padding + channelType + b'\x01'
        data += b'\x01' + b'\x01'
        data += b'\x00'*4
        data += b'\x00'*4
        self.sendPacket(pktType, data)


    def testEntityCreate(self):
        pktType = b'\x02'
        padding = b'\x01' + b'\x00\x0c'[::-1]
        channelType = b'\x07'
        data = padding + channelType + b'\x01'

        data += b'\x00\x01'[::-1]                       # entity ID?
        
        data += b'\xFF'                         # GCClassRegistry::readType
        data += 'Player'.encode('utf-8') + b'\x00'

        data += b'\x06'
        self.sendPacket(pktType, data)

        data = padding + channelType + b'\x02'
        data += b'\x00\x01'[::-1]

        data += 'testPlayer'.encode('utf-8') + b'\x00'  # Player::readInit
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\xFF'
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x02\x03\x04\x05'[::-1]

        data += b'\xFF'                         # GCClassRegistry::readType
        data += 'Player'.encode('utf-8') + b'\x00'

        data += 'anotherString'.encode('utf-8') + b'\x00'
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x06'
        self.sendPacket(pktType, data)


    def zoneClientInit(self):
        pktType = b'\x02' #1a'
        channelType = b'\x0d'
        data = b'\x01' + b'\x00\x0c'[::-1] 
        data += channelType + b'\x01' + b'\x7C\x9E\x93\x6D'[::-1]
        #                               not used during zone load?
        self.sendPacket(pktType, data)
        #self.sendZlibPacket3(pktType, data)

        data = b'\x01' + b'\x00\x0c'[::-1]
        data += channelType + b'\x05'
        data += b'\xFF\xFF\xFF\xFF'[::-1] + b'\x10\x20\x30\x40'[::-1]
        #                                   not used during zone load?
        self.sendPacket(pktType, data)
        #self.sendZlibPacket3(pktType, data)


    def pathManagerBudget(self):
        pktType = b'\x02' #1a'
        channelType = b'\x07'
        data = b'\x01' + b'\x00\x0c'[::-1]
        data += channelType + b'\x0d'
        data += b'\x7C\x9E\x93\x6D'[::-1]           # unknown 4 bytes
        data += b'\x7C\x9E\x93\x6D'[::-1]           # unknown 4 bytes
        data += b'\x7C\x9E\x93\x6D'[::-1]           # unknown 4 bytes

        data += b'\x7C\x9E\x93\x6D'[::-1]           # unknown 4 bytes
        data += b'\x00\x1e'[::-1]                   # perUpdate
        data += b'\x00\x07'[::-1]                   # perPath

        data += b'\x06'                             # end loop
        self.sendPacket(pktType, data)
        #self.sendZlibPacket3(pktType, data)


    def connectClientEntityManager(self):
        pktType = b'\x02'
        channelType = b'\x07'
        data = b'\x01' + b'\x00\x0c'[::-1]
        data += channelType + b'\x46'
        self.sendPacket(pktType, data)
        # sendZlibPacket3


    # valid zoneToLoad: Town, pvp_start
    # Spawnpoints(?): Start, Waypoint, Respawn
    def loadZone(self, zoneToLoad):
        pktType = b'\x02' #1a'
        channelType = b'\x0d'
        data = b'\x01' + b'\x00\x0c'[::-1]
        data += channelType + b'\x00'
        data += zoneToLoad.encode('utf-8') + b'\x00'
        #data += b'\x7C\x9E\x93\x6D'[::-1]
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x00'                             # number of (something)

#        data += b'\xFF'
#        data += 'ZoneDef'.encode('utf-8') + b'\x00'

        data += b'\x02\x03\x04\x05'[::-1]           # BaseLoadingScreen
        self.sendPacket(pktType, data)
        #self.sendZlibPacket3(pktType, data)


    def sendCharacter(self):
        pktType = b'\x02'
        padding = b'\x01' + b'\x00\x32'[::-1]
        channelType = b'\x04'
        data = padding + channelType + b'\x03'
        data += b'\x01'                             # num chars being sent
        data += b'\x02\x03\x04\x05'                 # character ID
        data += b'\x2D'                             # version number

        data += b'\x14\xfa\x62\x92'[::-1]           # native class -> Player
        data += b'\x14\xfa\x62\x92'[::-1]
        data += 'test haaaa'.encode('utf-8') + b'\x00'
        data += b'\x00'*4                           # number of nodes to read
        data += b'\x14\xfa\x62\x92'[::-1]           # GCObject -> Player

        data += b'\x7c\x9b\x0c\x46'[::-1]           # Property -> Name
        data += 'plzwork'.encode('utf-8') + b'\x00'

        data += b'\x00'*4

        data += 'test1234'.encode('utf-8') + b'\x00'
        data += 'test4321'.encode('utf-8') + b'\x00'

        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x02\x03\x04\x05'[::-1]

        data += b'\x2d'
        data += b'\xf2\xb1\xe0\x64'[::-1]           # native class -> Avatar
        data += b'\xf2\xb1\xe0\x64'[::-1]
        data += 'test fuuuu'.encode('utf-8') + b'\x00'

        #data += b'\x00'*5
        data += b'\x00\x00\x00\x06'[::-1]           # number of nodes to read

        data += b'\x2d'
        data += b'\x09\xc2\x6f\x07'[::-1]           # Node -> Modifiers
        data += b'\x00'*9
        data += b'\x09\xc2\x6f\x07'[::-1]
        data += b'\x00'*4

        data += b'\x2d'
        data += b'\xca\x2b\xc0\xc4'[::-1]           # Node -> Manipulators
        data += b'\x00'*9
        data += b'\xca\x2b\xc0\xc4'[::-1]
        data += b'\x00'*4
        
        data += b'\x2d'
        data += b'\x40\x0e\xd1\x75'[::-1]           # Node -> UnitBehavior
        data += b'\x00'*9
        data += b'\xD7\x2C\x9E\x4B'[::-1]           # node GCObject -> avatar.base.UnitBehavior
        data += b'\x00'*4

        data += b'\x2d'
        data += b'\x1b\xeb\xf0\x97'[::-1]           # Node -> Skills
        data += b'\x00'*9
        data += b'\x81\xBE\x54\xED'[::-1]           # node GCObject ->avatar.base.Skills
        data += b'\x00'*4

        data += b'\x2d'
        data += b'\x5b\xb7\xbf\x9d'[::-1]           # Node -> Equipment
        data += b'\x00'*9
        data += b'\xff\x4e\xcc\x33'[::-1]           # node GCObject -> avatar.base.Equipment
        data += b'\x00'*4

        data += b'\x2d'
        data += b'\xe9\xab\x2a\x48'[::-1]           # Node -> UnitContainer
        data += b'\x00'*9
        data += b'\xe9\xab\x2a\x48'[::-1]
        data += b'\x00'*4

        data += b'\x00'

        data += b'\x74\xf0\x57\xd6'[::-1]           # GCObject -> FighterMale

        data += b'\x7C\x9D\xF4\x3a'[::-1]           # Property -> Skin
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
        data += b'\x01'*4

        data += b'\x11\x01\xe4\xa3'[::-1]           # Property -> LastKnownQueueLevel
        data += b'\x01'*4

        data += b'\xc3\x4e\x12\xc3'[::-1]           # Property -> HasBlingGnome
        data += b'\x00'*4

        data += b'\x0f\xda\xbc\x3d'[::-1]           # Property -> Level
        data += b'\x00\x00\x00\x64'[::-1]

        data += b'\x1a\x64\x28\x47'[::-1]           # Property -> HitPoints
        data += b'\x00\x03\xd0\x90'[::-1]

        data += b'\xcd\xc4\xd6\xff'[::-1]           # Property -> ManaPoints
        data += b'\x00\x03\xd0\x90'[::-1]

        data += b'\x35\x46\x9c\x4d'[::-1]           # Property -> Experience
        data += b'\x00\x03\xD0\x90'[::-1]

        data += b'\x09\x95\xa0\x76'[::-1]           # Property -> AttributePoints
        data += b'\x00\x00\x00\x64'[::-1]

        data += b'\xe5\xa8\xe0\x88'[::-1]           # Property -> ReSpecTimer
        data += b'\x00\x00\x00\x00'[::-1]

        data += b'\x06\xb2\x18\xd1'[::-1]           # Property -> StrengthPoints
        data += b'\x00\x00\x00\x64'[::-1]

        data += b'\xdd\xdf\x76\xb5'[::-1]           # Property -> AgilityPoints
        data += b'\x00\x00\x00\x64'[::-1]

        data += b'\xe1\x54\x31\xe2'[::-1]           # Property -> ToughnessPoints
        data += b'\x00\x00\x00\x64'[::-1]

        data += b'\xb5\x24\x71\x4f'[::-1]           # Property -> PowerPoints
        data += b'\x00\x00\x00\x64'[::-1]

        data += b'\x0f\x8f\x06\x9d'[::-1]           # Property -> MaxTotalAttributePool
        data += b'\x00\x00\x00\x64'[::-1]

        data += b'\x8d\x69\x79\x00'[::-1]           # Property -> PVPRating
        data += b'\x00\x00\x05\x39'[::-1]

        data += b'\x00'*4

        data += b'\xAA'                             # not used?

        data += b'\x00'
        data += 'Normal'.encode('utf-8') + b'\x00'  # difficulty
                            # (Normal, Formidable, Extreme and Insane)
        data += b'\x02'
        data += b'\x00'

        data += b'\x02\x03\x04\x05'[::-1]                           # not used?
        self.sendPacket(pktType, data)


    # used to trigger client-side hashing function
    def clientHash(self):
        pktType = b'\x02'
        padding = b'\x66\x66\x66'
        channelType = b'\x04'
        data = padding + channelType + b'\x03'
        data += b'\x01\x02\x03\x04\x05'
        data += b'\x29'
        hashName = 'CharacterName'
        data += hashName.encode('utf-8') + b'\x00'
        self.sendPacket(pktType, data)


    def charCreate(self):
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
