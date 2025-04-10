from datetime import datetime

def generate_new_password():
    """Generates a password using a deterministic but hard-to-reverse algorithm."""
    # Secret key (change this to your own number)
    SECRET_KEY = 3956
    
    # Get current date as MMHRDay
    today = datetime.now().strftime("%M%H%Y")#minute,hour,year.
    date_digits = [int(c) for c in today]  # Convert to list of digits
    
    # Multiply each digit by the secret key and take modulo 10
    shifted_digits = [(d * SECRET_KEY) % 10 for d in date_digits]
    
    # Take the first 4 digits
    code_part = ''.join(map(str, shifted_digits[:4]))
    
    # Calculate checksum (sum of all date digits, modulo 10)
    checksum = sum(date_digits) % 10
    
    # Final password format: DDDD-X
    return f"{code_part}-{checksum}"


new_passkey = generate_new_password()

