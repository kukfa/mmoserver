#!/usr/bin/env python3

import asyncio
import binascii
import blowfish
import ipaddress
import os
import struct
import sys

# gameServer info, hardcoded for now
numServers = 1
ageLimit = 10

serverID = 1
gameIP = "10.0.0.1"
gamePort = 7777
maxPlayers = 20
numPlayers = 0
pvp = 0
online = 1

loginPort = 2106
key = b"[;'.]94-31==-%&@!^+]\000"
bf = blowfish.Cipher(key, byte_order="little")

class LoginServer(asyncio.Protocol):
    def connection_made(self, transport):
        print("Connection from: " + transport.get_extra_info('peername')[0])
        self.transport = transport
        self.initPacket()


    def data_received(self, data):
        lenLo = int(data[0])
        lenHi = int(data[1])
        length = lenHi * 256 + lenLo

        if (lenHi < 0):
            closeSocket("Invalid packet length")

        if (len(data) != length):
            closeSocket("Incomplete packet received")

        pt = b''.join(bf.decrypt_ecb(data[2:]))
        print(pt.hex())
        # TODO verify checksum?
        pktType = pt[0] & 0xff

        if (pktType == 0):
            result = self.requestAuthLogin(pt)
            if (type(result) is bytes):
                self.loginOk(result)
            else:
                self.loginFail(binascii.unhexlify(result))
        elif (pktType == 2):
            result = self.requestServerLogin(pt)
            if (type(result) is bytes):
                self.playOk(result)
            else:
                self.playFail(binascii.unhexlify(result))
        elif (pktType == 5):
            # requestServerList
            self.serverList()
        else:
            self.closeSocket("Unknown packet: " + str(pktType))


    def sendPacket(self, data):
        chksum = struct.pack("<L", self.checksum(data)) + b'\x00\x00\x00\x00'
        # append checksum
        if (len(data) % 8 == 0):
            data += chksum
        else:
            '''
            instead of appending the checksum and padding with 0's to reach
            a multiple of 8 (for encryption), the checksum overwrites some
            of least significant bytes in order to reach a multiple of 8
            '''
            data = data[0:len(data)-(len(data)%8)] + chksum
        ct = b''.join(bf.encrypt_ecb(data))	    # encrypt the data
        size = len(ct) + 2
        # added to front of packet, little-endian order
        packet = struct.pack("<H", size)
        packet += ct	                        # append encrypted data
        self.transport.write(packet)
        
        
    def closeSocket(self, reason):
        print(reason)
        self.transport.close()
        
        
    def checksum(self, data):
        # TODO rewrite
        chksum = 0
        for i in range(0, len(data)-4, 4):
            temp = data[i] & 0xff
            temp |= data[i+1] << 8 & 0xff00
            temp |= data[i+2] << 16 & 0xff0000
            temp |= data[i+3] << 24 & 0xff000000
            chksum ^= temp
        return chksum


    def initPacket(self):
        data = b'\x00'                          # packet ID
        data += b'\x9c\x77\xed\x03'             # session ID?
        data += b'\x5a\x78\x00\x00'             # protocol version -> 785a
        size = len(data) + 2
        packet = bytes([size & 0xff]) + bytes([size >> 8 & 0xff]) + data
        self.transport.write(packet)


    def loginFail(self, reason):
        '''
        reasons:
        0x01 -> system error *
        0x02 -> invalid username (message says "invalid username or password")
        0x03 -> invalid username or password
        0x04 -> access denied *
        0x05 -> info on account is incorrect *
        0x07 -> account already logged in
        0x09 -> banned account *
        0x10 -> ? *
        0x12 -> account expired *
        0x13 -> account out of game time *
        (* = cancels login with "error connecting to server" message)
        '''
        data = b'\x01'                  # packet ID
        data += reason
        data += b'\x00\x00\x00\x00\x00\x00'
        self.sendPacket(data)


    def accountKicked(self, reason):
        '''
        reasons:
        0x01 -> access denied (prints message about beta access timeframes)
        0x08 -> blocked
        0x10 -> blocked
        0x20 -> blocked
        '''
        data = b'\x02'                  # packet ID
        data += reason
        data += b'\x00\x00\x00\x00\x00\x00'
        self.sendPacket(data)


    def loginOk(self, sessionKey):
        data = b'\x03'                  # packet ID
        data += bytes(sessionKey)       # 8-byte session key
        data += b'\x00\x00\x00\x00'     # purpose unknown from here onwards
        data += b'\x00\x00\x00\x00'
        data += b'\xea\x03\x00\x00'
        data += b'\x00\x00\x00\x00'
        data += b'\x00\x00\x00\x00'
        data += b'\x02\x00\x00\x00'
        self.sendPacket(data)


    def serverList(self):
        data = b'\x04'                  # packet ID
        data += bytes([numServers])     # total num game servers available
        data += b'\x01'                 # last game server used

        # the following is repeated for each server
        data += bytes([serverID])       # ID of each server (starting at 1)
        # gameserver IP, packed in big-endian order
        data += ipaddress.IPv4Address(gameIP).packed
        # gameserver port, little-endian order
        data += struct.pack("<I", gamePort)
        data += bytes([ageLimit])       # unsure what this is used for
        data += bytes([pvp])            # 1 if pvp server, otherwise 0
        data += struct.pack("<H", numPlayers)   # current # of players
        data += struct.pack("<H", maxPlayers)   # max # of players
        data += bytes([online])     # 1 if server should be listed, otherwise 0
        if (online == 1):
            data += b'\x04\x00\x00\x00\x00'
        else:
            # TODO doesn't list server if it isn't a test server
            data += b'\x00\x00\x00\x00\x00'
        self.sendPacket(data)


    def playFail(self, reason):
        '''
        reasons:
        0x01 -> account in use *
        0x02 -> *
        0x03 -> invalid password *
        0x04 -> general failure? *
        0x0f -> too many players *
        (* = cancels with "error connecting to server" message)
        '''
        # TODO test
        data = b'\x06'              # packet ID
        data += reason
        data += b'\x00\x00\x00\x00\x00\x00'
        self.sendPacket(data)


    def playOk(self, sessionKey):
        data = b'\x07'              # packet ID
        data += sessionKey          # 8-byte session key
        data += b'\x01\x00\x00\x00\x00\x00\x00'
        self.sendPacket(data)


    def requestAuthLogin(self, pt):
        username = pt[1:15]
        password = pt[15:31]
        # TODO: fix decoding
        # if login invalid
            # return "03"
        # if account in (game or?) login server already
            # return "07"
        # if everything's valid
        sessionKey = os.urandom(8)
        # TODO associate key with account
        # TODO store that this account is currently logged in to login server
        return sessionKey


    def requestServerLogin(self, pt):
        '''
        comments describe the error codes defined for the protocol
        however, error code may be arbitrary b/c the client processes them all
        the same way?
        '''
        sessionKey = pt[1:9]
        serverID = pt[9]
        # if (numPlayers >= maxPlayers):
            # return "0f"    # 'too many players'
        # if account is logged in to a gameserver already
            # return "01"    # 'account in use'
        # if sessionKey not valid
            # return "03"    # 'invalid password'
        return sessionKey


def main():
    loop = asyncio.get_event_loop()
    coroutine = loop.create_server(LoginServer, host=None, port=loginPort)
    server = loop.run_until_complete(coroutine)
    
    print("Listening on: " + server.sockets[0].getsockname()[0])
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == "__main__":
    main()

