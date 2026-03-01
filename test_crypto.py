import os
import db
import crypto

def run_tests():
    if os.path.exists(db.DB_FILE):
        os.remove(db.DB_FILE)
    
    db.init_db()
    uid = db.create_user("test_user")
    
    print("Testing Vault Initialization...")
    crypto.initialize_vault(uid, "foo", "bar", "What is my name?", "Antigravity")
    
    print("Testing Unlock with Main Passwords (Correct)...")
    master_key = crypto.unlock_vault_main(uid, "foo", "bar")
    assert master_key is not None, "Failed to unlock with correct main passwords"
    
    print("Testing Unlock with Main Passwords (Incorrect)...")
    assert crypto.unlock_vault_main(uid, "foo", "baz") is None, "Unlocked with incorrect main passwords"
    
    print("Testing Encrypt/Decrypt Credentials...")
    enc = crypto.encrypt_password(master_key, "supersecret")
    db.add_credential(uid, "GitHub", "my_user", enc)
    
    creds = db.get_all_credentials(uid)
    assert len(creds) == 1
    assert creds[0][1] == "GitHub"
    assert creds[0][2] == "my_user"
    
    dec = crypto.decrypt_password(master_key, creds[0][3])
    assert dec == "supersecret", "Decrypted password does not match"
    
    print("Testing Unlock with Recovery Question (Correct)...")
    rec_key = crypto.unlock_vault_recovery(uid, "antigravity")
    assert rec_key is not None, "Failed to unlock with correct recovery answer"
    assert rec_key == master_key, "Recovery key did not unlock the same master key"
    
    print("Testing Password Reset...")
    crypto.reset_main_passwords(uid, rec_key, "new1", "new2")
    assert crypto.unlock_vault_main(uid, "foo", "bar") is None, "Old passwords still worked after reset"
    new_master_key = crypto.unlock_vault_main(uid, "new1", "new2")
    assert new_master_key is not None, "Failed to unlock with new main passwords"
    
    dec2 = crypto.decrypt_password(new_master_key, creds[0][3])
    assert dec2 == "supersecret", "Decrypted password does not match after reset"
    
    print("All backend tests passed!")

if __name__ == "__main__":
    run_tests()
