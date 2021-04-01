import hashlib
import ecdsa

# define Bitcoin's elliptic curve parameters
_a = 0x0000000000000000000000000000000000000000000000000000000000000000
_b = 0x0000000000000000000000000000000000000000000000000000000000000007
_p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

print("a =", _a)
print("b =", _b)
print("p =", _p)
print("n =", _n)

# define elliptic curve and order
curve_secp256k1 = ecdsa.ellipticcurve.CurveFp(_p, _a, _b)
ec_order = _n

# define generator point G
_Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
_Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
generator_secp256k1 = ecdsa.ellipticcurve.Point(curve_secp256k1, _Gx, _Gy, _n)
G = generator_secp256k1
print(f"G = {G}")

# get public key from previous scriptPubKey
prev_scriptPubKey = "41" \
                    "04" \
                    "11db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5c" \
                    "b2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3" \
                    "ac"
pub_key = prev_scriptPubKey[4:len(prev_scriptPubKey) - 2]  # remove prefixes 4104 and ac suffix
K_pub_x = int("0x" + str(pub_key[:len(pub_key) // 2]), 16)  # first part is the x coordinate
K_pub_y = int("0x" + str(pub_key[len(pub_key) // 2:]), 16)  # second part is the y coordinate
K_pub = ecdsa.ellipticcurve.Point(curve_secp256k1, K_pub_x, K_pub_y,
                                  ec_order)  # define public key as a point on the elliptic curve
print(f"K_pub = {K_pub}")

# get signature (r,s) from scriptSig
scriptSig = "48" \
            "47" \
            "30" \
            "44" \
            "02" \
            "20" \
            "4e45e16932b8af514961a1d3a1a25fdf3f4f7732e9d624c6c61548ab5fb8cd41" \
            "02" \
            "20" \
            "181522ec8eca07de4860a4acdd12909d831cc56cbbac4622082221a8768d1d09" \
            "01"
signature = scriptSig[8:len(scriptSig) - 2]
r = int("0x" + str(signature[4:len(signature) // 2]), 16)
s = int("0x" + str(signature[len(signature) // 2 + 4:]), 16)
print(f"(r,s) = ({r},{s})")

# get message t from raw transaction data
raw_trx_data = "01000000" \
               "01c997a5e56e104102fa209c6a852dd90660a20b2d9c352423edce25857fcd3704" \
               "00000000" \
               "48" \
               "47" \
               "30" \
               "44" \
               "02" \
               "20" \
               "4e45e16932b8af514961a1d3a1a25fdf3f4f7732e9d624c6c61548ab5fb8cd41" \
               "02" \
               "20" \
               "181522ec8eca07de4860a4acdd12909d831cc56cbbac4622082221a8768d1d09" \
               "01" \
               "ffffffff" \
               "02" \
               "00ca9a3b00000000" \
               "43" \
               "41" \
               "04" \
               "ae1a62fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302fa28414" \
               "e7aab37397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e6cd84c" \
               "ac" \
               "00286bee00000000" \
               "43" \
               "41" \
               "04" \
               "11db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5c" \
               "b2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3" \
               "ac" \
               "00000000"
print(f"Raw transaction data = {raw_trx_data}")
trx_copy = raw_trx_data  # the copied transaction will be modified
start_scriptSig = trx_copy.find(scriptSig)  # find the start of the scriptSig
len_scriptSig = 2*int(str(trx_copy[start_scriptSig:start_scriptSig+2]), 16)  # get the length of the scriptSig (2* for number of characters instead of bytes)
len_prevScriptSig = f'{len(prev_scriptPubKey) // 2:02x}'  # get length of previousScriptSig as hex

# replace scriptSig with previous scriptPubKey
trx_copy = trx_copy[:start_scriptSig] + \
           len_prevScriptSig + prev_scriptPubKey + \
           trx_copy[start_scriptSig+len_scriptSig+2:]

# add SIGHASH_ALL as little-endian integer ("01000000")
mod_trx = trx_copy + scriptSig[len(scriptSig) - 2: len(scriptSig)] + "000000"
print(mod_trx)

# hash modified transaction message to find t
T = bytes.fromhex(mod_trx)
h256 = hashlib.sha256(hashlib.sha256(T).digest()).digest()
t = int.from_bytes(h256, "big")
print(f"t = {hex(t)}")

# find the modular multiplicative inverse of s to find u1 and u2
s_inv = pow(s, -1, ec_order)
u1 = (s_inv * t) % ec_order
u2 = (s_inv * r) % ec_order
print(f"u1 = {u1}")
print(f"u2 = {u2}")

# find the point P
P = u1 * G + u2 * K_pub
print(f"P = {P}")

# check authenticity: is xp mod n == r
if P.x() % ec_order == r:
    print(f"The message t = {hex(t)} was signed by Satoshi's private key.")
else:
    print(f"The message t = {hex(t)} was NOT signed by Satoshi's private key.")
