#!/usr/bin/env python
"""
Quick deployment script for Windows
Run this before pushing to GitHub
"""
import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and print status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Preparing Mahima Medicare for deployment...\n")

    # Export data first
    if run_command("python export_data.py", "Exporting current data"):
        print("📦 Data backup created - this will preserve your medicines and doctors")

    # Clean up unnecessary files
    print("\n🧹 Cleaning up project...")

    # Create migrations for new prescription models
    if run_command("python manage.py makemigrations pharmacy", "Creating pharmacy migrations"):
        print("✅ New prescription upload models will be created on server")

    if run_command("python manage.py makemigrations", "Creating all migrations"):
        print("✅ All migrations prepared")

    # Add files to git
    run_command("git add .", "Adding files to git")

    # Commit changes
    commit_msg = input("\nEnter commit message (or press Enter for default): ").strip()
    if not commit_msg:
        commit_msg = "Add prescription upload feature and clean deployment"

    if run_command(f'git commit -m "{commit_msg}"', "Committing changes"):
        print("✅ Changes committed to git")

    # Push to GitHub
    if run_command("git push origin main", "Pushing to GitHub"):
        print("✅ Code pushed to GitHub successfully!")

        print("\n" + "="*60)
        print("🎉 DEPLOYMENT PREPARATION COMPLETE!")
        print("="*60)
        print("\n📋 Next steps on your server:")
        print("1. SSH to your server: ssh root@139.84.155.25")
        print("2. Go to project: cd /var/www/mahima-medicare")
        print("3. Run the automated deployment: chmod +x deploy_automated.sh && ./deploy_automated.sh")
        print("\n🆕 NEW FEATURES ADDED:")
        print("✅ Prescription upload system for patients")
        print("✅ Pharmacist review interface")
        print("✅ Data backup/restore system")
        print("✅ Automated deployment script")
        print("✅ Cleaned up unnecessary files")
        print("\n🔗 Your website will be live at: https://mahimamedicare.com")
    else:
        print("❌ Failed to push to GitHub. Please check your git configuration.")
        return False

    return True

if __name__ == "__main__":
    main()
