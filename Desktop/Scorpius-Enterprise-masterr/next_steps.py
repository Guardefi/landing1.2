#!/usr/bin/env python3
"""
Next Steps Script for Scorpius Enterprise
This script helps with post-cleanup tasks and validation.
"""

import os
import glob
import re
from pathlib import Path

def find_python_files(directory="."):
    """Find all Python files in the directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', 'venv', 'env'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def check_import_paths():
    """Check for potentially broken import paths."""
    print("🔍 Checking for potentially broken import paths...")
    
    python_files = find_python_files()
    potential_issues = []
    
    # Patterns that might indicate broken paths
    patterns = [
        r'from\s+(\w+)\s+import',  # from statements
        r'import\s+(\w+)',         # import statements
        r'from\s+\.\.(\w+)',       # relative imports
        r'from\s+\.(\w+)',         # relative imports
    ]
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern in patterns:
                        matches = re.findall(pattern, line)
                        for match in matches:
                            # Check if this might be a file that was moved
                            if any(keyword in match.lower() for keyword in ['test', 'config', 'docker', 'docs']):
                                potential_issues.append({
                                    'file': file_path,
                                    'line': line_num,
                                    'line_content': line.strip(),
                                    'import': match
                                })
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
    
    if potential_issues:
        print(f"\n⚠️  Found {len(potential_issues)} potential import issues:")
        for issue in potential_issues[:10]:  # Show first 10
            print(f"  {issue['file']}:{issue['line']} - {issue['line_content']}")
        if len(potential_issues) > 10:
            print(f"  ... and {len(potential_issues) - 10} more")
    else:
        print("✅ No obvious import issues found")
    
    return potential_issues

def check_configuration_files():
    """Check for configuration files that might need updates."""
    print("\n⚙️  Checking configuration files...")
    
    config_files = [
        'docker-compose.yml',
        'docker-compose.dev.yml',
        'docker-compose.secure.yml',
        'Makefile',
        'pytest.ini',
        '.coveragerc'
    ]
    
    issues = []
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check for hardcoded paths that might need updating
                    if 'test_' in content or 'config/' in content:
                        issues.append(config_file)
            except Exception as e:
                print(f"⚠️  Could not read {config_file}: {e}")
    
    if issues:
        print(f"⚠️  Configuration files that may need updates: {', '.join(issues)}")
    else:
        print("✅ Configuration files look good")
    
    return issues

def check_documentation_links():
    """Check for documentation links that might be broken."""
    print("\n📚 Checking documentation links...")
    
    doc_files = []
    for ext in ['*.md', '*.rst', '*.txt']:
        doc_files.extend(glob.glob(f"**/{ext}", recursive=True))
    
    broken_links = []
    for doc_file in doc_files:
        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for markdown links that might be broken
                links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                for link_text, link_url in links:
                    if link_url.startswith('./') or link_url.startswith('../'):
                        if not os.path.exists(link_url):
                            broken_links.append({
                                'file': doc_file,
                                'link': link_url,
                                'text': link_text
                            })
        except Exception as e:
            print(f"⚠️  Could not read {doc_file}: {e}")
    
    if broken_links:
        print(f"⚠️  Found {len(broken_links)} potentially broken documentation links:")
        for link in broken_links[:5]:  # Show first 5
            print(f"  {link['file']} - {link['text']} -> {link['link']}")
        if len(broken_links) > 5:
            print(f"  ... and {len(broken_links) - 5} more")
    else:
        print("✅ Documentation links look good")
    
    return broken_links

def generate_next_steps_report():
    """Generate a comprehensive next steps report."""
    print("📋 Generating next steps report...")
    
    report = """# Next Steps Report - Scorpius Enterprise

## Summary
This report outlines the next steps needed to complete the enterprise transformation.

## Immediate Actions Required

### 1. Import Path Updates
The following files may need import path updates after the cleanup:

"""
    
    import_issues = check_import_paths()
    if import_issues:
        report += f"- Found {len(import_issues)} potential import issues\n"
        report += "- Review and update import statements in affected files\n"
        report += "- Test imports after making changes\n\n"
    else:
        report += "- No obvious import issues found\n\n"
    
    report += """### 2. Configuration Updates
Update the following configuration files to reflect the new structure:

"""
    
    config_issues = check_configuration_files()
    if config_issues:
        for issue in config_issues:
            report += f"- {issue}\n"
    else:
        report += "- No configuration issues found\n"
    
    report += """
### 3. Documentation Updates
Update documentation to reflect the new structure:

"""
    
    doc_issues = check_documentation_links()
    if doc_issues:
        report += f"- Found {len(doc_issues)} potentially broken documentation links\n"
        report += "- Update README files with new paths\n"
        report += "- Update API documentation references\n"
    else:
        report += "- No documentation issues found\n"
    
    report += """
## Testing Checklist

### Build and Deployment
- [ ] Test Docker build process
- [ ] Test docker-compose configurations
- [ ] Test Kubernetes deployment
- [ ] Test Helm charts
- [ ] Verify all services start correctly

### Application Testing
- [ ] Run full test suite
- [ ] Test API endpoints
- [ ] Test frontend functionality
- [ ] Test monitoring and logging
- [ ] Test security features

### Integration Testing
- [ ] Test service communication
- [ ] Test database connections
- [ ] Test external API integrations
- [ ] Test backup and restore processes

## CI/CD Pipeline Updates

### GitHub Actions
- [ ] Update workflow file paths
- [ ] Update build contexts
- [ ] Update test paths
- [ ] Update deployment configurations

### Docker
- [ ] Update Dockerfile paths
- [ ] Update docker-compose file references
- [ ] Test image builds
- [ ] Verify container networking

### Kubernetes
- [ ] Update manifest file paths
- [ ] Update Helm chart paths
- [ ] Test deployment
- [ ] Verify service discovery

## Team Communication

### Documentation Updates
- [ ] Update team onboarding materials
- [ ] Update development guidelines
- [ ] Update code review checklists
- [ ] Update release procedures

### Training
- [ ] Schedule team training session
- [ ] Create walkthrough of new structure
- [ ] Document common tasks in new structure
- [ ] Establish support processes

## Monitoring and Observability

### Setup
- [ ] Configure Prometheus monitoring
- [ ] Set up Grafana dashboards
- [ ] Configure alerting rules
- [ ] Test monitoring endpoints

### Logging
- [ ] Configure centralized logging
- [ ] Set up log aggregation
- [ ] Configure log retention policies
- [ ] Test log shipping

## Security and Compliance

### Security
- [ ] Review security configurations
- [ ] Test secret management
- [ ] Verify access controls
- [ ] Run security scans

### Compliance
- [ ] Review compliance documentation
- [ ] Update audit procedures
- [ ] Configure compliance monitoring
- [ ] Test compliance reporting

## Success Metrics

### Immediate (Week 1)
- [ ] All tests passing
- [ ] Build process working
- [ ] Deployment successful
- [ ] Team trained on new structure

### Short-term (Month 1)
- [ ] Monitoring operational
- [ ] Security measures in place
- [ ] Documentation complete
- [ ] Performance optimized

### Long-term (Month 3)
- [ ] Enterprise features deployed
- [ ] Compliance requirements met
- [ ] Support processes established
- [ ] Governance procedures in place

## Support and Resources

### Documentation
- Project Structure: `docs/enterprise/PROJECT_STRUCTURE.md`
- Quick Reference: `docs/enterprise/QUICK_REFERENCE.md`
- Cleanup Summary: `docs/enterprise/CLEANUP_SUMMARY.md`

### Scripts
- Cleanup Script: `scripts/cleanup_enterprise.py`
- Next Steps: `scripts/next_steps.py`

### Contact
- Enterprise Support: enterprise-support@scorpius.com
- Documentation: `docs/enterprise/`
- Issues: GitHub Issues

---
Report generated by next_steps.py
"""
    
    with open('docs/enterprise/NEXT_STEPS_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ Next steps report generated: docs/enterprise/NEXT_STEPS_REPORT.md")

def main():
    """Main function."""
    print("🚀 Scorpius Enterprise - Next Steps Analysis")
    print("=" * 50)
    
    # Run all checks
    check_import_paths()
    check_configuration_files()
    check_documentation_links()
    
    # Generate comprehensive report
    generate_next_steps_report()
    
    print("\n🎉 Analysis complete!")
    print("\n📋 Next steps:")
    print("1. Review the generated report: docs/enterprise/NEXT_STEPS_REPORT.md")
    print("2. Address any issues found in the analysis")
    print("3. Test the build and deployment processes")
    print("4. Update team documentation and training materials")
    print("5. Implement monitoring and security measures")

if __name__ == "__main__":
    main() 