"""
Interactive Setup Script for Trading Bot
Run this once to configure your MT5 credentials
"""

import os

def setup():
    print("=" * 50)
    print("   TRADING BOT - INITIAL SETUP")
    print("=" * 50)
    print()
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  Configuration file (.env) already exists!")
        overwrite = input("Do you want to reconfigure? (yes/no): ").strip().lower()
        if overwrite not in ['yes', 'y']:
            print("Setup cancelled. Using existing configuration.")
            return
        print()
    
    # Account Type Selection
    print("SELECT ACCOUNT TYPE:")
    print("1. Exness REAL Account")
    print("2. Exness TRIAL Account")
    print()
    
    while True:
        account_type = input("Enter your choice (1 or 2): ").strip()
        if account_type == '1':
            server = "Exness-MT5Real"
            print("✓ Selected: REAL Account")
            break
        elif account_type == '2':
            server = "Exness-MT5Trial"
            print("✓ Selected: TRIAL Account")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")
    
    print()
    
    # Get MT5 Login
    while True:
        login = input("Enter your MT5 Login Number: ").strip()
        if login.isdigit():
            break
        else:
            print("Invalid login. Please enter numbers only.")
    
    # Get MT5 Password
    password = input("Enter your MT5 Password: ").strip()
    
    # Confirmation
    print()
    print("=" * 50)
    print("CONFIGURATION SUMMARY:")
    print(f"  Account Type: {'REAL' if account_type == '1' else 'TRIAL'}")
    print(f"  Server: {server}")
    print(f"  Login: {login}")
    print(f"  Password: {'*' * len(password)}")
    print("=" * 50)
    print()
    
    confirm = input("Save this configuration? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Setup cancelled.")
        return
    
    # Write to .env
    with open('.env', 'w') as f:
        f.write(f"MT5_LOGIN={login}\n")
        f.write(f"MT5_PASSWORD={password}\n")
        f.write(f"MT5_SERVER={server}\n")
    
    print()
    print("✅ Configuration saved successfully!")
    print()
    print("You can now run the bot with: python main.py")
    print()
    print("To change your account type later, run: python setup.py")
    print()

if __name__ == "__main__":
    setup()
