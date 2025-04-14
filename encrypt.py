from cryptography.fernet import Fernet

# Generate a key (run this once)
key = Fernet.generate_key()
print("Your encryption key:", key.decode())  # Save this securely!