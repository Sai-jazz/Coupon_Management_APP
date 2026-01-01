Coupon Manager System 🎫
A secure and feature-rich PyQt5-based coupon management system with automated password generation, WhatsApp integration, and encrypted configuration.

🌟 Features
🔒 Security
Dual Password Authentication: Separate passwords for app access and coupon generation

Encrypted Configuration: .env files encrypted using Fernet cryptography

Automated Password Rotation: Generation password changes automatically after use

Secure Logging: All button actions are logged with timestamps

🎫 Coupon Management
Bulk Generation: Generate single or multiple coupons (up to 100 at once)

Multiple Types: Regular, Premium, and VIP coupon categories

Custom Expiry: Set expiration periods from 1 to 365 days

Real-time Validation: Check coupon validity with customer details capture

Visual Status Indicators: Color-coded rows (Green=Used, Yellow=Valid, Pink=Expired)

📱 Integration
WhatsApp Sharing: Directly share coupons via WhatsApp

CSV Export: Export coupon data to CSV files

Customer Database: Store customer details with validation timestamps

Automatic Updates: Real-time statistics and expiry checking

📁 Project Structure
text
coupon_manager/
├── coupandon.py              # Main application file
├── genpass.py               # Password generation algorithm
├── encrypt.py               # Encryption key generator
├── .env.enc                 # Encrypted configuration file (generated)
├── fuffin.json             # Coupon database
├── button_logs.csv         # User action logs
├── customer_details.csv    # Customer information
├── appic.ico              # Application icon
└── refresh.png            # Refresh button icon
🔧 Installation
Prerequisites
Python 3.8+

pip package manager

Step 1: Install Dependencies
bash
pip install PyQt5 cryptography python-dotenv
Step 2: Generate Encryption Key
Run encrypt.py to create your encryption key:

bash
python encrypt.py
Save the generated key (you'll need it for step 4).

Step 3: Create .env File
Create a file named .env in the project directory with:

env
PASSWORD=your_main_app_password
GEN_PASS=initial_generation_password
Replace with your desired passwords.

Step 4: Update Encryption Key
In coupandon.py, replace line 13 with your generated key:

python
ENCRYPTION_KEY = b'YOUR_GENERATED_KEY_HERE'
Step 5: First Run
Run the application:

bash
python coupandon.py
The system will automatically encrypt your .env file into .env.enc.

🚀 Usage Guide
Starting the Application
Launch the app with python coupandon.py

Enter the main password (from your original .env file)

Generating Coupons
Click "Generate Coupon" or "Generate 100 Coupons"

Enter the generation password (auto-rotates after use)

Select number of coupons (for single generation)

Choose coupon type: Regular, Premium, or VIP

Set expiry days (1-365)

Optional: Share immediately via WhatsApp

Validating Coupons
Enter coupon code in the text field

Click "Validate Coupon"

Enter customer name and phone number

System automatically marks coupon as "Used"

Managing Coupons
Search: Filter by code, status, or date

Remove Used/Expired: Clean up old coupons

Remove Unshared: Delete coupons never shared

Export to CSV: Save all data to spreadsheet

Refresh: Update view and statistics

Password Recovery
If the generation password expires:

Click "Help" button

Select "Get New Generation Password"

System sends WhatsApp request to admin

Admin provides new password

🔐 Security Features Explained
Password Generation Algorithm
The system uses a deterministic algorithm (genpass.py):

text
Password = f"{code_part}-{checksum}"
Where:

code_part = First 4 digits of (date_digits × SECRET_KEY) mod 10

checksum = Sum of date_digits mod 10

Date format: MMHRDay (minute, hour, year)

File Encryption
.env → .env.enc using Fernet encryption

Key stored in code (for demo; move to secure storage in production)

Decryption happens in memory only

Action Logging
Every button press is logged to button_logs.csv:

csv
Button Name,Timestamp
Generate Coupon,2025-04-10 17:41:49
📊 Data Files
fuffin.json
Stores all coupon data in JSON format:

json
{
  "C1477D25": {
    "status": "Valid",
    "timestamp": "2025-04-09 22:18:53",
    "expiry": "2025-07-18 22:18:53",
    "shared": true,
    "type": "Premium"
  }
}
customer_details.csv
Records all validations:

csv
Coupon Code,Customer Name,Phone Number,Validation Date
4CA277D2,k.sairaj,9014190770,2025-04-05 19:30:07
button_logs.csv
Tracks all user actions for audit:

csv
Button Name,Timestamp
Generate Coupon,2025-04-10 17:41:49
🎨 UI Components
Main Window Layout
text
┌─────────────────────────────────────────────┐
│                 COUP&ON                     │
├─────────────────────────────────────────────┤
│ [ Search Box ]                              │
│ [Coupon Code] [Validate Coupon]            │
├─────────────────────────────────────────────┤
│ Generate: [Single] [100]                    │
│ [Share Selected] [Remove Used] [Export CSV] │
│ [Remove Unshared]                           │
├─────────────────────────────────────────────┤
│ Statistics: Valid - X | Used - Y | Expired - Z│
├─────────────────────────────────────────────┤
│ Code   Status  Created  Expiry   Shared  Type│
│ ABC123 Valid   2025-... 2025-... Yes     VIP│
│ DEF456 Used    2025-... 2025-... No      Reg│
└─────────────────────────────────────────────┘
Color Coding
Light Green: Used coupons

Light Yellow: Valid coupons

Light Pink/Red: Expired coupons

⚙️ Configuration
Environment Variables
Create .env file with:

env
PASSWORD=admin123          # Main app password
GEN_PASS=1234-5            # Initial generation password
Constants in coupandon.py
python
MODEL_PATH = "bilirubin_lstm_model.h5"  # Not used in this app
SCALER_PATH = "scaler.pkl"              # Not used in this app
EPOCHS = 100                            # Not used in this app
BATCH_SIZE = 8                          # Not used in this app
ENCRYPTION_KEY = b'...'                 # Your Fernet key
🔄 Password Rotation Flow
text
User clicks "Generate Coupon"
    ↓
System asks for current GEN_PASS
    ↓
User enters correct password
    ↓
System generates coupons
    ↓
System generates NEW password using genpass.py
    ↓
System encrypts and saves new password to .env.enc
    ↓
Old password becomes invalid
🚨 Error Handling
The system handles:

Invalid passwords with warning messages

Missing files with clear error prompts

Invalid coupon codes with appropriate feedback

Expired coupons with automatic status update

File permission issues with user-friendly messages

📱 WhatsApp Integration
Sharing Coupons
Select coupons from the list

Click "Share Selected Coupons"

WhatsApp opens with formatted message:

text
Hey! You know there's a restaurant near you with great food.
Hurry up! These coupons are valid only until their expiry dates.

C1477D25 (Valid until: 18 Jul 2025)
55D2343D (Valid until: 18 Jul 2025)
Password Requests
When generation password expires, system creates WhatsApp message to admin:

text
New Generation Password Request

Latest generation timestamp: 2025-04-10 23:10:30
💾 Backup and Recovery
Regular Backups
fuffin.json: Your main coupon database

customer_details.csv: Customer information

button_logs.csv: Audit trail

Recovery Process
If files are corrupted:

Restore from backup

Ensure .env.enc exists

Run application normally

🐛 Troubleshooting
Common Issues
"Failed to decrypt configuration"

Ensure .env.enc file exists

Check encryption key matches in code

"No patient has enough data" (incorrect error message)

Ensure CSV file has correct format

Check column names: PatientID, Day, Bilirubin

WhatsApp not opening

Ensure WhatsApp is installed

Check internet connection

Password not working

Check system date/time is correct

Contact admin for new password

Log Files
Check these files for debugging:

button_logs.csv - User actions

Console output - Runtime errors

🔮 Future Enhancements
Planned features:

Database integration (SQLite/MySQL)

Web dashboard

Email notifications

Barcode/QR code generation

Advanced reporting

Multi-user support

Cloud backup

📝 License
This project is for educational/demo purposes. Commercial use may require modifications.

👥 Contributing
Fork the repository

Create a feature branch

Commit your changes

Push to the branch

Create a Pull Request

⚠️ Disclaimer
This is a demonstration system. For production use:

Implement proper key management

Add database encryption

Include user role management

Add comprehensive logging

Conduct security audit

🆘 Support
For issues or questions:

Check the troubleshooting section

Review log files

Contact the development team
