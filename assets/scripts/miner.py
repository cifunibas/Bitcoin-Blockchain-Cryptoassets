from hashlib import sha256
from time import time


def my_miner(preimage: str, leading_zeros: int = 1) -> str:
    """
    Compute and return an sha256 hash from `preimage` with minimum amount of
    leading zeros by incrementing and appending a nonce value.
    """
    # The hash is 32 bytes or 64 characters long
    assert 0 <= leading_zeros <= 64

    # set nonce to default value
    nonce = 0

    # start timer
    start_time = time()

    # first iteration
    encoded_input = f"{preimage}{nonce}".encode("utf-8")
    hashed_image = sha256(encoded_input).hexdigest()

    # loop and increment the nonce until a solution hash is found
    while not hashed_image.startswith("0" * leading_zeros):
        nonce += 1
        if nonce % 1e5 == 0:
            print(f"nonce = {nonce}")
        encoded_input = f"{preimage}{nonce}".encode("utf-8")
        hashed_image = sha256(encoded_input).hexdigest()

    # print solution nonce and hash value
    print(f"Solution found with nonce = {nonce}, hash = {hashed_image}")
    print(f"Time elapsed: {round(time() - start_time, 4)} seconds")
    return hashed_image


# run miner
my_miner("name=Fabian, lastblock=182, transactions=(1, 2, 3), nonce=", leading_zeros=5)
