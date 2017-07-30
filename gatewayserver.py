#!/usr/bin/env python3

import asyncio
import binascii
from dfc import DFCObject
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
        
        player = DFCObject('Player', 33752069, 'plzwork', 'Player')
        avatar = DFCObject('Avatar', None, None, 'avatar.classes.FighterMale')
        
        modifiers = DFCObject('Modifiers', None, None, 'Modifiers')
        avatar.addNode(modifiers)

        manipulators = DFCObject('Manipulators', None, None, 'Manipulators')
        avatar.addNode(manipulators)

        unitbehavior = DFCObject('UnitBehavior', None, None, 'avatar.base.UnitBehavior')
        avatar.addNode(unitbehavior)

        skills = DFCObject('Skills', None, None, 'avatar.base.skills')
        avatar.addNode(skills)

        equipment = DFCObject('Equipment', None, None, 'avatar.base.Equipment')
        weapon = DFCObject('MeleeWeapon', None, None, 'items.pal.1HMacePAL.Normal001')
        weapon.addProperty('ID', 10)
        weapon.addProperty('Level', 1)
        equipment.addNode(weapon)
        avatar.addNode(equipment)

        unitcontainer = DFCObject('UnitContainer', None, None, 'UnitContainer')
        #avatar.addNode(unitcontainer)
        # might be loading extra data -- revisit
        
        avatar.addProperty('Skin', 0)
        avatar.addProperty('Face', 0)
        avatar.addProperty('FaceFeature', 0)
        avatar.addProperty('Hair', 0)
        avatar.addProperty('HairColor', 0)
        avatar.addProperty('TotalWorldTime', 10)
        avatar.addProperty('LastKnownQueueLevel', 0)
        avatar.addProperty('HasBlingGnome', 1)
        avatar.addProperty('Level', 100)
        avatar.addProperty('HitPoints', 1337)
        avatar.addProperty('ManaPoints', 1337)
        avatar.addProperty('Experience', 1337)
        avatar.addProperty('AttributePoints', 100)
        avatar.addProperty('ReSpecTimer', 0)
        avatar.addProperty('StrengthPoints', 100)
        avatar.addProperty('AgilityPoints', 100)
        avatar.addProperty('ToughnessPoints', 100)
        avatar.addProperty('PowerPoints', 100)
        avatar.addProperty('MaxTotalAttributePool', 100)
        avatar.addProperty('PVPRating', 1337)
        
        player.addNode(avatar)
        player.addProperty('Name', 'plzwork')

        data += player.serialize()

        data += 'plzwork'.encode('utf-8') + b'\x00'
        data += 'plzwork'.encode('utf-8') + b'\x00'

        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x02\x03\x04\x05'[::-1]
        
        avatarmetrics = DFCObject('AvatarMetrics', None, None, 'AvatarMetrics')
        # PlayTime
        extraData = (b'\x00'*4 + b'\x00'*4 + b'\x00'*4 + b'\x00'*4 + b'\x00'*4)
        
        # ZoneToPlayTimeMap
        extraData += b'\x00'*4
        #data += 'test'.encode('utf-8') + b'\x00'
        #data += b'\x00'
        #data += b'\x00'*20
        
        # LevelToPlayTimeMap
        extraData += b'\x00'*4
        #data += b'\x00'*4
        #data += b'\x00'*20   # incomplete

        # GoldStats
        extraData += (b'\x00'*8 + b'\x00'*8 + b'\x00'*8 + b'\x00'*8 + b'\x00'*8)

        # LevelToGoldStatsMap
        extraData += b'\x00'*4
        #data += b'\x00'*4
        #data += b'\x00'*8
        #data += b'\x00'*8
        #data += b'\x00'*8
        #data += b'\x00'*8
        #data += b'\x00'*8
        
        # SkillUseMap
        extraData += b'\x00'*4
        #data += 'fuck'.encode('utf-8') + b'\x00'
        #data += b'\x00'*4

        # DeathMap
        extraData += b'\x00'*4
        #data += 'test2'.encode('utf-8') + b'\x00'
        #data += b'\x00'*4

        # SkillUseMap
        extraData += b'\x00'*4
        #data += 'fuck'.encode('utf-8') + b'\x00'
        #data += b'\x00'*4

        avatarmetrics.addExtraData(extraData)
        data += avatarmetrics.serialize()

        data += b'\x00'
        data += b'\xAA'                             # not used?
        data += b'\x00'
        data += 'Normal'.encode('utf-8') + b'\x00'  # difficulty (Normal, Formidable, Extreme and Insane)
        data += b'\x02'
        data += b'\x00'
        data += b'\x02\x03\x04\x05'[::-1]    # not used?
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

