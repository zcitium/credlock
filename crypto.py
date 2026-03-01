import base64
import os
import secrets
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from cryptography.exceptions import InvalidKey
import db

def generate_salt() -> bytes:
    return secrets.token_bytes(16)

def derive_key(password_string: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return kdf.derive(password_string.encode('utf-8'))

def generate_verification_hash(key_bytes: bytes) -> str:
    digest = hashes.Hash(hashes.SHA256())
    digest.update(key_bytes)
    return base64.b64encode(digest.finalize()).decode('utf-8')

def verify_key(key_bytes: bytes, stored_hash: str) -> bool:
    return generate_verification_hash(key_bytes) == stored_hash

def initialize_vault(user_id: int, pw1: str, pw2: str, recovery_q: str, recovery_a: str):
    salt_main = generate_salt()
    salt_recovery = generate_salt()

    combined_pwd = pw1 + "|" + pw2
    main_key = derive_key(combined_pwd, salt_main)
    recovery_key = derive_key(recovery_a.strip().lower(), salt_recovery)

    master_key = Fernet.generate_key()

    fern_main = Fernet(base64.urlsafe_b64encode(main_key))
    fern_rec = Fernet(base64.urlsafe_b64encode(recovery_key))

    wrapped_master_key_main = fern_main.encrypt(master_key)
    wrapped_master_key_rec = fern_rec.encrypt(master_key)

    verify_hash_main = generate_verification_hash(main_key)
    verify_hash_rec = generate_verification_hash(recovery_key)

    db.set_config(user_id, "salt_main", base64.b64encode(salt_main).decode('utf-8'))
    db.set_config(user_id, "salt_recovery", base64.b64encode(salt_recovery).decode('utf-8'))
    
    db.set_config(user_id, "verify_hash_main", verify_hash_main)
    db.set_config(user_id, "verify_hash_rec", verify_hash_rec)

    db.set_config(user_id, "wrapped_master_main", base64.b64encode(wrapped_master_key_main).decode('utf-8'))
    db.set_config(user_id, "wrapped_master_rec", base64.b64encode(wrapped_master_key_rec).decode('utf-8'))
    
    db.set_config(user_id, "recovery_question", recovery_q)

def unlock_vault_main(user_id: int, pw1: str, pw2: str):
    salt_b64 = db.get_config(user_id, "salt_main")
    if not salt_b64: return None
    
    salt = base64.b64decode(salt_b64)
    combined = pw1 + "|" + pw2
    main_key = derive_key(combined, salt)

    stored_hash = db.get_config(user_id, "verify_hash_main")
    if not stored_hash or not verify_key(main_key, stored_hash):
        return None

    wrapped_master_b64 = db.get_config(user_id, "wrapped_master_main")
    wrapped_master = base64.b64decode(wrapped_master_b64)
    
    try:
        fern_main = Fernet(base64.urlsafe_b64encode(main_key))
        master_key = fern_main.decrypt(wrapped_master)
        return master_key
    except InvalidKey:
        return None

def unlock_vault_recovery(user_id: int, recovery_a: str):
    salt_b64 = db.get_config(user_id, "salt_recovery")
    if not salt_b64: return None
    
    salt = base64.b64decode(salt_b64)
    rec_key = derive_key(recovery_a.strip().lower(), salt)

    stored_hash = db.get_config(user_id, "verify_hash_rec")
    if not stored_hash or not verify_key(rec_key, stored_hash):
        return None

    wrapped_master_b64 = db.get_config(user_id, "wrapped_master_rec")
    wrapped_master = base64.b64decode(wrapped_master_b64)
    
    try:
        fern_rec = Fernet(base64.urlsafe_b64encode(rec_key))
        master_key = fern_rec.decrypt(wrapped_master)
        return master_key
    except InvalidKey:
        return None

def reset_main_passwords(user_id: int, master_key: bytes, pw1: str, pw2: str):
    salt_main = generate_salt()
    combined_pwd = pw1 + "|" + pw2
    main_key = derive_key(combined_pwd, salt_main)

    fern_main = Fernet(base64.urlsafe_b64encode(main_key))
    wrapped_master_key_main = fern_main.encrypt(master_key)
    verify_hash_main = generate_verification_hash(main_key)

    db.set_config(user_id, "salt_main", base64.b64encode(salt_main).decode('utf-8'))
    db.set_config(user_id, "verify_hash_main", verify_hash_main)
    db.set_config(user_id, "wrapped_master_main", base64.b64encode(wrapped_master_key_main).decode('utf-8'))

def encrypt_password(master_key: bytes, plaintext_password: str) -> str:
    f = Fernet(master_key)
    return f.encrypt(plaintext_password.encode('utf-8')).decode('utf-8')

def decrypt_password(master_key: bytes, encrypted_password: str) -> str:
    f = Fernet(master_key)
    return f.decrypt(encrypted_password.encode('utf-8')).decode('utf-8')

def get_recovery_question(user_id: int) -> str:
    return db.get_config(user_id, "recovery_question") or ""
