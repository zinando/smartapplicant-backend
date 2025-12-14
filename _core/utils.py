import json
from cryptography.fernet import Fernet
from django.conf import settings

def encrypt_data(data) -> str:
    """
    Encrypt data using Fernet symmetric encryption.
    Data can be a string or a dictionary (which will be converted to JSON).
    Returns the encrypted data as a base64 encoded string.
    """
    fernet = Fernet(settings.FERNET_KEYS[0])

    if isinstance(data, dict):
        data = json.dumps(data).encode('utf-8')

    if isinstance(data, str):
        data = data.encode('utf-8')

    encrypted_data = fernet.encrypt(data)
    return encrypted_data.decode('utf-8')

def decrypt_data(encrypted_data: str) -> str | dict:
    """
    Decrypt data using Fernet symmetric encryption.
    Returns the decrypted data as a string or dictionary (if JSON).
    """
    fernet = Fernet(settings.FERNET_KEYS[0])
    decrypted_data = fernet.decrypt(encrypted_data.encode('utf-8'))
    try:
        return json.loads(decrypted_data.decode('utf-8'))
    except json.JSONDecodeError:
        return decrypted_data.decode('utf-8')
