#!/usr/bin/env python3
"""
Template Safety Enhancer - Mahima Medicare
==========================================
Adds comprehensive error handling and safety conditions to all templates.
"""

import os
import re
from datetime import datetime

class TemplateSafetyEnhancer:
    def __init__(self):
        self.templates_dir = "templates"
        self.fixes_applied = []
        self.issues_found = []
        
    def log_fix(self, template_path, fix_description):
        self.fixes_applied.append({
            'file': template_path,
            'fix': fix_description,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        print(f"🔧 {template_path}: {fix_description}")
    
    def log_issue(self, template_path, issue_description):
        self.issues_found.append({
            'file': template_path,
            'issue': issue_description,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        print(f"⚠️ {template_path}: {issue_description}")
    
    def add_safety_conditions(self, template_path):
        """Add comprehensive safety conditions to a template"""
        if not os.path.exists(template_path):
            return False
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            fixes_in_file = 0
            
            # Safety Pattern 1: Protect user.patient access
            if 'user.patient' in content and '{% if user.patient %}' not in content:
                content = re.sub(
                    r'(user\.patient\.[\w.]+)',
                    r'{% if user.patient %}{{ \1 }}{% else %}N/A{% endif %}',
                    content
                )
                fixes_in_file += 1
            
            # Safety Pattern 2: Protect user.profile access (doctor)
            if 'user.profile' in content and '{% if user.profile %}' not in content:
                content = re.sub(
                    r'(user\.profile\.[\w.]+)',
                    r'{% if user.profile %}{{ \1 }}{% else %}N/A{% endif %}',
                    content
                )
                fixes_in_file += 1
            
            # Safety Pattern 3: Protect object.field access with existence check
            patterns_to_protect = [
                (r'patient\.[\w.]+', 'patient'),
                (r'doctor\.[\w.]+', 'doctor'),
                (r'medicine\.[\w.]+', 'medicine'),
                (r'invoice\.[\w.]+', 'invoice'),
                (r'order\.[\w.]+', 'order'),
                (r'payment\.[\w.]+', 'payment')
            ]
            
            for pattern, obj_name in patterns_to_protect:
                if obj_name in content:
                    # Check if already protected
                    if f'{{% if {obj_name} %}}' not in content:
                        # Add basic protection for unprotected object access
                        content = re.sub(
                            f'{{{{\\s*({pattern})\\s*}}}}',
                            f'{{{% if {obj_name} %}}}}{{{{ \\1 }}}}{{{% endif %}}',
                            content
                        )
                        if pattern in content:
                            fixes_in_file += 1
            
            # Safety Pattern 4: Add default values for empty fields
            content = re.sub(
                r'{{[\s]*([^}]+)[\s]*}}',
                lambda m: '{{ ' + m.group(1).strip() + '|default:"N/A" }}',
                content
            )
            
            # Safety Pattern 5: Protect image fields
            if '.featured_image' in content:
                content = re.sub(
                    r'{{[\s]*([^}]+\.featured_image\.url)[\s]*}}',
                    r'{% if \1 %}{{ \1 }}{% else %}{% static "images/default.png" %}{% endif %}',
                    content
                )
                fixes_in_file += 1
            
            # Only write if changes were made
            if content != original_content and fixes_in_file > 0:
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log_fix(template_path, f"Added {fixes_in_file} safety conditions")
                return True
            
        except Exception as e:
            self.log_issue(template_path, f"Error processing: {str(e)}")
            return False
        
        return False
    
    def enhance_specific_templates(self):
        """Apply specific enhancements to critical templates"""
        print("\n🛡️ APPLYING TEMPLATE SAFETY ENHANCEMENTS")
        print("=" * 45)
        
        critical_templates = [
            "templates/patient-sidebar.html",
            "templates/doctor-sidebar.html", 
            "templates/razorpay_payment/invoice_detail.html",
            "templates/hospital_admin/invoice.html",
            "templates/doctor-test-list.html"
        ]
        
        for template in critical_templates:
            if os.path.exists(template):
                self.add_safety_conditions(template)
            else:
                self.log_issue(template, "Template file not found")
    
    def scan_all_templates(self):
        """Scan all template files for potential issues"""
        print("\n🔍 SCANNING ALL TEMPLATES")
        print("=" * 30)
        
        for root, dirs, files in os.walk(self.templates_dir):
            for file in files:
                if file.endswith('.html'):
                    template_path = os.path.join(root, file)
                    self.scan_template_for_issues(template_path)
    
    def scan_template_for_issues(self, template_path):
        """Scan individual template for potential issues"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for unprotected object access
            risky_patterns = [
                (r'{{[^}]*user\.patient\.[^}]*}}', "Unprotected user.patient access"),
                (r'{{[^}]*user\.profile\.[^}]*}}', "Unprotected user.profile access"),
                (r'{{[^}]*\.url[^}]*}}', "Unprotected URL field access"),
                (r'for[\s]+[\w]+[\s]+in[\s]+[\w]+[\s]*%}', "Loop without empty check")
            ]
            
            for pattern, description in risky_patterns:
                if re.search(pattern, content):
                    # Check if it's already protected
                    if "{% if " not in content or "{% empty %}" not in content:
                        self.log_issue(template_path, description)
                        
        except Exception as e:
            self.log_issue(template_path, f"Scan error: {str(e)}")
    
    def create_enhanced_base_template(self):
        """Create enhanced base template with comprehensive error handling"""
        base_template_content = '''{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Mahima Medicare - ଆପଣଙ୍କ ସ୍ବାସ୍ଥ୍ୟ ର ସାଥୀ{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <style>
        :root {
            --primary-color: #95C270;
            --text-color: #2c3e50;
            --bg-color: #fff;
        }
        
        .error-boundary {
            padding: 1rem;
            background: #f8f9fa;
            border-left: 4px solid #dc3545;
            margin: 1rem 0;
        }
        
        .loading-placeholder {
            background: #f8f9fa;
            border-radius: 4px;
            padding: 1rem;
            text-align: center;
            color: #6c757d;
        }
    </style>
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Error Boundary for JavaScript errors -->
    <div id="error-boundary" class="error-boundary d-none">
        <h5>Something went wrong</h5>
        <p>Please refresh the page or contact support if the issue persists.</p>
    </div>
    
    <!-- Main Content -->
    <div id="main-content">
        {% block content %}
        <div class="loading-placeholder">
            <p>Loading...</p>
        </div>
        {% endblock %}
    </div>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Error Handling JavaScript -->
    <script>
        // Global error handler
        window.addEventListener('error', function(e) {
            console.error('Error:', e.error);
            document.getElementById('error-boundary').classList.remove('d-none');
        });
        
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', function(e) {
            console.error('Unhandled promise rejection:', e.reason);
            document.getElementById('error-boundary').classList.remove('d-none');
        });
        
        // Safe image loading
        document.addEventListener('DOMContentLoaded', function() {
            const images = document.querySelectorAll('img');
            images.forEach(img => {
                img.addEventListener('error', function() {
                    this.src = '{% static "images/default.png" %}';
                });
            });
        });
    </script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>'''
        
        base_template_path = "templates/base_enhanced.html"
        try:
            with open(base_template_path, 'w', encoding='utf-8') as f:
                f.write(base_template_content)
            self.log_fix(base_template_path, "Created enhanced base template with error handling")
            return True
        except Exception as e:
            self.log_issue(base_template_path, f"Failed to create: {str(e)}")
            return False
    
    def generate_report(self):
        """Generate comprehensive report of all fixes and issues"""
        print("\n" + "=" * 60)
        print("📊 TEMPLATE SAFETY ENHANCEMENT REPORT")
        print("=" * 60)
        
        print(f"🔧 FIXES APPLIED: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            print(f"   ✅ {fix['file']}: {fix['fix']}")
        
        print(f"\n⚠️ ISSUES FOUND: {len(self.issues_found)}")
        for issue in self.issues_found:
            print(f"   ⚠️ {issue['file']}: {issue['issue']}")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'fixes_applied': len(self.fixes_applied),
                'issues_found': len(self.issues_found)
            },
            'fixes': self.fixes_applied,
            'issues': self.issues_found
        }
        
        import json
        with open('template_safety_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Report saved to: template_safety_report.json")
        return report_data
    
    def run_enhancement(self):
        """Run complete template safety enhancement"""
        print("🚀 STARTING TEMPLATE SAFETY ENHANCEMENT")
        print("🏥 MAHIMA MEDICARE - ଆପଣଙ୍କ ସ୍ବାସ୍ଥ୍ୟ ର ସାଥୀ")
        print("=" * 60)
        
        # Apply specific enhancements
        self.enhance_specific_templates()
        
        # Scan all templates
        self.scan_all_templates()
        
        # Create enhanced base template
        self.create_enhanced_base_template()
        
        # Generate report
        report = self.generate_report()
        
        print(f"\n🎯 TEMPLATE ENHANCEMENT COMPLETE!")
        return report

if __name__ == "__main__":
    enhancer = TemplateSafetyEnhancer()
    enhancer.run_enhancement()