from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import base64

def generate_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def hybrid_encrypt(pubkey, plaintext):
    # Generate AES key
    aes_key = get_random_bytes(16)  # AES-128
    cipher_aes = AES.new(aes_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(plaintext.encode())

    # Encrypt AES key with RSA
    rsa_key = RSA.import_key(pubkey)
    cipher_rsa = PKCS1_OAEP.new(rsa_key)
    enc_aes_key = cipher_rsa.encrypt(aes_key)

    # Package all (base64 encode for transport)
    payload = {
        'enc_aes_key': base64.b64encode(enc_aes_key).decode(),
        'nonce': base64.b64encode(cipher_aes.nonce).decode(),
        'tag': base64.b64encode(tag).decode(),
        'ciphertext': base64.b64encode(ciphertext).decode()
    }
    return payload

def hybrid_decrypt(privkey, payload):
    # Decode all parts
    enc_aes_key = base64.b64decode(payload['enc_aes_key'])
    nonce = base64.b64decode(payload['nonce'])
    tag = base64.b64decode(payload['tag'])
    ciphertext = base64.b64decode(payload['ciphertext'])

    # Decrypt AES key with RSA
    rsa_key = RSA.import_key(privkey)
    cipher_rsa = PKCS1_OAEP.new(rsa_key)
    aes_key = cipher_rsa.decrypt(enc_aes_key)

    # Decrypt message with AES
    cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce)
    plaintext = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode()