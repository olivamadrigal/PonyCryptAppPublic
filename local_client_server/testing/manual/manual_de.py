from cryptosteganography import CryptoSteganography


fp = open("key.txt", "r")
key = fp.readline()
fp.close()

# cs object
cs = CryptoSteganography(key)


# modify as your wish -- keep it small
fp = open("secret.txt", "r")
expected = fp.readline()
fp.close()

# https://photos.google.com/photo/AF1QipNOXP3bIDq1dNtBw7I0md34zZ4BB5x4vKGzhoUN
# when you view photo, click the 3 dots at top right corner and select
# Download from options menu
# download crypto.png from google and name it verify.png
actual = cs.retrieve('verify.png')
print(expected)
print(actual)
assert actual == expected

# now run the script
