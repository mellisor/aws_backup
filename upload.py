#!/usr/bin/env python3


import boto3
import sys
import tarfile
import os
import configparser
import json
import datetime
# For encryption
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
# For string to list conversion
import ast

# Reads config file at given path
def loadConfig(path):
    conf = configparser.ConfigParser()
    conf.readfp(open(path))
    return conf

# Load config file
conf = loadConfig(os.path.join(os.path.dirname(__file__),'backup.conf'))

# Parse lists from config file
exclude = ast.literal_eval(conf.get('INCLUDES','exclude'))
include = ast.literal_eval(conf.get('INCLUDES','include'))

# Filter out any files that start with excluded keywords
def filter(info):
    name = info.name.split('/')[-1].lower()
    for item in exclude:
        if name.startswith(item):
            print('Excluding: ' + name)
            return None
    return info

# Write tar file
def do_tar(out_file):
    pardir = out_file.split('.')[0].split('/')[-1]
    with tarfile.open(out_file,"w:gz") as tar:
        for dir in include:
            print("Including: " + pardir + dir)
            tar.add(dir, arcname = pardir + dir,filter=filter)

# Get bucket name and keys from config file
bucket_name = conf.get('INFO','bucket_name')
access_key = conf.get('KEY','AWS_ACCESS_KEY_ID')
secret_key = conf.get('KEY','AWS_SECRET_ACCESS_KEY')

# Create the s3 client
s3 = boto3.client('s3',aws_access_key_id=access_key,aws_secret_access_key=secret_key)

# Create tar file
host_name = conf.get('INFO','host_name')
out_file = '/tmp/' + host_name + '-' + str(datetime.date.today()) + ".tar.gz"
do_tar(out_file)

""" ENCRYPT THE FILE """

enc_file = out_file + '.enc'
public_key = conf.get('KEY','public_key')

with open(enc_file,'wb') as enc:
    recip_key = RSA.import_key(open(public_key).read())
    session_key = get_random_bytes(16)
    cipher_rsa = PKCS1_OAEP.new(recip_key)
    enc.write(cipher_rsa.encrypt(session_key))
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    data = b''
    with open(out_file,'rb') as e:
        data = e.read()
    ciphertext,tag = cipher_aes.encrypt_and_digest(data)
    enc.write(cipher_aes.nonce)
    enc.write(tag)
    enc.write(ciphertext)

"""           END         """

# Upload file
try:
    # Try to upload the file
    s3.upload_file(enc_file,bucket_name,enc_file.split('/')[-1])
except boto3.exceptions.S3UploadFailedError:
    # The bucket didn't exist, create bucket
    s3.create_bucket(Bucket=bucket_name)
    s3.upload_file(enc_file,bucket_name,enc_file.split('/')[-1])
except Exception as e:
    print(e)
# Remove the files
os.remove(enc_file)
os.remove(out_file)
