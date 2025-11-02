import bcrypt

# The stored hash from auth.py
stored_hash = b"$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqHGjKT6em"

# Test password
test_password = "admin123"

# Try to verify
try:
    result = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash)
    print(f"Password verification result: {result}")
except Exception as e:
    print(f"Error: {e}")

# Let's create a fresh hash for "admin123"
print("\n--- Creating fresh hash for 'admin123' ---")
fresh_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
print(f"Fresh hash: {fresh_hash}")

# Verify the fresh hash works
verify_fresh = bcrypt.checkpw("admin123".encode('utf-8'), fresh_hash)
print(f"Fresh hash verification: {verify_fresh}")
