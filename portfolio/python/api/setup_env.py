#!/usr/bin/env python3
"""
Environment setup script for Portfolia application.
This script generates a .env file from the config.env.example template.
"""

import os
import shutil
from pathlib import Path


def setup_environment():
    """Set up environment configuration file."""

    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    example_file = script_dir / "config.env.example"
    env_file = script_dir / ".env"

    print("🚀 Setting up environment configuration...")

    # Check if .env already exists
    if env_file.exists():
        print(
            "⚠️  .env file already exists. Do you want to overwrite it? (y/N): ", end=""
        )
        response = input().strip().lower()
        if response not in ["y", "yes"]:
            print("✅ Keeping existing .env file")
            return

    # Check if example file exists
    if not example_file.exists():
        print(f"❌ Example configuration file not found: {example_file}")
        return

    try:
        # Copy the example file to .env
        shutil.copy2(example_file, env_file)
        print(f"✅ Environment file created: {env_file}")

        # Make the file readable only by the owner
        os.chmod(env_file, 0o600)
        print("🔒 Set proper file permissions (600)")

        print("\n📝 Next steps:")
        print("1. Edit the .env file with your actual configuration values")
        print("2. For production, change the SECRET_KEY and JWT_SECRET_KEY")
        print("3. Update database credentials if needed")
        print("4. Set external API keys if you have them")

    except Exception as e:
        print(f"❌ Error creating .env file: {e}")


def validate_environment():
    """Validate that required environment variables are set."""

    print("\n🔍 Validating environment configuration...")

    # Check if .env file exists
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("❌ .env file not found. Run setup_env.py first.")
        return False

    # Try to load the configuration
    try:
        from database.config import db_settings

        # Test database connection
        from database.connection import health_check

        if health_check():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False

        print("✅ Environment configuration is valid")
        return True

    except Exception as e:
        print(f"❌ Environment validation failed: {e}")
        return False


if __name__ == "__main__":
    setup_environment()
    validate_environment()
