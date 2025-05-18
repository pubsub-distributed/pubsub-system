from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes

def generate_keys():
    key = RSA.generate(2048)
    return key.export_key(), key.publickey().export_key()

def encrypt_message(pubkey, plaintext):
    rsa_key = RSA.import_key(pubkey)
    cipher = PKCS1_OAEP.new(rsa_key)
    return cipher.encrypt(plaintext.encode())

def decrypt_message(privkey, ciphertext):
    rsa_key = RSA.import_key(privkey)
    cipher = PKCS1_OAEP.new(rsa_key)
    return cipher.decrypt(ciphertext).decode()