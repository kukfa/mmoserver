# auth server config
AUTH_PORT = 2110
AUTH_NUMGATEWAYS = 1
AUTH_BLOWFISHKEY = b"[;'.]94-31==-%&@!^+]\000"
AUTH_DESKEY = b'\x54\x45\x53\x54\x00\x00\x00\x00'

# gateway server config
GATEWAY_ID = 1
GATEWAY_IP = "10.0.2.4"
GATEWAY_PORT = 7777
GATEWAY_AGELIMIT = 10
GATEWAY_MAXPLAYERS = 24
GATEWAY_NUMPLAYERS = 0
GATEWAY_PVP = 0
GATEWAY_ONLINE = 1

# channel IDs
CHANNEL_INIT = 1
CHANNEL_USERMANAGER = 3
CHANNEL_CHARACTERMANAGER = 4
CHANNEL_CHATSERVER = 6
CHANNEL_ENTITYMANAGER = 7
CHANNEL_GROUPSERVER = 9
CHANNEL_TRADESERVER = 10
CHANNEL_ZONESERVER = 13
CHANNEL_POSSESERVER = 15

# function IDs
FUNC_USERMANAGER_CONNECT = 0
FUNC_USERMANAGER_ROSTER = 1

FUNC_CHARACTERMANAGER_CONNECT = 0
FUNC_CHARACTERMANAGER_CREATED = 2
FUNC_CHARACTERMANAGER_SEND = 3
FUNC_CHARACTERMANAGER_CREATE = 4
FUNC_CHARACTERMANAGER_SELECT = 5

FUNC_GROUPSERVER_CLIENTCONNECT = 00
FUNC_GROUPSERVER_CONNECT = 48

FUNC_ZONESERVER_CONNECT = 0
FUNC_ZONESERVER_READY = 1
FUNC_ZONESERVER_INSTANCECOUNT = 5
FUNC_ZONESERVER_LOADED = 6

FUNC_ENTITYMANAGER_ENDPACKET = 6
FUNC_ENTITYMANAGER_ENTITYCREATEINIT = 8
FUNC_ENTITYMANAGER_RANDOMSEED = 12
FUNC_ENTITYMANAGER_INTERVAL = 13
FUNC_ENTITYMANAGER_COMPONENTCREATE = 50
FUNC_ENTITYMANAGER_CONNECT = 70

# misc game server constants
ZONE_TOWNSTON = 'Town'
CHAR_ID = 33752069

