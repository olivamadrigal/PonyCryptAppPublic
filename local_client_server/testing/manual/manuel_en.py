from cryptosteganography import CryptoSteganography
import random

# this is ran only once, MUST USE SAME KEY TO ENCRYPT & DECRYPT
# key = str(random.getrandbits(256))  # pseudo-random number generator
# fp = open("key.txt", "w")
# fp.write(key)
# fp.close()

fp = open("key.txt", "r")
key = fp.readline()
fp.close()

# cs object
cs = CryptoSteganography(key)
# modify as your wish -- keep it small
secret = 'e=mc2'
# save secret in a file
fp = open("secret.txt", "w")
fp.write(secret)
fp.close()

cs.hide('test.png', 'crypto.png', secret)
# upload crypto.png to a google photos album (MANUALLY) drop it in


