import rsa as rsa


def generate_keys(public_key_file, private_key_file):
    public_key, private_key = rsa.newkeys(1024)
    print(public_key)
    print(private_key)
    with open(public_key_file, 'wb') as f:
        f.write(public_key.save_pkcs1('PEM'))
    with open(private_key_file, 'wb') as f:
        f.write(private_key.save_pkcs1('PEM'))


def load_Public_key(Public_key_file):
    with open(Public_key_file, 'rb') as f:
        public_key = rsa.PublicKey.load_pkcs1(f.read())
        return public_key

def load_Private_key(Private_key_file):
    with open(Private_key_file, 'rb') as f:
        private_key = rsa.PrivateKey.load_pkcs1(f.read())
        return private_key


def encrypt(mes, key):
    return rsa.encrypt(mes.encode('UTF-8'), key)


def decrypt(ciphertext, key):
    try:
        return rsa.decrypt(ciphertext, key).decode('UTF-8')
    except:
        return False


def sign_sha1(msg, key):
    return rsa.sign(msg, key, 'SHA-1')


def verify_sha1(msg, signature, publick_key):
    try:
        return rsa.verify(msg, signature, publick_key) == 'SHA-1'
    except:
        return False
