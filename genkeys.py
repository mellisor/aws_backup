#!/usr/bin/env python3

# Don't run this unless you want to overwrite your rsa keys

from Crypto.PublicKey import RSA
import configparser
import os

# Reads config file at given path
def loadConfig(path):
    conf = configparser.ConfigParser()
    conf.readfp(open(path))
    return conf

# Load config file
conf = loadConfig(os.path.join(os.path.dirname(__file__),'backup.conf'))

code = conf.get('KEY','passphrase')
private_key = conf.get('KEY','private_key')
public_key = conf.get('KEY','public_key')

key = RSA.generate(2048)
encrypted_key = key.exportKey(passphrase=code,pkcs=8)

with open(private_key,'wb') as f:
    f.write(encrypted_key)

with open(public_key,'wb') as f:
    f.write(key.publickey().exportKey())