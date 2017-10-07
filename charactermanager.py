import struct

from constants import *
from dfc import DFCObject


class CharacterManager:
    def __init__(self):
        self.pktType = b'\x0e'
        self.channelType = struct.pack("B", CHANNEL_CHARACTERMANAGER)


    def process(self, gateway, packet):
        functionID = packet[1]
        if (functionID == FUNC_CHARACTERMANAGER_CONNECT):
            self.connect(gateway)
        if (functionID == FUNC_CHARACTERMANAGER_CREATED):
            pass
        if (functionID == FUNC_CHARACTERMANAGER_SEND):
            self.sendCharacters(gateway)
        if (functionID == FUNC_CHARACTERMANAGER_SELECT):
            self.selectCharacter(gateway, packet[2:])


    def connect(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_CHARACTERMANAGER_CONNECT)
        gateway.send_zlib1(self.pktType, data)


    def sendCharacters(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_CHARACTERMANAGER_SEND)
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
        
        dialogmanager = DFCObject('DialogManager', None, None, 'DialogManager')
        avatar.addNode(dialogmanager)

        data += player.serialize()
        gateway.send_zlib1(self.pktType, data)
        
        
    def openCharCreationScreen(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_CHARACTERMANAGER_CREATE)
        gateway.send_zlib1(self.pktType, data)
        
        
    def selectCharacter(self, gateway, charID):
        data = self.channelType + struct.pack("B", FUNC_CHARACTERMANAGER_SELECT)
        data += charID
        gateway.send_zlib1(self.pktType, data)
