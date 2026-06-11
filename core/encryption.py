import os
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent
SECRETS_DIR = BASE_DIR / 'secrets'
PRIVATE_KEY_PATH = SECRETS_DIR / 'private_key.pem'
PUBLIC_KEY_PATH = SECRETS_DIR / 'public_key.pem'
ENCRYPTED_AES_KEY_PATH = SECRETS_DIR / 'encrypted_aes_key.bin'

_cipher = None

def _initialize_keys():
    """
    Checks if cryptographic keys exist. If not, generates RSA keys, 
    creates a random AES (Fernet) key, encrypts it with RSA, and saves it.
    """
    global _cipher
    
    if _cipher is not None:
        return

    # Ensure secrets directory exists
    SECRETS_DIR.mkdir(exist_ok=True)

    # 1. Generate keys if they do not exist
    if not (PRIVATE_KEY_PATH.exists() and ENCRYPTED_AES_KEY_PATH.exists()):
        # Generate RSA Key Pair
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()

        # Save Private Key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(PRIVATE_KEY_PATH, 'wb') as f:
            f.write(private_pem)

        # Save Public Key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(PUBLIC_KEY_PATH, 'wb') as f:
            f.write(public_pem)

        # Generate AES (Fernet) Key
        aes_key = Fernet.generate_key()

        # Encrypt (Wrap) the AES key using the RSA Public Key (Hybrid Encryption)
        encrypted_aes_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Save Encrypted AES Key
        with open(ENCRYPTED_AES_KEY_PATH, 'wb') as f:
            f.write(encrypted_aes_key)

    # 2. Load and Decrypt the AES key
    with open(PRIVATE_KEY_PATH, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )

    with open(ENCRYPTED_AES_KEY_PATH, 'rb') as f:
        encrypted_aes_key = f.read()

    # Decrypt (Unwrap) the AES key using the RSA Private Key
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Initialize Fernet cipher with the decrypted key
    _cipher = Fernet(aes_key)

def encrypt(value: str) -> str:
    """
    Encrypts a string value using the hybrid-decrypted AES key.
    """
    if not value:
        return value
    _initialize_keys()
    # Fernet requires bytes and returns bytes
    encrypted_bytes = _cipher.encrypt(value.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')

def decrypt(value: str) -> str:
    """
    Decrypts a string value using the hybrid-decrypted AES key.
    """
    if not value:
        return value
    _initialize_keys()
    try:
        decrypted_bytes = _cipher.decrypt(value.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception:
        # Fallback in case of decryption failure or unencrypted database data
        return value
