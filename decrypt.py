#!/usr/bin/env python3
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES,PKCS1_OAEP
import configparser
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file',help='The file to decrypt')
parser.add_argument('-k','--key',help='Private key to use')
parser.add_argument('-p','--passphrase',help='Passphrase for key')
args = parser.parse_args()

# Reads config file at given path
def loadConfig(path):
    conf = configparser.ConfigParser()
    conf.readfp(open(path))
    return conf

# Load config file
conf = loadConfig(os.path.join(os.path.dirname(__file__),'backup.conf'))

if args.passphrase:
    code = args.passphrase
else:
    code = conf.get('KEY','passphrase')

if args.key:
    private_key = args.key
else:
    private_key = conf.get('KEY','private_key')
try:
    with open(args.file,'rb') as fobj:
        # Gets private key
        private_key = RSA.import_key(open(private_key).read(),passphrase=code)
        
        enc_session_key, nonce, tag, ciphertext = [ fobj.read(x) for x in (private_key.size_in_bytes(),16,16,-1) ]

        # Sets up cipher
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt data
        cipher_aes = AES.new(session_key, AES.MODE_EAX,nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext,tag)

        # Parse output file name from path
        out_file = '.'.join(args.file.split('/')[-1].split('.')[:-1])
        with open(out_file,'wb') as f:
            f.write(data)
except ValueError as v:
    print(v)
except TypeError as t:
    print("Incorrect Key")
except Exception as e:
    print(e)