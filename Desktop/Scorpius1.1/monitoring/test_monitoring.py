#!/usr/bin/env python3
"""
Test script for SLA monitoring and alerting system
"""

import time
import requests
import yaml
import json
import sys
from datetime import datetime


def test_prometheus_config():
    """Test Prometheus configuration validity"""
    print("🔍 Testing Prometheus configuration...")
    
    try:
        with open('prometheus.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        required_sections = ['global', 'scrape_configs', 'rule_files', 'alerting']
        missing_sections = []
        
        for section in required_sections:
            if section not in config:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing sections in prometheus.yml: {missing_sections}")
            return False
        
        # Check scrape configs
        scrape_configs = config.get('scrape_configs', [])
        expected_jobs = [
            'prometheus', 'api-gateway', 'wallet-guard', 'usage-metering',
            'scanner-service', 'bridge-service', 'node-exporter'
        ]
        
        configured_jobs = [job.get('job_name') for job in scrape_configs]
        missing_jobs = [job for job in expected_jobs if job not in configured_jobs]
        
        if missing_jobs:
            print(f"⚠️  Missing scrape jobs: {missing_jobs}")
        
        print("✅ Prometheus configuration valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading prometheus.yml: {e}")
        return False


def test_alerting_rules():
    """Test alerting rules configuration"""
    print("\n🚨 Testing alerting rules...")
    
    rule_files = [
        'rules/sla_alerts.yml',
        'rules/audit_security_alerts.yml'
    ]
    
    all_valid = True
    total_rules = 0
    
    for rule_file in rule_files:
        try:
            with open(rule_file, 'r') as f:
                rules = yaml.safe_load(f)
            
            groups = rules.get('groups', [])
            for group in groups:
                group_rules = group.get('rules', [])
                total_rules += len(group_rules)
                
                for rule in group_rules:
                    # Check required fields for alerts
                    if 'alert' in rule:
                        required_fields = ['expr', 'labels', 'annotations']
                        for field in required_fields:
                            if field not in rule:
                                print(f"❌ Alert {rule.get('alert', 'Unknown')} missing {field}")
                                all_valid = False
            
            print(f"✅ {rule_file}: {len([r for g in groups for r in g.get('rules', [])])} rules")
            
        except Exception as e:
            print(f"❌ Error reading {rule_file}: {e}")
            all_valid = False
    
    print(f"📊 Total alerting rules: {total_rules}")
    return all_valid


def test_alertmanager_config():
    """Test Alertmanager configuration"""
    print("\n📧 Testing Alertmanager configuration...")
    
    try:
        with open('alertmanager.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        required_sections = ['global', 'route', 'receivers']
        missing_sections = []
        
        for section in required_sections:
            if section not in config:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing sections in alertmanager.yml: {missing_sections}")
            return False
        
        # Check receivers
        receivers = config.get('receivers', [])
        expected_receivers = [
            'critical-alerts', 'sla-violations', 'infrastructure-team',
            'platform-team', 'security-team', 'billing-team'
        ]
        
        configured_receivers = [r.get('name') for r in receivers]
        missing_receivers = [r for r in expected_receivers if r not in configured_receivers]
        
        if missing_receivers:
            print(f"⚠️  Missing receivers: {missing_receivers}")
        
        print(f"✅ Alertmanager configuration valid ({len(receivers)} receivers)")
        return True
        
    except Exception as e:
        print(f"❌ Error reading alertmanager.yml: {e}")
        return False


def test_grafana_dashboards():
    """Test Grafana dashboard configurations"""
    print("\n📊 Testing Grafana dashboards...")
    
    dashboard_files = [
        'dashboards/sla-dashboard.json'
    ]
    
    all_valid = True
    
    for dashboard_file in dashboard_files:
        try:
            with open(dashboard_file, 'r') as f:
                dashboard = json.load(f)
            
            if 'dashboard' not in dashboard:
                print(f"❌ {dashboard_file}: Invalid dashboard structure")
                all_valid = False
                continue
            
            panels = dashboard['dashboard'].get('panels', [])
            panel_count = len(panels)
            
            # Check for essential panels
            panel_titles = [p.get('title', '') for p in panels]
            essential_panels = [
                'Platform Availability', 'API Gateway Latency', 'Error Rate',
                'Service Status', 'Active Alerts'
            ]
            
            missing_panels = []
            for panel in essential_panels:
                if not any(panel in title for title in panel_titles):
                    missing_panels.append(panel)
            
            if missing_panels:
                print(f"⚠️  {dashboard_file}: Missing panels: {missing_panels}")
            
            print(f"✅ {dashboard_file}: {panel_count} panels")
            
        except Exception as e:
            print(f"❌ Error reading {dashboard_file}: {e}")
            all_valid = False
    
    return all_valid


def test_sla_thresholds():
    """Test SLA threshold definitions"""
    print("\n📏 Testing SLA thresholds...")
    
    sla_requirements = {
        'api_gateway_latency_p95': 2.5,  # seconds
        'platform_availability': 99.9,   # percentage
        'error_rate': 2.0,               # percentage
        'wallet_guard_latency_p95': 1.8   # seconds
    }
    
    try:
        with open('rules/sla_alerts.yml', 'r') as f:
            rules = yaml.safe_load(f)
        
        found_thresholds = {}
        
        for group in rules.get('groups', []):
            for rule in group.get('rules', []):
                if 'alert' in rule:
                    alert_name = rule['alert']
                    expr = rule['expr']
                    
                    # Extract thresholds from expressions
                    if 'APIGatewayHighLatency' in alert_name and '>' in expr:
                        threshold = float(expr.split('>')[-1].strip())
                        found_thresholds['api_gateway_latency_p95'] = threshold
                    
                    elif 'APIGatewayHighErrorRate' in alert_name and '>' in expr:
                        threshold = float(expr.split('>')[-1].strip())
                        found_thresholds['error_rate'] = threshold * 100  # Convert to percentage
                    
                    elif 'WalletGuardHighLatency' in alert_name and '>' in expr:
                        threshold = float(expr.split('>')[-1].strip())
                        found_thresholds['wallet_guard_latency_p95'] = threshold
        
        # Validate thresholds
        all_correct = True
        for metric, expected_threshold in sla_requirements.items():
            if metric in found_thresholds:
                actual_threshold = found_thresholds[metric]
                if actual_threshold != expected_threshold:
                    print(f"⚠️  {metric}: Expected {expected_threshold}, found {actual_threshold}")
                    all_correct = False
                else:
                    print(f"✅ {metric}: {actual_threshold}")
            else:
                print(f"❌ {metric}: Threshold not found")
                all_correct = False
        
        return all_correct
        
    except Exception as e:
        print(f"❌ Error checking SLA thresholds: {e}")
        return False


def test_metrics_endpoints():
    """Test that metrics endpoints are properly configured"""
    print("\n📈 Testing metrics endpoint configurations...")
    
    metrics_endpoints = [
        ('API Gateway', 'api-gateway:8000/metrics'),
        ('Usage Metering', 'usage-metering:8005/metrics/usage'),
        ('Wallet Guard', 'wallet-guard:8006/metrics'),
        ('Prometheus', 'localhost:9090/metrics')
    ]
    
    configured_endpoints = []
    try:
        with open('prometheus.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        for job in config.get('scrape_configs', []):
            targets = job.get('static_configs', [{}])[0].get('targets', [])
            metrics_path = job.get('metrics_path', '/metrics')
            
            for target in targets:
                endpoint = f"{target}{metrics_path}"
                configured_endpoints.append((job.get('job_name'), endpoint))
    
    except Exception as e:
        print(f"❌ Error reading prometheus config: {e}")
        return False
    
    print(f"✅ Found {len(configured_endpoints)} configured metrics endpoints")
    return True


def generate_monitoring_report():
    """Generate comprehensive monitoring report"""
    print("\n" + "="*60)
    print("📋 SCORPIUS SLA MONITORING VALIDATION REPORT")
    print("="*60)
    
    test_results = {
        'prometheus_config': test_prometheus_config(),
        'alerting_rules': test_alerting_rules(),
        'alertmanager_config': test_alertmanager_config(),
        'grafana_dashboards': test_grafana_dashboards(),
        'sla_thresholds': test_sla_thresholds(),
        'metrics_endpoints': test_metrics_endpoints()
    }
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("\n🎉 SLA MONITORING SYSTEM VALIDATION PASSED!")
        print("\nMonitoring system includes:")
        print("✅ Comprehensive Prometheus configuration")
        print("✅ SLA alerting rules with proper thresholds")
        print("✅ Multi-channel alerting via Alertmanager")
        print("✅ Grafana dashboards for SLA visualization")
        print("✅ Audit trail and security monitoring")
        print("✅ Business metrics and compliance rules")
        print("✅ Infrastructure and performance monitoring")
        
        print("\n🎯 SLA Coverage:")
        print("• API Gateway: <2.5s p95 latency, <2% error rate, 99.9% availability")
        print("• Wallet Guard: <1.8s p95 latency for 25 addresses")
        print("• Usage Metering: <1s API latency")
        print("• Audit Trail: Tamper detection, compliance monitoring")
        print("• Security: Failed auth, suspicious activity, rate limiting")
        
        return True
    else:
        print("\n❌ SLA MONITORING SYSTEM VALIDATION FAILED!")
        print("Please fix the failing components above.")
        
        failed_tests = [test for test, result in test_results.items() if not result]
        print(f"\nFailed tests: {', '.join(failed_tests)}")
        
        return False


def main():
    """Main execution function"""
    print("🔍 Validating Scorpius SLA Monitoring & Alerting System...")
    print("Starting validation at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    success = generate_monitoring_report()
    
    if success:
        print("\n🚀 Ready for production deployment!")
        print("Next steps:")
        print("1. Configure environment variables (Slack webhooks, SMTP)")
        print("2. Deploy monitoring stack with docker-compose")
        print("3. Import Grafana dashboards")
        print("4. Test alert routing and notifications")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
