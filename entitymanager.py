import os
import struct

from constants import *


class EntityManager:
    def __init__(self):
        self.pktType = b'\x0e'
        self.channelType = struct.pack("B", CHANNEL_ENTITYMANAGER)
        self.seedValue = os.urandom(4)
        
    def process(self, gateway, packet):
        functionID = packet[1]


    def connect(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_ENTITYMANAGER_CONNECT)
        gateway.send_zlib1(self.pktType, data)
        
        
    def randomSeed(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_ENTITYMANAGER_RANDOMSEED)
        data += self.seedValue
        data += b'\x06'
        gateway.send_zlib1(self.pktType, data)
        
        
    def interval(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_ENTITYMANAGER_INTERVAL)
        data += b'\x02\x03\x04\x05'[::-1]           # unknown 4 bytes
        data += b'\x77\x77\x77\x77'[::-1]           # unknown 4 bytes
        data += b'\x88\x88\x88\x88'[::-1]           # unknown 4 bytes

        data += b'\x99\x99\x99\x99'[::-1]           # unknown 4 bytes
        data += b'\x00\x1e'[::-1]                   # perUpdate
        data += b'\x00\x07'[::-1]                   # perPath

        data += struct.pack("B", FUNC_ENTITYMANAGER_ENDPACKET)
        gateway.send_zlib1(self.pktType, data)
        
    
    def entityCreateInit(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_ENTITYMANAGER_ENTITYCREATEINIT)
        data += b'\x00\x50'[::-1]                       # entity ID?
        data += b'\xFF'                         # GCClassRegistry::readType
        data += 'Player'.encode('utf-8') + b'\x00'
        data += CHAR_NAME.encode('utf-8') + b'\x00'  # Player::readInit
        data += b'\x00\x00\x00\x00'[::-1]
        data += b'\x00\x00\x00\x00'[::-1]
        data += b'\xFF'
        data += struct.pack("<I", CHAR_ID)
        data += b'\x00\x00\x00\x00'[::-1]
        data += b'\x00\x00\x00\x00'[::-1]
        data += b'\xFF'                         # GCClassRegistry::readType
        data += 'ZoneDef'.encode('utf-8') + b'\x00'
        data += 'Town'.encode('utf-8') + b'\x00'
        data += b'\x00\x00\x00\x00'[::-1]
        
        data += struct.pack("B", FUNC_ENTITYMANAGER_ENTITYCREATEINIT)
        data += b'\x00\x51'[::-1]
        data += b'\xFF'
        data += 'avatar.classes.FighterMale'.encode('utf-8') + b'\x00'
        # WorldEntity::readInit
        data += struct.pack("<i", 150)   # size?
        data += struct.pack("!f", 444)      # position x (datatype = ??)
        data += struct.pack("!f", -170)      # position y (datatype = ??)
        data += struct.pack("!f", 50)       # position z (datatype = ??)
        data += struct.pack("<f", 0)       # heading
        data += b'\x00'
        #data += b'\x99\x99'[::-1]
        # Unit::readInit
        data += b'\x01'
        data += b'\x01'
        data += b'\x00\x66'[::-1]
        data += b'\x00\x48'[::-1]
        data += b'\x00\x50'[::-1]       # this should be player entity ID
        # Hero::readInit
        data += b'\x00\x00\x00\x03'[::-1]
        data += b'\x01\x02'[::-1]
        data += b'\x01\x02'[::-1]
        data += b'\x01\x02'[::-1]
        data += b'\x01\x02'[::-1]
        data += b'\x01\x02'[::-1]
        data += b'\x01\x02'[::-1]
        data += b'\x01\x02\x03\x04'[::-1]
        data += b'\x01\x02\x03\x04'[::-1]
        # Avatar::readInit
        data += b'\x01'                 # ???
        data += b'\x06'                 # hairstyle?
        data += b'\x00'                 # hair color
        
        data += struct.pack("B", FUNC_ENTITYMANAGER_ENDPACKET)
        gateway.send_zlib1(self.pktType, data)
        

    def entityUpdate(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_ENTITYMANAGER_ENTITYUPDATE)
        data += b'\x00\x51'[::-1]
        data += b'\x15'
        # xx::processUpdate
        #data += b'\x00\x51'[::-1]
        data += b'\x0a' # flags
        data += b'\x99\x99\x99\x99'[::-1]
        data += struct.pack("B", FUNC_ENTITYMANAGER_ENDPACKET)
        gateway.send_zlib1(self.pktType, data)
        
        
    def componentCreate(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_ENTITYMANAGER_COMPONENTCREATE)
        data += b'\x00\x51'[::-1]       # entity ID
        data += b'\x00\x0a'[::-1]       # component ID
        data += b'\xFF'
        data += 'UnitContainer'.encode('utf-8') + b'\x00'
        data += b'\x01'
        # container::readInit
        data += b'\x66'*4
        data += b'\x77'*4
        # gcobject::readchilddata<inventory>
        data += b'\x09'
        
        data += b'\xFF'
        data += 'avatar.base.Inventory'.encode('utf-8') + b'\x00'
        data += b'\x01' # inventory type enum? 0->generic,1->backpack,2->bank,3->trade
        data += b'\x01'
        data += b'\x00'
        
        data += b'\xFF'
        data += 'avatar.base.Bank'.encode('utf-8') + b'\x00'
        data += b'\x02' # inventory type enum? 0->generic,1->backpack,2->bank,3->trade
        data += b'\x01'
        data += b'\x00'
        
        data += b'\xFF'
        data += 'avatar.base.Bank2'.encode('utf-8') + b'\x00'
        data += b'\x02' # inventory type enum? 0->generic,1->backpack,2->bank,3->trade
        data += b'\x01'
        data += b'\x00'
        
        data += b'\xFF'
        data += 'avatar.base.Bank3'.encode('utf-8') + b'\x00'
        data += b'\x02' # inventory type enum? 0->generic,1->backpack,2->bank,3->trade
        data += b'\x01'
        data += b'\x00'
        
        data += b'\xFF'
        data += 'avatar.base.Bank4'.encode('utf-8') + b'\x00'
        data += b'\x02' # inventory type enum? 0->generic,1->backpack,2->bank,3->trade
        data += b'\x01'
        data += b'\x00'
        
        data += b'\xFF'
        data += 'avatar.base.Bank5'.encode('utf-8') + b'\x00'
        data += b'\x02' # inventory type enum? 0->generic,1->backpack,2->bank,3->trade
        data += b'\x01'
        data += b'\x00'
        
        data += b'\xFF'
        data += 'avatar.base.Bank6'.encode('utf-8') + b'\x00'
        data += b'\x02' # inventory type enum? 0->generic,1->backpack,2->bank,3->trade
        data += b'\x01'
        data += b'\x00'
        
        data += b'\xFF'
        data += 'avatar.base.Bank7'.encode('utf-8') + b'\x00'
        data += b'\x02' # inventory type enum? 0->generic,1->backpack,2->bank,3->trade
        data += b'\x01'
        data += b'\x00'
        
        data += b'\xFF'
        data += 'avatar.base.TradeInventory'.encode('utf-8') + b'\x00'
        data += b'\x03' # inventory type enum? 0->generic,1->backpack,2->bank,3->trade
        data += b'\x01'
        data += b'\x00'
        # unitcontainer::readinit
        data += b'\x00'
        
        data += struct.pack("B", FUNC_ENTITYMANAGER_COMPONENTCREATE)
        data += b'\x00\x51'[::-1]       # entity ID
        data += b'\x00\x0b'[::-1]       # component ID
        data += b'\xFF'
        data += 'Manipulators'.encode('utf-8') + b'\x00'
        data += b'\x01'
        # xx::readInit
        data += b'\x00'
        
        data += struct.pack("B", FUNC_ENTITYMANAGER_COMPONENTCREATE)
        data += b'\x00\x50'[::-1]
        data += b'\x00\x0c'[::-1]
        data += b'\xFF'
        data += 'DialogManager'.encode('utf-8') + b'\x00'
        data += b'\x01'
        
        data += struct.pack("B", FUNC_ENTITYMANAGER_COMPONENTCREATE)
        data += b'\x00\x50'[::-1]
        data += b'\x00\x0d'[::-1]
        data += b'\xFF'
        data += 'QuestManager'.encode('utf-8') + b'\x00'
        data += b'\x01'
        # questmanager::readinit
        data += b'\x66'*4
        data += b'\x00'
        data += 'questtest'.encode('utf-8') + b'\x00'
        data += 'questtest2'.encode('utf-8') + b'\x00'
        data += b'\x77'*4
        data += b'\x00'
        data += 'questtest3'.encode('utf-8') + b'\x00'
        data += 'questtest4'.encode('utf-8') + b'\x00'
        data += b'\x88'*4
        data += 'questtest5'.encode('utf-8') + b'\x00'
        data += 'questtest6'.encode('utf-8') + b'\x00'
        data += 'questtest7'.encode('utf-8') + b'\x00'
        # questmanager::readavailablequests
        data += b'\x00'
        
        data += b'\x00\x00'[::-1]
        data += b'\x00\x00'[::-1]
        
        data += struct.pack("B", FUNC_ENTITYMANAGER_COMPONENTCREATE)
        data += b'\x00\x51'[::-1]
        data += b'\x00\x0e'[::-1]
        data += b'\xFF'
        data += 'avatar.base.Equipment'.encode('utf-8') + b'\x00'
        data += b'\x01'
        # gcobject::readchilddata
        data += b'\x00'
        
        data += struct.pack("B", FUNC_ENTITYMANAGER_COMPONENTCREATE)
        data += b'\x00\x51'[::-1]
        data += b'\x00\x0f'[::-1]
        data += b'\xFF'
        data += 'avatar.base.Skills'.encode('utf-8') + b'\x00'
        data += b'\x01'
        # readinit
        data += b'\x01\x02\x03\x04'
        # readchilddata<skill>
        data += b'\x00'
        # readchilddata<skillprofession>
        data += b'\x00'
        
        data += struct.pack("B", FUNC_ENTITYMANAGER_COMPONENTCREATE)
        data += b'\x00\x51'[::-1]
        data += b'\x00\x10'[::-1]
        data += b'\xFF'
        data += 'Modifiers'.encode('utf-8') + b'\x00'
        data += b'\x01'
        # readinit
        data += b'\x00'*4
        data += b'\x00'*4
        # readchilddatacomplete<modifier>
        data += b'\x00'
        
        data += struct.pack("B", FUNC_ENTITYMANAGER_COMPONENTCREATE)
        data += b'\x00\x51'[::-1]
        data += b'\x00\x11'[::-1]
        data += b'\xFF'
        data += 'avatar.base.UnitBehavior'.encode('utf-8') + b'\x00'
        data += b'\x01'
        # behavior::readinit
        data += b'\x01'
        data += b'\x00'
        data += b'\x00'
        data += b'\x01'
        # unitmover::readinit
        data += b'\x01'
        data += b'\x00'*4
        data += b'\x00'*4
        data += b'\x00'*4
        data += b'\x00'*4
        data += b'\x03'
        # unitbehavior::readinit
        data += b'\x00'
        data += b'\x00'
        data += b'\x01' 
        
        data += struct.pack("B", FUNC_ENTITYMANAGER_ENDPACKET)
        gateway.send_zlib1(self.pktType, data)
