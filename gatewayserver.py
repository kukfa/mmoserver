#!/usr/bin/env python3

import asyncio
import struct
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
            if (pktType == 1):
                self.initPacket()
            #if (pktType == 4):
                #self.testPacket()
            else:
                pass
        else:
            self.testPacket()


    def sendPacket(self, pktType, data):
        packet = pktType                        # byte
        packet += b'\x99\x88\x77'               # unknown
        packet += struct.pack("<I", len(data))  # message length
        packet += data
        print("[S] Data: " + packet.hex())
        self.transport.write(packet)
        
        
    def closeSocket(self, reason):
        print(reason)
        self.transport.close()


    def initPacket(self):
        pktType = b'\x08'
        zlibMessage = b'\x03\xBA\xAD\xF0\x0D'
        data = struct.pack("<I", len(zlibMessage))  # uncompressed size
        data += zlib.compress(zlibMessage)          # compressed message
        self.sendPacket(pktType, data)

        pktType = b'\x02'
        data = b'\x00\x03\x00'
        self.sendPacket(pktType, data)


    def testPacket(self):
        pktType = b'\x0c'
        zlibMessage = b'\x00\x00\x00'
        data = struct.pack("<I", len(zlibMessage))
        data += zlib.compress(zlibMessage)
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

