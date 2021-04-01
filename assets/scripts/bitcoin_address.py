import hashlib
import base58

# Uncompressed public key
pubKey = bytes.fromhex("04"
                       "2e930f39ba62c6534ee98ed20ca98959d34aa9e057cda01cfd422c6bab3667b7"
                       "6426529382c23f42b9b08d7832d4fee1d6b437a8526e59667ce9c4e9dcebcabb")
print(f"Public key: {pubKey.hex()}")

# Hash: SHA256
d = hashlib.sha256(pubKey)
print(f"SHA256 of public key: {d.hexdigest()}")

# Hash: RIPEMD-160
h = hashlib.new('ripemd160')
h.update(d.digest())
print(f"Hash160: {h.hexdigest()}")

# Prefix 00
H = bytearray("\x00", "ascii") + h.digest()
print(f"Hash160 with prefix: {H.hex()}")

# Last 4 bytes of the double hashed Hash160 (incl. prefix) are the checksum
checksum = hashlib.sha256(hashlib.sha256(H).digest()).digest()[:4]
print(f"The last 4 bytes of the double hashed Hash160 (incl. prefix) are the checksum: {checksum.hex()}")

# Add checksum to Hash160 and encode in base58
H += checksum
address = base58.b58encode(bytes(H))
print(f"Bitcoin address: {address.decode('utf-8')}")
