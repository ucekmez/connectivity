#!/usr/bin/python
# -*- coding: utf-8 -*-

from cryptography.fernet import Fernet
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Crypto():
    def __init__(self, key=None, payload=None):
        self.payload   = payload
        self.key       = self.generate_key(key) if key else Fernet.generate_key()
        self.algorithm = Fernet(self.key)
        self.cipher    = b''
        self.filename  = ''
        self.password  = b''
        self.key       = b''

    def generate_key(self, password):
        self.password = bytes(password, encoding='utf-8')
        salt     = b'salt_'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        # Can only use kdf once
        self.key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return self.key

    def encrypt(self, filename=None):
        payload       = self.payload if type(self.payload) == bytes else bytes(self.payload, encoding='utf-8')
        self.cipher   = self.algorithm.encrypt(payload)
        self.filename = filename
        f             = open(self.filename, "wb")
        f.write(self.cipher)
        f.close()
        return self.filename if self.filename else self.cipher

    def decrypt(self, filename=None, key=None):
        if self.algorithm:
            return self.algorithm.decrypt(self.cipher)
        else:
            self.cipher    = open(filename, "rb").read()
            self.key       = key if type(key) == bytes else self.generate_key(key)
            self.algorithm = Fernet(key)
            self.payload   = self.algorithm.decrypt(self.cipher)
            return self.payload


if __name__ == '__main__':
    print('Crypto encryption - decryption module using Fernet')



# EOF
