import os
from hashlib import sha256
from hmac import HMAC
from base64 import b64encode, b64decode


def encrypt_password(password, salt=None):
    """Hash password on the fly."""
    if salt is None:
        salt = os.urandom(8)  # 64 bits.

    assert 8 == len(salt)
    assert isinstance(salt, bytes)
    assert isinstance(password, str)

    if isinstance(password, str):
        password = password.encode('UTF-8')

    assert isinstance(password, bytes)

    result = password
    for i in range(10):
        result = HMAC(result, salt, sha256).digest()

    return b64encode(salt + result)


def validate_password(hashed, input_password):
    return hashed == encrypt_password(input_password, salt=b64decode(hashed)[:8])
