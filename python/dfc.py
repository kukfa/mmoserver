import struct

class DFCObject:
    def __init__(self, nativeClass, nodeID, nodeName, GCClass):
        self.nativeClass = nativeClass
        self.nodeID = nodeID
        self.nodeName = nodeName
        self.nodes = []
        self.GCClass = GCClass
        self.properties = {}
        self.extraData = b''

    def hash_djb2(self, s):
        hash = 5381
        for x in s:
            hash = ((hash << 5) + hash) + ord(x.lower())
        return struct.pack("<I", hash & 0xFFFFFFFF)

    def addNode(self, DFCObject):
        self.nodes.append(DFCObject)

    def addProperty(self, propertyName, propertyValue):
        self.properties[propertyName] = propertyValue

    def addExtraData(self, extraData):
        self.extraData += extraData

    def serialize(self):
        data = b'\x2D'                                  # version number
        data += self.hash_djb2(self.nativeClass)        # native class
        if self.nodeID:                                 # node ID
            data += struct.pack("<I", self.nodeID)
        else:
            data += b'\x00'*4
        if self.nodeName:                               # node name
            data += self.nodeName.encode('utf-8') + b'\x00'
        else:
            data += b'\x00'
        data += struct.pack("<I", len(self.nodes))      # number of nodes
        for obj in self.nodes:                          # serialize child nodes
            data += obj.serialize()
        data += self.hash_djb2(self.GCClass)            # GC class
        for name, value in self.properties.items():     # properties
            data += self.hash_djb2(name)
            if isinstance(value, int):                  # numeric property
                data += struct.pack("<I", value)
            else:                                       # string property
                data += value.encode('utf-8') + b'\x00'
        data += b'\x00'*4                               # end object
        data += self.extraData                          # additional data
        return data
