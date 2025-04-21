from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QIcon
import json
from cryptography.fernet import Fernet
import uuid
import webbrowser
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import sys
from genpass import generate_new_password

from cryptography.fernet import Fernet
import os

# Replace this with your actual key (from step 1)
ENCRYPTION_KEY = b'cFdQ9rtHU_JaVWqqkQjSC75fTpr2V3IJHJhFj3HQjVs='

def encrypt_env_file():
    """Encrypt the current .env file"""
    cipher_suite = Fernet(ENCRYPTION_KEY)
    env_path = resource_path('.env')
    encrypted_path = resource_path('.env.enc')
    
    try:
        with open(env_path, 'rb') as file:
            file_data = file.read()
        
        encrypted_data = cipher_suite.encrypt(file_data)
        
        with open(encrypted_path, 'wb') as file:
            file.write(encrypted_data)
            
        # Remove the plaintext file (optional but recommended)
        os.remove(env_path)
        return True
    except Exception as e:
        print(f"Encryption failed: {e}")
        return False

def decrypt_env_file():
    """Decrypt the .env.enc file when needed"""
    cipher_suite = Fernet(ENCRYPTION_KEY)
    encrypted_path = resource_path('.env.enc')
    
    try:
        with open(encrypted_path, 'rb') as file:
            encrypted_data = file.read()
        
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        
        # Only keep decrypted data in memory, don't write to disk
        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"Decryption failed: {e}")
        return None


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    For writable data files (.json), uses either:
    - The executable directory (when frozen)
    - The current directory (when in development)
    """
    try:
        # Handle PyInstaller bundled case
        if getattr(sys, 'frozen', False):
            # For data files that need to be writable (like JSON)
            if (relative_path.endswith('.json') or relative_path.endswith('.csv') or 
            relative_path.endswith('.env')or 
            relative_path.endswith('.enc')):
                # Use the directory where the executable resides
                base_path = os.path.dirname(sys.executable)
            else:
                # Use PyInstaller's temp folder for read-only resources
                base_path = sys._MEIPASS
        else:
            # Normal development case
            base_path = os.path.abspath(".")
        
        # Create directory if it doesn't exist (only for JSON/data files)
        if (relative_path.endswith('.json') or relative_path.endswith('.csv') or 
            relative_path.endswith('.env')or relative_path.endswith('.enc')
            ):
            os.makedirs(base_path, exist_ok=True)
        
        full_path = os.path.join(base_path, relative_path)
        return full_path
        
    except Exception as e:
        print(f"Error in resource_path: {e}")
        # Fallback to current directory
        return os.path.join(os.path.abspath("."), relative_path)

def load_secure_env():
    """Load environment variables from encrypted file"""
    decrypted_content = decrypt_env_file()
    if not decrypted_content:
        QtWidgets.QMessageBox.critical(None, "Error", "Failed to decrypt configuration")
        raise SystemExit
    
    # Parse the decrypted content into environment variables
    for line in decrypted_content.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            key, value = line.split('=', 1)
            os.environ[key] = value


def log_button_press(button_name):
    """Log button presses with timestamp to a CSV file."""
    try:
        filename = resource_path("button_logs.csv")
        os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
        file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0
        
        with open(filename, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Button Name", "Timestamp"])
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([button_name, timestamp])
            
        return True
    except Exception as e:
        print(f"Error logging button press: {e}")
        return False


def update_env_file(new_gen_pass):
    """Update the GEN_PASS in the encrypted .env file"""
    try:
        # Get current decrypted content
        decrypted_content = decrypt_env_file()
        if not decrypted_content:
            return False
        
        # Update the GEN_PASS line
        lines = decrypted_content.splitlines()
        updated = False
        new_lines = []
        
        for line in lines:
            if line.startswith("GEN_PASS="):
                new_lines.append(f"GEN_PASS={new_gen_pass}")
                updated = True
            else:
                new_lines.append(line)
        
        if not updated:
            new_lines.append(f"GEN_PASS={new_gen_pass}")
        
        # Re-encrypt the updated content
        cipher_suite = Fernet(ENCRYPTION_KEY)
        encrypted_data = cipher_suite.encrypt('\n'.join(new_lines).encode())
        
        with open(resource_path('.env.enc'), 'wb') as file:
            file.write(encrypted_data)
        
        # Update in-memory environment
        os.environ["GEN_PASS"] = new_gen_pass
        return True
        
    except Exception as e:
        print(f"Error updating encrypted env: {e}")
        return False


# If this is the first run and you have a plain .env file
if os.path.exists(resource_path('.env')) and not os.path.exists(resource_path('.env.enc')):
    if encrypt_env_file():
        print("Successfully encrypted .env file")
    else:
        print("Failed to encrypt .env file")
load_secure_env()
COUPON_FILE = resource_path("fuffin.json")
PASSWORD = os.getenv("PASSWORD")  # Set your password here
GENERATION_PASSWORD = os.getenv("GEN_PASS")  # Set your password for generating coupons

def load_coupons():
    try:
        with open(COUPON_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_coupons(data, filename="fuffin.json"):
    try:
        filepath = resource_path(filename)
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        return True
    except Exception as e:
        QtWidgets.QMessageBox.critical(None,"save error", f"failed to save coupons:{str(e)}")
        return False

coupons = load_coupons()

def save_customer_details(coupon_code, customer_name, phone_number):
    """Save customer details to a CSV file."""
    try:
        filename = resource_path("customer_details.csv")
        os.makedirs(os.path.dirname(filename) or '.',exist_ok=True)
        file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0
        
        with open(filename, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Coupon Code", "Customer Name", "Phone Number", "Validation Date"])
            
            validation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([coupon_code, customer_name, phone_number, validation_date])
            
        return True
    except Exception as e:
        print(f"Error saving customer details: {e}")
        return False

class CouponManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon("appic.ico"))
        if not self.authenticate(PASSWORD, "Authentication"):
            QtWidgets.QMessageBox.critical(self, "Access Denied", "Incorrect password! Exiting...")
            raise SystemExit
        else:
            self.init_ui()
    
    def authenticate(self, required_password, title):
        password, ok = QtWidgets.QInputDialog.getText(self, title, "Enter Password:", QtWidgets.QLineEdit.Password)
        return ok and password == required_password
    
    def init_ui(self):
        self.setWindowTitle("Coupon Manager")
        self.setGeometry(100, 100, 1000, 800)
        self.layout = QtWidgets.QVBoxLayout()
        
        # Title
        self.title_label = QtWidgets.QLabel("COUP&ON")
        self.title_label.setFont(QtGui.QFont("Berosong", 20, QtGui.QFont.Bold))
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.title_label)
        
        # Search Bar
        self.search_layout = QtWidgets.QHBoxLayout()
        self.search_entry = QtWidgets.QLineEdit(self)
        self.search_entry.setFixedHeight(35)
        self.search_entry.setPlaceholderText("Search by Code, Status, or Date")
        self.search_entry.textChanged.connect(self.filter_coupons)
        self.search_layout.addWidget(self.search_entry)
        self.layout.addLayout(self.search_layout)
        
        # Coupon Entry and Validation
        self.entry_layout = QtWidgets.QHBoxLayout()
        self.coupon_entry = QtWidgets.QLineEdit(self)
        self.coupon_entry.setFixedHeight(40)
        self.coupon_entry.setPlaceholderText("Enter Coupon Code")
        self.entry_layout.addWidget(self.coupon_entry)
        
        self.validate_btn = QtWidgets.QPushButton("Validate Coupon", self)
        self.validate_btn.clicked.connect(self.validate_coupon)
        self.validate_btn.setFixedHeight(40)
        self.validate_btn.setFixedWidth(180)
        self.validate_btn.setStyleSheet("QPushButton{font-weight:bold;}")
        self.entry_layout.addWidget(self.validate_btn)
        self.layout.addLayout(self.entry_layout)
        
        self.group_box1 = QtWidgets.QGroupBox("Generate",self) #generate groupbox
       
        # Buttons for Actions
        self.generate_btn = QtWidgets.QPushButton("Generate Coupon", self) 
        self.generate_btn.setFixedSize(150, 40)  # Width: 150px, Height: 40px
        self.generate_btn.clicked.connect(self.generate_coupon)
        self.generate_btn.adjustSize()
        
        self.generate_100_btn = QtWidgets.QPushButton("Generate 100 Coupons", self)
        self.generate_100_btn.setFixedSize(180, 40)  # Width: 150px, Height: 40px
        self.generate_100_btn.clicked.connect(self.generate_100_coupons)
       
        h1_layout = QtWidgets.QHBoxLayout() #create horizontal layout
        h1_layout.addWidget(self.generate_btn)
        h1_layout.addWidget(self.generate_100_btn) 

        self.group_box1.setLayout(h1_layout) #set layout for group box
        self.layout.addWidget(self.group_box1)
        self.setLayout(self.layout)
      
        self.share_selected_btn = QtWidgets.QPushButton("Share Selected Coupons", self)
        self.share_selected_btn.setFixedSize(150, 40)  # Width: 150px, Height: 40px
        self.share_selected_btn.clicked.connect(self.share_selected_coupons)
        self.layout.addWidget(self.share_selected_btn)
        
        button_style = """
        QPushButton {
            background-color: none;
            color: black;
            border: 1px solid black;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: tomato;
        }
        
        QPushButton:pressed {
            background-color: red;
            padding-top: 9px;
            padding-bottom: 7px;
        }
    """
        
        self.group_box2 = QtWidgets.QGroupBox("Remove",self) #generate groupbox

        self.remove_used_btn = QtWidgets.QPushButton("Remove Used and expired ", self)
        self.remove_used_btn.setFixedSize(180, 40)  # Width: 150px, Height: 40px
        self.remove_used_btn.clicked.connect(self.remove_used_coupons)
        
        self.remove_unshared_btn = QtWidgets.QPushButton("Remove Unshared Coupons", self)
        self.remove_unshared_btn.setFixedSize(250, 40)  # Width: 150px, Height: 40px
        self.remove_unshared_btn.clicked.connect(self.remove_unshared_coupons)
        self.remove_unshared_btn.setStyleSheet(button_style)
        
        h2_layout = QtWidgets.QHBoxLayout() #create horizontal layout
        h2_layout.addWidget(self.remove_used_btn)
        h2_layout.addWidget(self.remove_unshared_btn) 

        self.group_box2.setLayout(h2_layout) #set layout for group box
        self.layout.addWidget(self.group_box2) #add goupbox to the main layout
        self.setLayout(self.layout)

        self.export_csv_btn = QtWidgets.QPushButton("Export to CSV", self)
        self.export_csv_btn.setFixedSize(150, 40)  # Width: 150px, Height: 40px
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        self.layout.addWidget(self.export_csv_btn)




      
      # Create refresh and help buttons layout
        self.refresh_help_layout = QtWidgets.QHBoxLayout()
        
        # Refresh button
        self.refresh_btn = QtWidgets.QPushButton(self)
        self.refresh_btn.setIcon(QIcon("refresh.png"))
        self.refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: none;
                color: black;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color:shadow ;
               
            }
            QPushButton:pressed {
                background-color: #ffcc66;
            }
        """
        )
        self.refresh_btn.setFixedSize(40, 40)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.refresh_help_layout.addWidget(self.refresh_btn)
        
        # Help button
        self.help_btn = QtWidgets.QPushButton("Help", self)
        self.help_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f0f0f0;
                color: black;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """
        )
        self.help_btn.setFixedSize(60, 40)
        self.help_btn.clicked.connect(self.show_help_dialog)
        self.refresh_help_layout.addStretch()  # This will push the help button to the right
        self.refresh_help_layout.addWidget(self.help_btn)
        
        # Add the refresh-help layout to main layout
        self.layout.addLayout(self.refresh_help_layout)

       

    # ... (keep all your existing methods including the new show_help_dialog and send_new_password methods)




        # Statistics Display
        self.stats_label = QtWidgets.QLabel("Statistics: Valid - 0 | Used - 0 | Expired - 0")
        self.stats_label.setFont(QtGui.QFont("Arial", 12))
        self.layout.addWidget(self.stats_label)
        
        # Coupon List Table
        self.coupon_list = QtWidgets.QTableWidget()
        self.coupon_list.setColumnCount(6)
        self.coupon_list.setHorizontalHeaderLabels(["Code", "Status", "Created At", "Expiry Date", "Shared","Type"])
        self.coupon_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.coupon_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.coupon_list.setColumnWidth(0, 150)
        self.coupon_list.setColumnWidth(1, 100)
        self.coupon_list.setColumnWidth(2, 200)
        self.coupon_list.setColumnWidth(3, 200)
        self.coupon_list.setColumnWidth(4, 100)
        self.coupon_list.setColumnWidth(5, 100)
        self.layout.addWidget(self.coupon_list)
        
        self.setLayout(self.layout)
        self.update_coupon_list()
        self.update_statistics()

    def show_help_dialog(self):
        """Show the help dialog with option to get new generation password"""
        self.help_dialog = QtWidgets.QDialog(self)  # Store as instance variable
        self.help_dialog.setWindowTitle("Help")
        self.help_dialog.setModal(True)
        
        layout = QtWidgets.QVBoxLayout()
        
        # Message label
        message = QtWidgets.QLabel("The Generation password has expired.To GET new password\n👇👇👇")
        layout.addWidget(message)
        
        # Get New Pass button
        get_pass_btn = QtWidgets.QPushButton("Get New Generation Password")
        get_pass_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
            """
        )
        get_pass_btn.clicked.connect(self.send_new_password)  # Remove lambda
        layout.addWidget(get_pass_btn)
        
        self.help_dialog.setLayout(layout)
        self.help_dialog.exec_()

    def send_new_password(self):
        """Send the latest generation password via WhatsApp"""
        try:
            # Read the button_logs.csv file
            log_file = resource_path("button_logs.csv")
            if not os.path.exists(log_file):
                QtWidgets.QMessageBox.warning(self, "Error", "CONTACT OWNER!!!")
                return
            
            # Find the latest "Generate" entry
            latest_entry = None
            with open(log_file, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if "Generate" in row[0]:  # Look for generate entries
                        latest_entry = row
            
            if not latest_entry:
                QtWidgets.QMessageBox.warning(self, "Error", "the password is not changed")
                return
            
            
            # Create WhatsApp message
            message = f"New Generation Password Request\n\nLatest generation timestamp: {latest_entry[1]}"
            encoded_message = message.replace(" ", "%20").replace("\n", "%0A")
            url = f"https://api.whatsapp.com/send?phone=919014190770&text={encoded_message}"
            
            # Open WhatsApp
            webbrowser.open(url)
            
            QtWidgets.QMessageBox.information(self, "NOTICE SENT", "the new password will be sent shortly.")
            
            # Close the help dialog after successful operation
            if hasattr(self, 'help_dialog') and self.help_dialog:
                self.help_dialog.close()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to send password: {str(e)}")
    
    def get_expiry_days(self):
        """Prompt the user to enter the number of days until the coupon expires."""
        days, ok = QtWidgets.QInputDialog.getInt(self, "Set Expiry", "Enter the number of days until the coupon expires:", 30, 1, 365)
        if ok:
            return days
        return None
    
    def generate_coupon(self):
        global GENERATION_PASSWORD
        
        if not self.authenticate(GENERATION_PASSWORD, "Generate Coupon Authentication"):
            QtWidgets.QMessageBox.warning(self, "Access Denied", "Incorrect password!")
            return

        # Ask for the number of coupons to generate
        num_coupons, ok = QtWidgets.QInputDialog.getInt(self, "Number of Coupons", "Enter the number of coupons to generate:", min=1, max=100, value=100)
        if not ok or num_coupons < 1:
            return  # User canceled or entered an invalid number

        # Ask for coupon type
        coupon_types = ["Regular", "Premium", "VIP"]
        coupon_type, ok = QtWidgets.QInputDialog.getItem(
            self, 
            "Coupon Type", 
            "Select the type of coupon:", 
            coupon_types, 
            0,  # Default to first item
            False  # Not editable
        )
        if not ok:
            return  # User canceled the input

        # Ask for expiry days
        expiry_days = self.get_expiry_days()
        if expiry_days is None:
            return  # User canceled the input
            
        generated_coupons = []
        
        for _ in range(num_coupons):
            coupon_code = str(uuid.uuid4())[:8].upper()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime("%Y-%m-%d %H:%M:%S")
            coupons[coupon_code] = {
                "status": "Valid", 
                "timestamp": timestamp, 
                "expiry": expiry_date, 
                "shared": False,
                "type": coupon_type  # Add coupon type to the data
            }
            generated_coupons.append(coupon_code)

        save_coupons(coupons)
        self.update_coupon_list()
        self.update_statistics()
        
        # Ask to share the generated coupons
        self.ask_to_share(generated_coupons)

        #new passkey
        new_pass = generate_new_password()
        log_button_press("Generate Coupon")
        if not update_env_file(new_pass):
            QtWidgets.QMessageBox.warning(self,"error","Failed to update the generation password")
            return
        
        GENERATION_PASSWORD = new_pass
       

    def generate_100_coupons(self):
        global GENERATION_PASSWORD
        
        if not self.authenticate(GENERATION_PASSWORD, "Generate 100 Coupons Authentication"):
            QtWidgets.QMessageBox.warning(self, "Access Denied", "Incorrect password!")
            return
        
        # Ask for coupon type
        coupon_types = ["Regular", "Premium", "VIP"]
        coupon_type, ok = QtWidgets.QInputDialog.getItem(
            self, 
            "Coupon Type", 
            "Select the type of coupon:", 
            coupon_types, 
            0,  # Default to first item
            False  # Not editable
        )
        if not ok:
            return  # User canceled the input
        
        expiry_days = self.get_expiry_days()
        if expiry_days is None:
            return  # User canceled the input
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime("%Y-%m-%d %H:%M:%S")
        new_coupons = []
        for _ in range(100):
            coupon_code = str(uuid.uuid4())[:8].upper()
            coupons[coupon_code] = {
                "status": "Valid", 
                "timestamp": timestamp, 
                "expiry": expiry_date, 
                "shared": False,
                "type": coupon_type  # Add coupon type to the data
            }
            new_coupons.append(coupon_code)
        save_coupons(coupons)
        self.update_coupon_list()
        self.update_statistics()

        self.ask_to_share(new_coupons)

        #new passkey
        new_pass = generate_new_password()
        log_button_press("Generate 100 Coupons")
        if not update_env_file(new_pass):
            QtWidgets.QMessageBox.warning(self,"Error","Failed to update genaration password")

        
        GENERATION_PASSWORD = new_pass
        







    def filter_coupons(self):
        search_text = self.search_entry.text().strip().lower()
        for row in range(self.coupon_list.rowCount()):
            match = False
            for col in range(self.coupon_list.columnCount()):
                item = self.coupon_list.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.coupon_list.setRowHidden(row, not match)
    
    def ask_to_share(self, coupon_codes):
        """Ask the user if they want to share the generated coupons."""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Share Coupons",
            "Do you want to share the generated coupons via WhatsApp?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.share_coupons(coupon_codes)
    
    def share_coupons(self, coupon_codes):
        """Share the coupons via WhatsApp with their expiry dates."""
        message = "Hey! You know there's a restaurant near you with great food.\nHurry up! These coupons are valid only until their expiry dates.\n\n"
        
        # Create formatted coupon list with expiry dates
        coupon_list = []
        for code in coupon_codes:
            if code in coupons:
                expiry_date = datetime.strptime(coupons[code]["expiry"], "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y")
                coupon_list.append(f"{code} (Valid until: {expiry_date})")
        
        coupon_text = "\n".join(coupon_list)
        full_text = message + coupon_text
        full_text = full_text.replace(" ", "%20").replace("\n", "%0A")
        url = f"https://api.whatsapp.com/send?text={full_text}"
        webbrowser.open(url)
        
        # Mark coupons as shared
        for code in coupon_codes:
            if code in coupons:
                coupons[code]["shared"] = True
        save_coupons(coupons)
        self.update_coupon_list()
        
    def validate_coupon(self):
        code = self.coupon_entry.text().strip().upper()
        if code in coupons:
            if coupons[code]["status"] == "Valid":
                if datetime.now() <= datetime.strptime(coupons[code]["expiry"], "%Y-%m-%d %H:%M:%S"):
                    # Ask for customer details
                    customer_dialog = QtWidgets.QDialog(self)
                    customer_dialog.setWindowTitle("Customer Details")
                    customer_dialog.setModal(True)
                    
                    layout = QtWidgets.QVBoxLayout()
                    
                    # Name field
                    name_label = QtWidgets.QLabel("Customer Name:")
                    name_input = QtWidgets.QLineEdit()
                    layout.addWidget(name_label)
                    layout.addWidget(name_input)
                    
                    # Phone field
                    phone_label = QtWidgets.QLabel("Phone Number:")
                    phone_input = QtWidgets.QLineEdit()
                    layout.addWidget(phone_label)
                    layout.addWidget(phone_input)
                    
                    # Buttons
                    button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
                    button_box.accepted.connect(customer_dialog.accept)
                    button_box.rejected.connect(customer_dialog.reject)
                    layout.addWidget(button_box)
                    
                    customer_dialog.setLayout(layout)
                    
                    if customer_dialog.exec_() == QtWidgets.QDialog.Accepted:
                        customer_name = name_input.text().strip()
                        phone_number = phone_input.text().strip()
                        
                        if customer_name and phone_number:
                            # Save customer details
                            if save_customer_details(code, customer_name, phone_number):
                                coupons[code]["status"] = "Used"
                                save_coupons(coupons)
                                self.update_coupon_list()
                                self.update_statistics()
                                QtWidgets.QMessageBox.information(
                                    self, 
                                    "Success", 
                                    f"Coupon validated successfully!\nCustomer: {customer_name}\nPhone: {phone_number}"
                                )
                            else:
                                QtWidgets.QMessageBox.warning(self, "Error", "Failed to save customer details.")
                        else:
                            QtWidgets.QMessageBox.warning(self, "Error", "Please enter both name and phone number.")
                            return
                else:
                    coupons[code]["status"] = "Expired"
                    save_coupons(coupons)
                    self.update_coupon_list()
                    self.update_statistics()
                    QtWidgets.QMessageBox.warning(self, "Error", "Coupon has expired!")
            elif coupons[code]["status"] == "Used":
                QtWidgets.QMessageBox.warning(self, "Error", "Coupon is already used!")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Coupon has expired!")
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Invalid coupon code!")

    def remove_used_coupons(self):
        # Show confirmation dialog
        reply = QtWidgets.QMessageBox.question(
            self, 
            "Confirm Deletion", 
            "Want to remove all used and expired coupons?", 
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
            QtWidgets.QMessageBox.No
        )

        # Proceed only if the user clicks "Yes"
        if reply == QtWidgets.QMessageBox.Yes:
            global coupons
            coupons = {code: data for code, data in coupons.items() if data["status"] not in ["Used", "Expired"]}
            save_coupons(coupons)
            self.update_coupon_list()
            self.update_statistics()

            QtWidgets.QMessageBox.information(self, "Cleanup", "All used and expired coupons have been removed.")

    def remove_unshared_coupons(self):
        selected_coupons = []
        for item in self.coupon_list.selectedItems():
            if item.column() == 0:  # Only add the coupon code (first column)
              selected_coupons.append(item.text())
    
        if not selected_coupons:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select coupons to remove.")
            return
    
        global coupons
       
        for code in selected_coupons:
            if code in coupons and not coupons[code]["shared"]:
              del coupons[code]
    
        save_coupons(coupons)
        self.update_coupon_list()
        self.update_statistics()
        QtWidgets.QMessageBox.information(self, "Cleanup", "Selected unshared coupons have been removed.")
    
    def export_to_csv(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")

        if filename:
            try:
                # Ensure the file has the correct extension
                if not filename.endswith(".csv"):
                    filename += ".csv"

                # Update all coupons' shared status to True
                global coupons
                for code in coupons:
                    coupons[code]["shared"] = True  # Mark as shared

                # Save the updated coupons
                save_coupons(coupons)

                with open(filename, "w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

                    # Write CSV Header
                    writer.writerow(["Code", "Status", "Created At", "Expiry Date", "Shared"])

                    # Write Coupon Data
                    for code, data in coupons.items():
                        writer.writerow([
                            code, 
                            data.get("status", "N/A"), 
                            data.get("timestamp", "N/A"), 
                            data.get("expiry", "N/A"), 
                            "Yes"  # Ensure "Shared" is marked as Yes
                        ])

                QtWidgets.QMessageBox.information(self, "Export Successful", f"Coupons exported successfully to:\n{filename}")

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Export Failed", f"An error occurred: {str(e)}")

    def refresh_data(self):
        self.update_coupon_list()
        self.update_statistics()
           
    def share_selected_coupons(self):
        selected_coupons = []
        for item in self.coupon_list.selectedItems():
            if item.column() == 0:  # Only add the coupon code (first column)
                selected_coupons.append(item.text())
        if selected_coupons:
            self.share_coupons(selected_coupons)
        else:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select coupons to share.")
    
    def filter_coupons(self):
        search_text = self.search_entry.text().strip().lower()
        for row in range(self.coupon_list.rowCount()):
            match = False
            for col in range(self.coupon_list.columnCount()):
                item = self.coupon_list.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.coupon_list.setRowHidden(row, not match)
    
    def autocheck_expiry(self,code):
        if coupons[code]["status"] == "Valid":
                if datetime.now() <= datetime.strptime(coupons[code]["expiry"], "%Y-%m-%d %H:%M:%S"):
                    coupons[code]["status"] = "Used"
                    save_coupons(coupons)
                    self.update_coupon_list()
                    self.update_statistics()
                      # Recursively check for other valid coupons after one has been used or expired
                elif datetime.now() >= datetime.strptime(coupons[code]["expiry"], "%Y-%m-%d %H:%M:%S"):
                    coupons[code]["status"] = "Expired"
                    save_coupons(coupons)
                    self.update_coupon_list()
                    self.update_statistics()
                      # Recursively check for other valid coupons after one has been used or expired
                   

    def update_coupon_list(self):
        self.coupon_list.setRowCount(len(coupons))
        for row, (code, data) in enumerate(coupons.items()):
            self.coupon_list.setItem(row, 0, QtWidgets.QTableWidgetItem(code))
            self.coupon_list.setItem(row, 1, QtWidgets.QTableWidgetItem(data["status"]))
            self.coupon_list.setItem(row, 2, QtWidgets.QTableWidgetItem(data["timestamp"]))
            self.coupon_list.setItem(row, 3, QtWidgets.QTableWidgetItem(data["expiry"]))
            self.coupon_list.setItem(row, 4, QtWidgets.QTableWidgetItem("Yes" if data["shared"] else "No"))
            self.coupon_list.setItem(row,5,QtWidgets.QTableWidgetItem(data.get("type","regular")))

            # Set row color based on status and expiry
            if data["status"] == "Used":
                self.color_row(row, QtGui.QColor(144, 238, 144))  # Light green for used coupons
            elif datetime.now() > datetime.strptime(data["expiry"], "%Y-%m-%d %H:%M:%S") :
                self.color_row(row, QtGui.QColor(255, 182, 193))  # Light red for expired coupons
                self.autocheck_expiry(code)
                
            else:
                self.color_row(row, QtGui.QColor(255, 255, 153))  # Light yellow for valid coupons
    
    def color_row(self, row, color):
        """Color the entire row with the specified color."""
        for col in range(self.coupon_list.columnCount()):
            item = self.coupon_list.item(row, col)
            if item:
                item.setBackground(color)
    
    def update_statistics(self):
        valid = sum(1 for data in coupons.values() if datetime.now() <= datetime.strptime(data["expiry"], "%Y-%m-%d %H:%M:%S") and data["status"]=="Valid")
        used = sum(1 for data in coupons.values() if data["status"] == "Used")
        expired = sum(1 for data in coupons.values() if datetime.now() > datetime.strptime(data["expiry"], "%Y-%m-%d %H:%M:%S"))
        self.stats_label.setText(f"Statistics: Valid - {valid} | Used - {used} | Expired - {expired}")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = CouponManager()
    window.show()
    app.exec_()