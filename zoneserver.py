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
        data += b'\x00\x00\x00\x01'[::-1]
        data += b'\x1D'                             # number of (something)

        data += b'\xFF'
        data += 'world.town.npc.Amazon1'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.Bank'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.base.TrainerFighterBase'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.base.TrainerMageBase'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.base.TrainerRangerBase'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.Boy1'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.Girl1'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.Gnome1'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.HelperNoobosaur01'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.OldMan1'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.PosseMagnate'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.SnowMan1'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.TokenFI'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.TokenJewelry'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.TokenMA'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.TokenRG'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.TownCommander'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.TownGuard1'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.TownGuard2'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.TownGuard3'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.TownLieutenant'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.TrainerFighter'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.TrainerMage'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.TrainerRanger'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.VendorPotion1'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.VendorWeapon1'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.VendorWeapon2'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.VendorWeapon3'.encode('utf-8') + b'\x00'
        data += b'\xFF'
        data += 'world.town.npc.Well'.encode('utf-8') + b'\x00'

        data += b'\x00\x00\x00\x01'[::-1]           # BaseLoadingScreen
        gateway.send_zlib1(self.pktType, data)
        

    def ready(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_ZONESERVER_READY)
        data += struct.pack("<I", CHAR_ID)
        gateway.send_zlib1(self.pktType, data)
        
        
    def instanceCount(self, gateway):
        data = self.channelType + struct.pack("B", FUNC_ZONESERVER_INSTANCECOUNT)
        data += b'\x00\x00\x00\x01'[::-1] + b'\x00\x00\x00\x01'[::-1]
        gateway.send_zlib1(self.pktType, data)
        
