#!/usr/bin/env python
"""
Setup script for MeshTradeBot - Initializes database, generates encryption key,
and performs first-time setup checks.

Usage:
    python setup.py
"""

import os
import sys
from pathlib import Path
from getpass import getpass

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from cryptography.fernet import Fernet
from database import init_db


def generate_encryption_key():
    """Generate a new Fernet encryption key"""
    key = Fernet.generate_key().decode()
    return key


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def check_env_file():
    """Check and guide user through .env setup"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print("\n✓ .env file already exists")
        return True
    
    if not env_example_path.exists():
        print("\n❌ .env.example not found")
        return False
    
    print("\n📝 Creating .env file from template...")
    with open(env_example_path) as f:
        content = f.read()
    
    with open(env_path, 'w') as f:
        f.write(content)
    
    print("✓ .env created. Please edit with your actual values:")
    return True


def setup_encryption_key():
    """Setup encryption key for API key storage"""
    print_section("Encryption Key Setup")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    # Read current .env
    with open(env_path) as f:
        lines = f.readlines()
    
    # Check if already configured
    has_encryption_key = any("ENCRYPTION_KEY=" in line and not line.strip().startswith("#") 
                              for line in lines)
    
    if has_encryption_key:
        print("✓ ENCRYPTION_KEY already configured in .env")
        key = [line.split("=")[1].strip() for line in lines 
               if "ENCRYPTION_KEY=" in line and not line.strip().startswith("#")][0]
        if key and key != "your_encryption_key_here":
            return True
    
    print("\nGenerating new encryption key for API key storage...")
    new_key = generate_encryption_key()
    
    print(f"\n🔑 New Encryption Key Generated:")
    print(f"   {new_key}")
    print("\n✓ This key is already saved to .env")
    
    # Update .env
    new_lines = []
    found = False
    for line in lines:
        if "ENCRYPTION_KEY=" in line and not line.strip().startswith("#"):
            new_lines.append(f"ENCRYPTION_KEY={new_key}\n")
            found = True
        else:
            new_lines.append(line)
    
    if not found:
        # Add if not found
        new_lines.append(f"ENCRYPTION_KEY={new_key}\n")
    
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    return True


def setup_database():
    """Initialize database"""
    print_section("Database Setup")
    
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    print("📊 Initializing SQLite database...")
    try:
        init_db()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def check_dependencies():
    """Check if all required packages are installed"""
    print_section("Dependency Check")
    
    required_packages = [
        'aiogram',
        'sqlalchemy',
        'cryptography',
        'freqtrade',
        'ccxt',
        'pandas',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} (MISSING)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def create_directories():
    """Create necessary directories"""
    print_section("Directory Setup")
    
    directories = [
        "data",
        "logs",
        "freqtrade_config",
        "strategies",
        "config",
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ {directory}/")
    
    return True


def print_next_steps():
    """Print setup completion message"""
    print_section("Setup Complete! 🎉")
    
    print("""
📋 Next Steps:

1. ✅ Edit .env file with your actual values:
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_PROVIDER_TOKEN  
   - FREQTRADE_JWT_SECRET
   
   Run: nano .env

2. 📊 Verify Freqtrade config:
   - freqtrade_config/default.json
   - Set your exchange (binance, bybit, okx)
   - Set stake_currency and pairs

3. 🚀 Start the bot:
   
   Option A - Docker (Recommended):
   $ docker-compose up -d
   $ docker-compose logs -f meshtradebot
   
   Option B - Local:
   $ python main.py

4. 📱 Test your bot:
   - Open Telegram and message your bot
   - Send /start
   - Click buttons to test

5. 🔒 Security checklist:
   ☐ Never commit .env to git
   ☐ Encryption key is secure
   ☐ Exchange API keys are encrypted
   ☐ Freqtrade dry_run = true (for testing)
   ☐ Telegram bot token kept secret

📚 Documentation:
   - README.md - Full setup guide
   - Database models in database/models.py
   - Strategy in strategies/ema200_rsi_strategy.py

⚠️  Remember:
   🔴 Trading involves serious risk of loss
   🔴 Start with small amounts
   🔴 Use dry-run mode first
   🔴 Never share your API keys

Need help? Check the README or logs in ./logs/

Happy trading! 🚀
    """)


def main():
    """Run setup"""
    print("\n")
    print("╔════════════════════════════════════════════════════════╗")
    print("║       🤖 MeshTradeBot - Initial Setup                 ║")
    print("║   Production-Ready Telegram Trading Bot               ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    # Run setup steps
    steps = [
        ("Checking directories", create_directories),
        ("Checking .env file", check_env_file),
        ("Checking dependencies", check_dependencies),
        ("Setting up encryption", setup_encryption_key),
        ("Initializing database", setup_database),
    ]
    
    failed = False
    for step_name, step_func in steps:
        print(f"\n⏳ {step_name}...")
        if not step_func():
            print(f"❌ {step_name} - FAILED")
            failed = True
        else:
            print(f"✓ {step_name} - OK")
    
    if failed:
        print("\n⚠️  Setup completed with errors. Please fix the issues above.")
        return 1
    
    print_next_steps()
    return 0


if __name__ == "__main__":
    sys.exit(main())
