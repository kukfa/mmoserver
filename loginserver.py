#!/usr/bin/env python3

import os
import socket
import sys
import blowfish
import ipaddress
import struct
import binascii

# gameServer info, hardcoded for now
numServers = 1
ageLimit = 10

serverID = 1
gameIP = "10.0.0.1"
gamePort = 7777
maxPlayers = 20
numPlayers = 0
pvp = 0
testServer = 1

loginPort = 2106
key = b"[;'.]94-31==-%&@!^+]\000"
bf = blowfish.Cipher(key, byte_order = "little")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', loginPort))
s.listen(1)
print("loginServer listening: port " + str(loginPort))

def checksum(data):
	# TODO rewrite
	chksum = 0
	for i in range(0, len(data)-4, 4):
		temp = data[i] & 0xff
		temp |= data[i+1] << 8 & 0xff00
		temp |= data[i+2] << 16 & 0xff0000
		temp |= data[i+3] << 24 & 0xff000000
		chksum ^= temp
	return chksum

def sendPacket(conn, data):
	chksum = struct.pack("<L", checksum(data)) + b'\x00\x00\x00\x00'
	# append checksum
	if (len(data) % 8 == 0):
		data += chksum
	else:
		data = data[0:len(data)-(len(data)%8)] + chksum	# instead of appending the checksum and padding with 0's to reach a multiple of 8 (for encryption), the checksum overwrites some of least significant bytes in order to reach a multiple of 8
	ct = b''.join(bf.encrypt_ecb(data))	# encrypt the data
	size = len(ct) + 2
	packet = struct.pack("<H", size)	# added to front of packet, little-endian order
	packet += ct	# append encrypted data
	conn.send(packet)

def initPacket(conn):
	data = b'\x00'	# packet ID
	data += b'\x9c\x77\xed\x03'	# session ID?
	data += b'\x5a\x78\x00\x00'	# protocol version -> 785a
	size = len(data) + 2
	packet = bytes([size & 0xff]) + bytes([size >> 8 & 0xff]) + data
	conn.send(packet)

def loginOk(conn, sessionKey):
	data = b'\x03'		# packet ID
	data += bytes(sessionKey)	# 8-byte session key
	data += b'\x00\x00\x00\x00'	# purpose unknown from here onwards
	data += b'\x00\x00\x00\x00'
	data += b'\xea\x03\x00\x00'
	data += b'\x00\x00\x00\x00'
	data += b'\x00\x00\x00\x00'
	data += b'\x02\x00\x00\x00'
	sendPacket(conn, data)

def loginFail(conn, reason):
	# TODO test
	data = b'\x01'	# packet ID
	data += b'\x00\x00\x00'	# filler?
	# reasons:
	# 0x01 -> system error
	# 0x02 -> invalid password
	# 0x03 -> invalid username or password
	# 0x04 -> access denied
	# 0x05 -> info on account is incorrect (?) might mean internal error in database?
	# 0x07 -> account already in use
	# 0x09 -> banned account
	# 0x10 -> ?
	# 0x12 -> account expired?
	# 0x13 -> account out of game time
	data += reason
	sendPacket(conn, data)

def serverList(conn):
	data = b'\x04'	# packet ID
	data += bytes([numServers])	# total # game servers available
	data += b'\x00'	# fixed
	# the following is repeated for each server
	data += bytes([serverID])	# ID of each server (starting at 1)
	data += ipaddress.IPv4Address(gameIP).packed	# gameserver IP, packed in big-endian order
	data += struct.pack("<I", gamePort)	# gameserver port, little-endian order
	data += bytes([ageLimit])	# unsure what this is used for
	data += bytes([pvp])	# 1 if pvp server, otherwise 0
	data += struct.pack("<H", numPlayers)	# current # of players
	data += struct.pack("<H", maxPlayers)	# max # of players
	data += bytes([testServer])	# 1 if test server, otherwise 0
	if (testServer == 1):
		data += b'\x04\x00\x00\x00\x00'
	else:
		data += b'\x00\x00\x00\x00\x00'	# TODO doesn't list server if it isn't a test server
	sendPacket(conn, data)

def playOk(conn, sessionKey):
	data = b'\x07'	# packet ID
	data += sessionKey	# 8-byte session key
	data += b'\x01\x00\x00\x00\x00\x00\x00'
	sendPacket(conn, data)

def playFail(conn, reason):
	# TODO test
	data = b'\x06'	# packet ID
	data += b'\x00\x00\x00'	# probably filler?
	# reasons:
	# 0x01 -> account in use
	# 0x02 -> ?
	# 0x03 -> invalid password
	# 0x04 -> general failure?
	# 0x0f -> too many players
	data += reason
	sendPacket(conn, data)

def requestAuthLogin(pt):
	username = pt[2:15].decode('cp1252')
	password = pt[16:30].decode('cp1252')
	# TODO: fix decoding
	print("RequestAuthLogin: " + username + ":" + password)
	# TODO: additional checks: validate login, check if account is in game server or login server already
	if (True):
		sessionKey = os.urandom(8)
		# associate key with account
		# store that this account is currently logged in to login server
		return sessionKey
	return "01"

def requestServerLogin(pt):
	sessionKey = pt[1:9]
	serverID = pt[9]
	# check if too many players
	if (True):
		return sessionKey
	return "01"

while True:
	conn, client = s.accept()
	print("connection from: " + str(client))
	initPacket(conn)	# send initial packet
	while True:		# process subsequent packets	
		lenLo = int.from_bytes(conn.recv(1), byteorder='big')
		lenHi = int.from_bytes(conn.recv(1), byteorder='big')
		length = lenHi * 256 + lenLo
		if (lenHi < 0):
			break
		data = conn.recv(length-2)
		if (len(data)+2 != length):
			print("incomplete packet received")
			conn.close()
			break
		pt = b''.join(bf.decrypt_ecb(data))

		pktType = pt[0] & 0xff
		if (pktType == 0):
			result = requestAuthLogin(pt)
			if (type(result) is bytes):
				loginOk(conn, result)
			else:
				loginFail(conn, binascii.unhexlify(result))
		elif (pktType == 2):
			result = requestServerLogin(pt)
			if (type(result) is bytes):
				playOk(conn, result)
			else:
				playFail(conn, binascii.unhexlify(result))
		elif (pktType == 5):
			# requestServerList
			serverList(conn)
		else:
			print("unknown packet: " + str(pktType))
			conn.close()
			break
