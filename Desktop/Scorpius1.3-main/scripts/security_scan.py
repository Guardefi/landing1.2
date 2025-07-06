import os
import sys
import yaml
import logging
from datetime import datetime
from pathlib import Path
from core.security.scanner import SecurityScanner

class SecurityScanManager:
    def __init__(self, config_path: str):
        """
        Initialize security scan manager
        
        Args:
            config_path: Path to security scanner configuration
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.scanner = SecurityScanner()

    def _load_config(self) -> dict:
        """Load security scanner configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {str(e)}")
            raise

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config['logging']['level']),
            format=self.config['logging']['format'],
            handlers=[
                logging.FileHandler(self.config['logging']['file']),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)

    def scan_code(self) -> dict:
        """Perform code security scanning"""
        try:
            self.logger.info("Starting code security scan...")
            results = self.scanner.scan_code(
                directory=self.config['code']['directory'],
                exclude_patterns=self.config['code']['exclude_patterns']
            )
            self.logger.info("Code scan completed")
            return results
        except Exception as e:
            self.logger.error(f"Code scan failed: {str(e)}")
            raise

    def scan_containers(self) -> dict:
        """Scan all configured containers"""
        results = {}
        try:
            self.logger.info("Starting container security scans...")
            for image in self.config['containers']['images']:
                self.logger.info(f"Scanning container: {image}")
                results[image] = self.scanner.scan_image(
                    image_name=image,
                    config=self.config['trivy']
                )
            self.logger.info("Container scans completed")
            return results
        except Exception as e:
            self.logger.error(f"Container scan failed: {str(e)}")
            raise

    def scan_infrastructure(self) -> dict:
        """Scan infrastructure configuration"""
        results = {}
        try:
            self.logger.info("Starting infrastructure security scan...")
            if self.config['infrastructure']['k8s']['enabled']:
                results['k8s'] = self.scanner.scan_kubernetes()
            if self.config['infrastructure']['network']['enabled']:
                results['network'] = self.scanner.scan_network()
            self.logger.info("Infrastructure scan completed")
            return results
        except Exception as e:
            self.logger.error(f"Infrastructure scan failed: {str(e)}")
            raise

    def generate_report(self, scan_results: dict) -> str:
        """Generate security scan report"""
        report = "# Security Scan Report\n\n"
        report += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Code scan results
        if 'code' in scan_results:
            report += "## Code Security\n\n"
            report += f"- Secrets found: {len(scan_results['code'].get('secrets', []))}\n"
            report += f"- Vulnerabilities: {len(scan_results['code'].get('vulnerabilities', []))}\n"

        # Container scan results
        if 'containers' in scan_results:
            report += "\n## Container Security\n\n"
            for image, result in scan_results['containers'].items():
                report += f"### {image}\n"
                report += f"- Critical: {len(result.get('critical', []))}\n"
                report += f"- High: {len(result.get('high', []))}\n"
                report += f"- Medium: {len(result.get('medium', []))}\n"

        # Infrastructure scan results
        if 'infrastructure' in scan_results:
            report += "\n## Infrastructure Security\n\n"
            if 'k8s' in scan_results['infrastructure']:
                report += f"- Kubernetes: {scan_results['infrastructure']['k8s'].get('status', 'N/A')}\n"
            if 'network' in scan_results['infrastructure']:
                report += f"- Network: {scan_results['infrastructure']['network'].get('status', 'N/A')}\n"

        return report

    def save_report(self, report: str, output_path: str = None) -> None:
        """Save security scan report"""
        try:
            output_path = output_path or self.config['reports']['output_path']
            os.makedirs(Path(output_path).parent, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(report)
            self.logger.info(f"Report saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save report: {str(e)}")
            raise

    def send_alerts(self, scan_results: dict) -> None:
        """Send security alerts if needed"""
        try:
            # Check severity thresholds
            severity = self._determine_severity(scan_results)
            if severity >= self.config['alerts']['severity_threshold']:
                self._send_slack_alert(scan_results, severity)
                self._send_email_alert(scan_results, severity)
        except Exception as e:
            self.logger.error(f"Failed to send alerts: {str(e)}")
            raise

    def _determine_severity(self, scan_results: dict) -> str:
        """Determine overall scan severity"""
        severity = "INFO"
        
        # Check container vulnerabilities
        if 'containers' in scan_results:
            for result in scan_results['containers'].values():
                if result.get('critical'):
                    severity = "CRITICAL"
                elif result.get('high'):
                    severity = max(severity, "HIGH")
                elif result.get('medium'):
                    severity = max(severity, "MEDIUM")

        # Check code issues
        if 'code' in scan_results:
            if scan_results['code'].get('secrets'):
                severity = max(severity, "HIGH")
            if scan_results['code'].get('vulnerabilities'):
                severity = max(severity, "MEDIUM")

        return severity

    def _send_slack_alert(self, scan_results: dict, severity: str) -> None:
        """Send Slack alert"""
        try:
            if self.config['alerts']['methods']['slack']['enabled']:
                webhook = self.config['alerts']['methods']['slack']['webhook']
                channel = self.config['alerts']['methods']['slack']['channel']
                
                # Create Slack message
                message = {
                    "channel": channel,
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Security Alert: {severity.upper()}*"
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Date:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Severity:*\n{severity.upper()}"
                                }
                            ]
                        }
                    ]
                }
                
                # Send to Slack
                response = requests.post(
                    webhook,
                    json=message,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code != 200:
                    self.logger.error(f"Failed to send Slack alert: {response.text}")
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {str(e)}")
            raise

    def _send_email_alert(self, scan_results: dict, severity: str) -> None:
        """Send email alert"""
        try:
            if self.config['alerts']['methods']['email']['enabled']:
                recipients = self.config['alerts']['methods']['email']['recipients']
                subject = f"Security Alert: {severity.upper()}"
                
                # Create email content
                message = f"""
                Security Alert: {severity.upper()}
                Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                
                Scan Results:
                {self.generate_report(scan_results)}
                """
                
                # TODO: Implement email sending
                self.logger.info(f"Email alert sent to {recipients}")
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {str(e)}")
            raise

def main():
    """Main entry point"""
    try:
        # Load configuration
        config_path = os.getenv('SECURITY_CONFIG', 'config/security/scanner_config.yaml')
        manager = SecurityScanManager(config_path)
        
        # Perform scans
        scan_results = {
            'code': manager.scan_code(),
            'containers': manager.scan_containers(),
            'infrastructure': manager.scan_infrastructure()
        }
        
        # Generate and save report
        report = manager.generate_report(scan_results)
        manager.save_report(report)
        
        # Send alerts if needed
        manager.send_alerts(scan_results)
        
        # Print summary
        print("\nSecurity Scan Summary:")
        print("-" * 50)
        print(f"Code Scan: {'PASS' if not scan_results['code'].get('secrets') else 'FAIL'}")
        print(f"Container Scan: {'PASS' if all(len(r.get('critical', [])) == 0 for r in scan_results['containers'].values()) else 'FAIL'}")
        print(f"Infrastructure Scan: {'PASS' if not scan_results['infrastructure'].get('violations') else 'FAIL'}")
        print("-" * 50)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
