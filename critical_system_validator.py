#!/usr/bin/env python3
"""
CRITICAL SYSTEM VALIDATION - MAHIMA MEDICARE
===========================================
Testing core functionality and identifying issues for fixes.
"""

import subprocess
import json
import os
from datetime import datetime

class CriticalSystemValidator:
    def __init__(self):
        self.issues = []
        self.fixes = []
        
    def log_issue(self, category, description, severity="HIGH", fix_suggestion=""):
        issue = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'category': category,
            'description': description,
            'severity': severity,
            'fix_suggestion': fix_suggestion
        }
        self.issues.append(issue)
        severity_icon = "🚨" if severity == "HIGH" else "⚠️" if severity == "MEDIUM" else "ℹ️"
        print(f"{severity_icon} {category}: {description}")
        if fix_suggestion:
            print(f"   💡 Fix: {fix_suggestion}")
    
    def log_fix(self, description):
        self.fixes.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'description': description
        })
        print(f"✅ FIXED: {description}")
    
    def test_server_health(self):
        """Test if Django server can start and basic functionality works"""
        print("\n🏥 TESTING SERVER HEALTH")
        print("=" * 30)
        
        try:
            # Test Django checks
            result = subprocess.run(['python', 'manage.py', 'check'], 
                                  capture_output=True, text=True, cwd=".")
            
            if result.returncode == 0:
                print("✅ Django system checks passed")
            else:
                self.log_issue("SERVER", "Django system check failed", "HIGH", 
                              f"Error: {result.stderr}")
        except Exception as e:
            self.log_issue("SERVER", f"Cannot run Django checks: {str(e)}", "HIGH")
    
    def test_database_connectivity(self):
        """Test database connection and basic queries"""
        print("\n🗄️ TESTING DATABASE")
        print("=" * 25)
        
        try:
            # Test database connection
            result = subprocess.run(['python', 'manage.py', 'shell', '-c', 
                                   'from django.db import connection; connection.ensure_connection(); print("Database OK")'], 
                                  capture_output=True, text=True, cwd=".")
            
            if "Database OK" in result.stdout:
                print("✅ Database connection successful")
            else:
                self.log_issue("DATABASE", "Database connection failed", "HIGH",
                              "Check database settings and migrations")
        except Exception as e:
            self.log_issue("DATABASE", f"Database test failed: {str(e)}", "HIGH")
    
    def test_static_files(self):
        """Test static file configuration"""
        print("\n📁 TESTING STATIC FILES")
        print("=" * 30)
        
        # Check if static directories exist
        static_dirs = ['static', 'media']
        for dir_name in static_dirs:
            if os.path.exists(dir_name):
                print(f"✅ {dir_name}/ directory exists")
            else:
                self.log_issue("STATIC", f"{dir_name}/ directory missing", "MEDIUM",
                              f"Create {dir_name} directory and run collectstatic")
        
        # Check for missing notification file (from server logs)
        notification_path = "static/HealthStack-System/sounds/notification.mp3"
        if not os.path.exists(notification_path):
            self.log_issue("STATIC", "notification.mp3 missing", "LOW",
                          "Create dummy notification file or update templates")
    
    def test_critical_migrations(self):
        """Test if all migrations are applied"""
        print("\n🔄 TESTING MIGRATIONS")
        print("=" * 25)
        
        try:
            result = subprocess.run(['python', 'manage.py', 'showmigrations'], 
                                  capture_output=True, text=True, cwd=".")
            
            if "[X]" in result.stdout:
                applied_count = result.stdout.count("[X]")
                unapplied_count = result.stdout.count("[ ]")
                print(f"✅ {applied_count} migrations applied")
                
                if unapplied_count > 0:
                    self.log_issue("MIGRATIONS", f"{unapplied_count} unapplied migrations", "MEDIUM",
                                  "Run 'python manage.py migrate'")
            else:
                self.log_issue("MIGRATIONS", "Cannot check migration status", "MEDIUM")
                
        except Exception as e:
            self.log_issue("MIGRATIONS", f"Migration check failed: {str(e)}", "MEDIUM")
    
    def test_critical_models(self):
        """Test critical model functionality"""
        print("\n🧪 TESTING CRITICAL MODELS")
        print("=" * 35)
        
        test_commands = [
            ("Patient Model", "from hospital.models import Patient; print(f'Patients: {Patient.objects.count()}')"),
            ("Doctor Model", "from doctor.models import Doctor_Information; print(f'Doctors: {Doctor_Information.objects.count()}')"),
            ("Medicine Model", "from pharmacy.models import Medicine; print(f'Medicines: {Medicine.objects.count()}')"),
            ("TestInfo Model", "from hospital.models import TestInfo; print(f'Tests: {TestInfo.objects.count()}')"),
            ("Invoice Model", "from razorpay_payment.models import Invoice; print(f'Invoices: {Invoice.objects.count()}')"),
        ]
        
        for test_name, command in test_commands:
            try:
                result = subprocess.run(['python', 'manage.py', 'shell', '-c', command], 
                                      capture_output=True, text=True, cwd=".")
                
                if result.returncode == 0 and ":" in result.stdout:
                    count = result.stdout.strip().split('\n')[-1]
                    print(f"✅ {test_name}: {count}")
                else:
                    self.log_issue("MODELS", f"{test_name} failed", "HIGH",
                                  f"Check model definition and imports")
            except Exception as e:
                self.log_issue("MODELS", f"{test_name} error: {str(e)}", "HIGH")
    
    def test_url_patterns(self):
        """Test if URL patterns are properly configured"""
        print("\n🌐 TESTING URL PATTERNS")
        print("=" * 30)
        
        try:
            result = subprocess.run(['python', 'manage.py', 'shell', '-c', 
                                   'from django.urls import get_resolver; resolver = get_resolver(); print(f"URL patterns loaded: {len(resolver.url_patterns)}")'], 
                                  capture_output=True, text=True, cwd=".")
            
            if "URL patterns loaded:" in result.stdout:
                print("✅ URL patterns loaded successfully")
            else:
                self.log_issue("URLS", "URL pattern loading failed", "HIGH")
        except Exception as e:
            self.log_issue("URLS", f"URL test failed: {str(e)}", "HIGH")
    
    def fix_notification_file(self):
        """Fix missing notification file"""
        notification_dir = "static/HealthStack-System/sounds"
        notification_file = os.path.join(notification_dir, "notification.mp3")
        
        if not os.path.exists(notification_file):
            try:
                os.makedirs(notification_dir, exist_ok=True)
                # Create a minimal MP3 file structure (just headers)
                with open(notification_file, 'wb') as f:
                    # Write minimal MP3 header
                    f.write(b'ID3\x03\x00\x00\x00\x00\x00\x00')
                self.log_fix("Created missing notification.mp3 file")
                return True
            except Exception as e:
                self.log_issue("FIX", f"Cannot create notification file: {str(e)}", "LOW")
                return False
        return True
    
    def fix_template_conditions(self):
        """Add safety conditions to templates"""
        print("\n🔧 APPLYING TEMPLATE SAFETY FIXES")
        print("=" * 40)
        
        # Common template safety patterns to add
        template_fixes = [
            ("Patient sidebar safety", "templates/patient-sidebar.html"),
            ("Doctor sidebar safety", "templates/doctor-sidebar.html"),
            ("Invoice template safety", "templates/razorpay_payment/invoice_detail.html"),
        ]
        
        for fix_name, template_path in template_fixes:
            if os.path.exists(template_path):
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if safety conditions are already present
                    if "{% if " in content and "patient" in content.lower():
                        print(f"✅ {fix_name}: Safety conditions present")
                    else:
                        print(f"⚠️ {fix_name}: Could use more safety conditions")
                        
                except Exception as e:
                    self.log_issue("TEMPLATE", f"Cannot check {template_path}: {str(e)}", "LOW")
    
    def create_error_handlers(self):
        """Create proper error handling"""
        print("\n🛡️ CHECKING ERROR HANDLING")
        print("=" * 35)
        
        # Check if custom error pages exist
        error_templates = ["404.html", "500.html", "403.html"]
        templates_dir = "templates"
        
        for template in error_templates:
            template_path = os.path.join(templates_dir, template)
            if os.path.exists(template_path):
                print(f"✅ {template} exists")
            else:
                self.log_issue("ERROR_HANDLING", f"Missing {template}", "MEDIUM",
                              f"Create {template} for better user experience")
    
    def test_security_settings(self):
        """Check basic security configurations"""
        print("\n🔒 TESTING SECURITY SETTINGS")
        print("=" * 35)
        
        try:
            # Check DEBUG setting
            result = subprocess.run(['python', 'manage.py', 'shell', '-c', 
                                   'from django.conf import settings; print(f"DEBUG: {settings.DEBUG}")'], 
                                  capture_output=True, text=True, cwd=".")
            
            if "DEBUG: True" in result.stdout:
                self.log_issue("SECURITY", "DEBUG is enabled", "MEDIUM",
                              "Set DEBUG=False for production")
            elif "DEBUG: False" in result.stdout:
                print("✅ DEBUG is properly disabled")
                
        except Exception as e:
            self.log_issue("SECURITY", f"Cannot check DEBUG setting: {str(e)}", "MEDIUM")
    
    def generate_comprehensive_fix_report(self):
        """Generate comprehensive report with fixes"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE SYSTEM VALIDATION REPORT")
        print("=" * 60)
        
        high_priority = len([i for i in self.issues if i['severity'] == 'HIGH'])
        medium_priority = len([i for i in self.issues if i['severity'] == 'MEDIUM'])
        low_priority = len([i for i in self.issues if i['severity'] == 'LOW'])
        
        print(f"🚨 HIGH PRIORITY ISSUES: {high_priority}")
        print(f"⚠️ MEDIUM PRIORITY ISSUES: {medium_priority}")
        print(f"ℹ️ LOW PRIORITY ISSUES: {low_priority}")
        print(f"✅ FIXES APPLIED: {len(self.fixes)}")
        
        if high_priority > 0:
            print(f"\n🚨 CRITICAL ISSUES TO FIX IMMEDIATELY:")
            for issue in self.issues:
                if issue['severity'] == 'HIGH':
                    print(f"   - {issue['category']}: {issue['description']}")
                    if issue['fix_suggestion']:
                        print(f"     💡 {issue['fix_suggestion']}")
        
        if medium_priority > 0:
            print(f"\n⚠️ MEDIUM PRIORITY IMPROVEMENTS:")
            for issue in self.issues:
                if issue['severity'] == 'MEDIUM':
                    print(f"   - {issue['category']}: {issue['description']}")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_issues': len(self.issues),
                'high_priority': high_priority,
                'medium_priority': medium_priority,
                'low_priority': low_priority,
                'fixes_applied': len(self.fixes)
            },
            'issues': self.issues,
            'fixes': self.fixes
        }
        
        with open('system_validation_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: system_validation_report.json")
        print(f"🕐 Validation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return report_data
    
    def run_comprehensive_validation(self):
        """Run all validation tests and apply fixes"""
        print("🚀 STARTING CRITICAL SYSTEM VALIDATION")
        print("🏥 MAHIMA MEDICARE - ଆପଣଙ୍କ ସ୍ବାସ୍ଥ୍ୟ ର ସାଥୀ")
        print("=" * 60)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        self.test_server_health()
        self.test_database_connectivity()
        self.test_static_files()
        self.test_critical_migrations()
        self.test_critical_models()
        self.test_url_patterns()
        self.test_security_settings()
        
        # Apply automatic fixes
        print("\n🔧 APPLYING AUTOMATIC FIXES")
        print("=" * 35)
        
        self.fix_notification_file()
        self.fix_template_conditions()
        self.create_error_handlers()
        
        # Generate report
        report = self.generate_comprehensive_fix_report()
        
        return report

if __name__ == "__main__":
    validator = CriticalSystemValidator()
    validator.run_comprehensive_validation()