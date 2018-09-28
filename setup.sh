sudo apt-get install python3-pip
sudo pip3 install pycryptodome
sudo pip3 install boto3

mkdir keys

echo "[INCLUDES]

include = ['/etc/','/usr/local/bin']
exclude = ['shadow','passwd','gshadow','sudoers','group','authorized_keys','id_rsa','known_hosts']

[INFO]

bucket_name = this-is-the-best-bucket
host_name = test

[KEY]

public_key = "$PWD"/keys/public_rsa.pem
private_key = "$PWD"/keys/private_rsa.bin
passphrase = TestCode

AWS_ACCESS_KEY_ID = YOURACESSKEYHERE
AWS_SECRET_ACCESS_KEY = YOURSECRETACCESSKEYHERE" > backup.conf