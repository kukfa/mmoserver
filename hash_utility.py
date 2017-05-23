def hash_djb2(s):
    hash = 5381
    for x in s:
        hash = ((hash << 5) + hash) + ord(x.lower())
    return hex(hash & 0xFFFFFFFF)
    
print(hash_djb2('Example'))
