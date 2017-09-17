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
        self.msgSource = b'\xdd' + b'\x00\x7b'[::-1]
        self.msgDest = b'\x01' + b'\x00\x32'[::-1]


    def connection_lost(self, exc):
        print("Connection closed: " + self.client)

    
    def closeSocket(self, reason):
        print(reason)
        self.transport.close()


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
                self.sessionKey = decompressed[1:5]
                self.initPacket()

            if (pktType == 3):
                if (secondByte == 0):
                    self.connectUserManagerClient()
                if (secondByte == 1):
                    self.rosterUserManagerClient()
                    #self.connectCharacterManagerClient()

            if (pktType == 4):
                if (secondByte == 0):
                    self.connectCharacterManagerClient()
                if (secondByte == 2):
                    pass
                if (secondByte == 3):
                    #self.connectClientEntityManager()
                    #self.testEntityCreate()
                    self.sendCharacter()
                if (secondByte == 5):
                    self.confirmCharSelection(decompressed[2:])

            if (pktType == 9):
                if (secondByte == 0):
                    pass
                    self.connectGroupClient()
                    #self.testPacket()
                    self.addUserGroupClient()
                    self.loadZone('Town')

            if (pktType == 13):
                if (secondByte == 6):
                    self.zoneClientInit()
                    self.pathManagerBudget()
                    self.testPacket()
                    self.testEntityCreate()
                    self.testAvatarEntityCreate()
                    self.testEntityUpdate()
                    #self.testComponentCreate()
                    time.sleep(1)
                    self.connectClientEntityManager()
            else:
                pass
        else:
            pass


    def sendZlibPacket1(self, pktType, data):
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


    def sendZlibPacket2(self, pktType, data):
        packet = pktType                            # byte
        packet += self.msgDest                   # unknown
        zlibMsg = zlib.compress(data)
        packet += struct.pack("<I", len(zlibMsg)+4) # compressed size
        packet += zlibMsg                           # compressed zlib data
        packet += struct.pack("<I", len(data))      # uncompressed size
        print("[S-Z2] Data: " + packet.hex())
        self.transport.write(packet)


    def sendZlibPacket3(self, pktType, data):
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
        packet += self.msgDest   # message address?
        packet += struct.pack("<I", len(data))
        packet += data
        print("[S] Data: " + packet.hex())
        print("Decompressed: " + data[3:].hex())
        self.transport.write(packet)


    def initPacket(self):
        # GatewayClient::UpdateAuthorize
        pktType = b'\x0a'
        data = b'\x03'
        self.sendZlibPacket3(pktType, data)

        # DFCMessageClient::processConnected
        data = b'\x01' + b'\x32\x00'
        self.sendZlibPacket3(pktType, data)
        

    def connectUserManagerClient(self):
        pktType = b'\x0e'
        channelType = b'\x03'
        data = channelType + b'\x00'
        data += 'plzwork'.encode('utf-8') + b'\x00'
        self.sendZlibPacket1(pktType, data)


    def rosterUserManagerClient(self):
        pktType = b'\x0e'
        channelType = b'\x03'
        data = channelType + b'\x01'
        data += b'\x00' + b'\x00'
        data += b'\x00'*4
        data += b'\x00'*4
        self.sendZlibPacket1(pktType, data)


    def connectCharacterManagerClient(self):
        pktType = b'\x0e'
        channelType = b'\x04'
        data = channelType + b'\x00'
        self.sendZlibPacket1(pktType, data)
        
        
    def sendCharacter(self):
        pktType = b'\x0e'
        channelType = b'\x04'
        data = channelType + b'\x03'
        data += b'\x01'                             # num chars being sent
        data += b'\x02\x03\x04\x05'[::-1]           # character ID
        
        player = DFCObject('Player', 772586, 'plzwork', 'Player')

        # build avatar
        avatar = DFCObject('Avatar', 772587, 'avatar', 'avatar.classes.FighterMale')

        modifiers = DFCObject('Modifiers', None, None, 'Modifiers')
        zonespawn = DFCObject('AttributeModifier', None, None, 'avatar.base.ZoneSpawnInvulnerabilityModifier')
        #modifiers.addNode(zonespawn)
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
        
        inventory = DFCObject('Inventory', None, None, 'avatar.base.Inventory')
        unitcontainer.addNode(inventory)

        tradeinventory = DFCObject('Inventory', None, None, 'avatar.base.TradeInventory')
        unitcontainer.addNode(tradeinventory)

        bank1 = DFCObject('Inventory', None, None, 'avatar.base.Bank')
        unitcontainer.addNode(bank1)

        bank2 = DFCObject('Inventory', None, None, 'avatar.base.Bank2')
        unitcontainer.addNode(bank2)

        bank3 = DFCObject('Inventory', None, None, 'avatar.base.Bank3')
        unitcontainer.addNode(bank3)

        bank4 = DFCObject('Inventory', None, None, 'avatar.base.Bank4')
        unitcontainer.addNode(bank4)

        bank5 = DFCObject('Inventory', None, None, 'avatar.base.Bank5')
        unitcontainer.addNode(bank5)

        extraData = weapon.serialize()      # filler
        unitcontainer.addExtraData(extraData)
        avatar.addNode(unitcontainer)

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
        avatar.addNode(avatarmetrics)

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

        #test = DFCObject('StockUnit', None, None, 'skills.generic.DivineIntervention.DelayObject')
        #player.addNode(test)

        extraData = 'plzwork1'.encode('utf-8') + b'\x00'
        extraData += 'plzwork2'.encode('utf-8') + b'\x00'

        extraData += b'\x02\x03\x04\x05'[::-1]           # not used?
        extraData += b'\x02\x03\x04\x05'[::-1]           # not used?

        test2 = DFCObject('WorldEntity', None, None, 'WorldEntity')
        extraData += test2.serialize() #filler

        extraData += b'\x00'                             # changed queue levels
        extraData += b'\xAA'                             # not used?
        #data += b'\x00'
        extraData += 'Normal'.encode('utf-8') + b'\x00'  # difficulty (Normal, Formidable, Extreme and Insane)
        extraData += b'\x02'                             # not used? 
        extraData += b'\x00'                             # not used?
        extraData += b'\x02\x03\x04\x05'[::-1]    # not used?
        player.addExtraData(extraData)

        worldtest = DFCObject('EntityObject', None, None, 'EntityObject')
        worldtest.addNode(player)
        #data += worldtest.serialize()

        #vehicle = DFCObject('Vehicle', None, None, 'Vehicle')
        #avatar.addNode(vehicle)

        procmod = DFCObject('ProcModifier', None, None, 'ProcModifier')
        player.addNode(procmod)

        data += player.serialize()

        #self.sendPacket(pktType, data)
        self.sendZlibPacket1(pktType, data)
        
        
    def charCreate(self):
        pktType = b'\x0e'
        channelType = b'\x04'
        data = channelType + b'\x04'
        self.sendZlibPacket1(pktType, data)
        
        
    def confirmCharSelection(self, charID):
        pktType = b'\x0e'
        channelType = b'\x04'
        data = channelType + b'\x05'
        data += charID
        self.sendZlibPacket1(pktType, data)


    def testEntityCreate(self):
        pktType = b'\x0e'
        channelType = b'\x07'
        data = channelType + b'\x08'
        data += b'\x00\x50'[::-1]                       # entity ID?
        data += b'\xFF'                         # GCClassRegistry::readType
        data += 'Player'.encode('utf-8') + b'\x00'
        #data += b'\x06'
        #self.sendZlibPacket1(pktType, data)

        #data = channelType + b'\x02'
        #data += b'\x02'
        #data += b'\x00\x50'[::-1]
        data += 'plzwork'.encode('utf-8') + b'\x00'  # Player::readInit
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\xFF'
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\xFF'                         # GCClassRegistry::readType
        data += 'Player'.encode('utf-8') + b'\x00'
        data += 'Town'.encode('utf-8') + b'\x00'
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x06'
        self.sendZlibPacket1(pktType, data)


    def testAvatarEntityCreate(self):
        pktType = b'\x0e'
        channelType = b'\x07'
        data = channelType + b'\x08'
        data += b'\x00\x51'[::-1]
        data += b'\xFF'
        data += 'avatar.classes.FighterMale'.encode('utf-8') + b'\x00'

        # WorldEntity::readInit
        data += b'\x01\x02\x03\x04'[::-1]
        data += b'\x01\x02\x03\x04'[::-1]
        data += b'\x01\x02\x03\x04'[::-1]
        data += b'\x01\x02\x03\x04'[::-1]
        data += b'\x01\x02\x03\x04'[::-1]
        data += b'\x08'
        data += b'\x01\x02\x03\x04'[::-1]
        # Unit::readInit
        data += b'\x01'
        data += b'\x01'
        data += b'\x01\x02'[::-1]
        data += b'\x01\x02'[::-1]
        data += b'\x00\x50'[::-1]       # this should be player entity ID
        # Hero::readInit
        data += b'\x01\x02\x03\x04'[::-1]
        data += b'\x01\x02'[::-1]
        data += b'\x01\x02'[::-1]
        data += b'\x01\x02'[::-1]
        data += b'\x01\x02'[::-1]
        data += b'\x01\x02'[::-1]
        data += b'\x01\x02'[::-1]
        data += b'\x01\x02\x03\x04'[::-1]
        data += b'\x01\x02\x03\x04'[::-1]
        # Avatar::readInit
        data += b'\x01'
        data += b'\x01'
        data += b'\x01'
        
        data += b'\x06'
        self.sendZlibPacket1(pktType, data)


    def testComponentCreate(self):
        pktType = b'\x0e'
        channelType = b'\x07'
        data = channelType + b'\x32'
        data += b'\x00\x50'[::-1]       # entity ID
        data += b'\x00\x0a'[::-1]       # component ID
        data += b'\xFF'[::-1]
        data += 'Manipulators'.encode('utf-8') + b'\x00'
        data += b'\x01'*2
        data += b'\xFF'
        data += 'creatures.weapons.1HPick_scrapyard'.encode('utf-8') + b'\x00'
        data += b'\x01' #TODO
        
        data += b'\x33'
        data += b'\x00\x69'[::-1]
        data += b'\x06'
        self.sendZlibPacket1(pktType, data)


    def testEntityUpdate(self):
        pktType = b'\x0e'
        channelType = b'\x07'
        data = channelType + b'\x03'
        data += b'\x00\x51'[::-1]
        data += b'\x15'
        # xx::processUpdate
        #data += b'\x00\x51'[::-1]
        data += b'\x0a' # flags
        data += b'\x99\x99\x99\x99'[::-1]
        data += b'\x06'
        self.sendZlibPacket1(pktType, data)
  
        
    def testPacket(self):
        pktType = b'\x0e'
        channelType = b'\x07'
        data = channelType + b'\x0c'
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x06'
        self.sendZlibPacket1(pktType, data)
        
        
    def pathManagerBudget(self):
        pktType = b'\x0e'
        channelType = b'\x07'
        data = channelType + b'\x0d'
        data += b'\x66\x66\x66\x66'[::-1]           # unknown 4 bytes
        data += b'\x77\x77\x77\x77'[::-1]           # unknown 4 bytes
        data += b'\x88\x88\x88\x88'[::-1]           # unknown 4 bytes

        data += b'\x99\x99\x99\x99'[::-1]           # unknown 4 bytes
        data += b'\x00\x1e'[::-1]                   # perUpdate
        data += b'\x00\x07'[::-1]                   # perPath

        data += b'\x06'                             # end loop
        self.sendZlibPacket1(pktType, data)
        

    def connectClientEntityManager(self):
        pktType = b'\x0e'
        channelType = b'\x07'
        data = channelType + b'\x46'
        self.sendZlibPacket1(pktType, data)


    # valid zoneToLoad: Town, pvp_start
    # Spawnpoints(?): Start, Waypoint, Respawn
    def loadZone(self, zoneToLoad):
        pktType = b'\x0e'
        channelType = b'\x0d'
        data = channelType + b'\x00'
        data += zoneToLoad.encode('utf-8') + b'\x00'
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x01'                             # number of (something)

        data += b'\xFF'
        data += 'world.town.npc.Amazon1'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.Bank'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.base.TrainerFighterBase'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.base.TrainerMageBase'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.base.TrainerRangerBase'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.Boy1'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.Girl1'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.Gnome1'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.HelperNoobosaur01'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.OldMan1'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.PosseMagnate'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.SnowMan1'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.TokenFI'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.TokenJewelry'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.TokenMA'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.TokenRG'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.TownCommander'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.TownGuard1'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.TownGuard2'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.TownGuard3'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.TownLieutenant'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.TrainerFighter'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.TrainerMage'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.TrainerRanger'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.VendorPotion1'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.VendorWeapon1'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.VendorWeapon2'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.VendorWeapon3'.encode('utf-8') + b'\x00'
        data += 'world.town.npc.Well'.encode('utf-8') + b'\x00'


        data += b'\x00\x00\x00\x00'[::-1]           # BaseLoadingScreen
        self.sendZlibPacket1(pktType, data)
        

    def zoneClientInit(self):
        pktType = b'\x0e'
        channelType = b'\x0d'
        data = channelType + b'\x01' + b'\x66\x66\x66\x66'[::-1]
        #                               not used during zone load?
        self.sendZlibPacket1(pktType, data)

        data = channelType + b'\x05'
        data += b'\xFF\xFF\xFF\xFF'[::-1] + b'\x10\x20\x30\x40'[::-1]
        #                                   not used during zone load?
        self.sendZlibPacket1(pktType, data)
        
        
    def connectGroupClient(self):
        pktType = b'\x0e'
        channelType = b'\x09'
        data = channelType + b'\x30'
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x01'
        data += b'\x01'
        self.sendZlibPacket1(pktType, data)


    def addUserGroupClient(self):
        pktType = b'\x0e'
        channelType = b'\x09'
        data = channelType + b'\x42'
        data += b'\x00'*4

        data += b'\x02\x03\x04\x05'[::-1]
        data += 'plzwork'.encode('utf-8') + b'\x00'
        data += b'\x02\x03\x04\x05'[::-1]
        data += b'\x00'
        self.sendZlibPacket1(pktType, data)


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

