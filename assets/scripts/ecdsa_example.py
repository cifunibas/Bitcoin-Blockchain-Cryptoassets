import ecdsa

# define ECDSA example parameters
_a = 0
_b = 7
_p = 37
_n = 13

print(f"a = {_a}")
print(f"b = {_b}")
print(f"p = {_p}")
print(f"n = {_n}")

# define elliptic curve and order
curve_secp256k1 = ecdsa.ellipticcurve.CurveFp(_p, _a, _b)
ec_order = _n

# define generator point
_Gx = 8
_Gy = 1
generator_secp256k1 = ecdsa.ellipticcurve.Point(curve_secp256k1, _Gx, _Gy, _n)
G = generator_secp256k1
print(f"G = {G}")

# choose private key
k_prv = 9
print(f"k_prv = {k_prv}")

# find the corresponding public key
K_pub = k_prv * G
print(f"K_pub = {K_pub}")

# signature

# define transaction message
t = 4
print(f"t = {t}")

# choose random number
i = 7
P = i * G
print(f"P = {P}")

# find r
r = P.x() % ec_order
print(f"r = {r}")

# find modular multiplicative inverse of i to find s
i_inv = pow(i, -1, ec_order)
s = (i_inv * (t + r * k_prv)) % ec_order
print(f"s = {s}")

# verification

# find modular multiplicative inverse of s to find u1 and u2
s_inv = pow(s, -1, ec_order)
u1 = (s_inv * t) % ec_order
u2 = (s_inv * r) % ec_order
print(f"u1 = {u1}")
print(f"u2 = {u2}")

# find P
P_alt = u1 * G + u2 * K_pub
print(f"P = {P_alt}")

# check if xp mod n == r
if P_alt.x() % ec_order == r:
    print(f"The message t = {t} was signed by Tamara's private key.")
else:
    print(f"The message t = {t} was NOT signed by Tamara's private key.")
