import os
import sys
import yaml
import logging
import docker
import requests
import subprocess
from typing import Dict, Any, List
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

class ProductionVerifier:
    def __init__(self, config_path: str):
        """
        Initialize production verifier
        
        Args:
            config_path: Path to verification configuration
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = logging.getLogger(__name__)
        self.docker_client = docker.from_env()
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.config['aws']['access_key'],
            aws_secret_access_key=self.config['aws']['secret_key'],
            region_name=self.config['aws']['region']
        )

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

    def _load_config(self) -> Dict[str, Any]:
        """Load verification configuration"""
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

    def verify_docker_images(self) -> Dict[str, Any]:
        """Verify Docker images are built and tagged correctly"""
        results = {}
        try:
            for service in self.config['services']:
                image_name = f"scorpius/{service}:latest"
                try:
                    image = self.docker_client.images.get(image_name)
                    results[service] = {
                        'status': 'pass',
                        'size': image.attrs['Size'] / (1024 * 1024),  # Size in MB
                        'created': image.attrs['Created']
                    }
                except docker.errors.ImageNotFound:
                    results[service] = {
                        'status': 'fail',
                        'error': 'Image not found'
                    }
            return results
        except Exception as e:
            self.logger.error(f"Failed to verify Docker images: {str(e)}")
            raise

    def verify_kubernetes_resources(self) -> Dict[str, Any]:
        """Verify Kubernetes resources are properly configured"""
        results = {}
        try:
            # Check for required resources
            required_resources = [
                'deployment',
                'service',
                'ingress',
                'configmap',
                'secret'
            ]
            
            for resource in required_resources:
                try:
                    # Get list of resources
                    cmd = [
                        'kubectl',
                        'get',
                        resource,
                        '-n', self.config['kubernetes']['namespace']
                    ]
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        results[resource] = {
                            'status': 'fail',
                            'error': result.stderr
                        }
                    else:
                        results[resource] = {
                            'status': 'pass',
                            'count': len(result.stdout.splitlines()) - 1
                        }
                except Exception as e:
                    results[resource] = {
                        'status': 'fail',
                        'error': str(e)
                    }
            return results
        except Exception as e:
            self.logger.error(f"Failed to verify Kubernetes resources: {str(e)}")
            raise

    def verify_backup_system(self) -> Dict[str, Any]:
        """Verify backup system is functioning"""
        results = {}
        try:
            # Check S3 bucket exists
            try:
                self.s3_client.head_bucket(Bucket=self.config['backup']['s3_bucket'])
                results['bucket'] = {
                    'status': 'pass'
                }
            except ClientError as e:
                results['bucket'] = {
                    'status': 'fail',
                    'error': str(e)
                }
            
            # Check backup schedule
            try:
                cmd = [
                    'kubectl',
                    'get',
                    'cronjob',
                    '-n', self.config['kubernetes']['namespace']
                ]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    results['schedule'] = {
                        'status': 'fail',
                        'error': result.stderr
                    }
                else:
                    results['schedule'] = {
                        'status': 'pass',
                        'count': len(result.stdout.splitlines()) - 1
                    }
            except Exception as e:
                results['schedule'] = {
                    'status': 'fail',
                    'error': str(e)
                }
            
            return results
        except Exception as e:
            self.logger.error(f"Failed to verify backup system: {str(e)}")
            raise

    def verify_monitoring_system(self) -> Dict[str, Any]:
        """Verify monitoring system is properly configured"""
        results = {}
        try:
            # Check Prometheus endpoints
            try:
                response = requests.get(
                    f"http://{self.config['monitoring']['prometheus_host']}/api/v1/status/config"
                )
                if response.status_code == 200:
                    results['prometheus'] = {
                        'status': 'pass'
                    }
                else:
                    results['prometheus'] = {
                        'status': 'fail',
                        'error': response.text
                    }
            except Exception as e:
                results['prometheus'] = {
                    'status': 'fail',
                    'error': str(e)
                }
            
            # Check Alertmanager
            try:
                response = requests.get(
                    f"http://{self.config['monitoring']['alertmanager_host']}/api/v2/status"
                )
                if response.status_code == 200:
                    results['alertmanager'] = {
                        'status': 'pass'
                    }
                else:
                    results['alertmanager'] = {
                        'status': 'fail',
                        'error': response.text
                    }
            except Exception as e:
                results['alertmanager'] = {
                    'status': 'fail',
                    'error': str(e)
                }
            
            return results
        except Exception as e:
            self.logger.error(f"Failed to verify monitoring system: {str(e)}")
            raise

    def verify_security_settings(self) -> Dict[str, Any]:
        """Verify security settings are properly configured"""
        results = {}
        try:
            # Check TLS configuration
            try:
                response = requests.get(
                    f"https://{self.config['ingress']['host']}",
                    verify=True
                )
                if response.status_code == 200:
                    results['tls'] = {
                        'status': 'pass'
                    }
                else:
                    results['tls'] = {
                        'status': 'fail',
                        'error': 'TLS verification failed'
                    }
            except Exception as e:
                results['tls'] = {
                    'status': 'fail',
                    'error': str(e)
                }
            
            # Check rate limiting
            try:
                # Send multiple requests to test rate limiting
                for _ in range(1000):
                    response = requests.get(
                        f"http://{self.config['ingress']['host']}/api/health"
                    )
                    if response.status_code == 429:
                        results['rate_limiting'] = {
                            'status': 'pass'
                        }
                        break
                else:
                    results['rate_limiting'] = {
                        'status': 'fail',
                        'error': 'Rate limiting not working'
                    }
            except Exception as e:
                results['rate_limiting'] = {
                    'status': 'fail',
                    'error': str(e)
                }
            
            return results
        except Exception as e:
            self.logger.error(f"Failed to verify security settings: {str(e)}")
            raise

    def generate_report(self, verification_results: Dict[str, Any]) -> str:
        """Generate verification report"""
        report = "# Production Verification Report\n\n"
        report += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Docker images
        report += "## Docker Images\n\n"
        for service, result in verification_results['docker_images'].items():
            status = "PASS" if result['status'] == 'pass' else "FAIL"
            report += f"- {service}: {status}"
            if result['status'] == 'fail':
                report += f" ({result['error']})\n"
            else:
                report += f" (Size: {result['size']:.2f} MB)\n"

        # Kubernetes resources
        report += "\n## Kubernetes Resources\n\n"
        for resource, result in verification_results['k8s_resources'].items():
            status = "PASS" if result['status'] == 'pass' else "FAIL"
            report += f"- {resource}: {status}"
            if result['status'] == 'fail':
                report += f" ({result['error']})\n"
            else:
                report += f" (Count: {result['count']})\n"

        # Backup system
        report += "\n## Backup System\n\n"
        for component, result in verification_results['backup'].items():
            status = "PASS" if result['status'] == 'pass' else "FAIL"
            report += f"- {component}: {status}"
            if result['status'] == 'fail':
                report += f" ({result['error']})\n"

        # Monitoring system
        report += "\n## Monitoring System\n\n"
        for component, result in verification_results['monitoring'].items():
            status = "PASS" if result['status'] == 'pass' else "FAIL"
            report += f"- {component}: {status}"
            if result['status'] == 'fail':
                report += f" ({result['error']})\n"

        # Security settings
        report += "\n## Security Settings\n\n"
        for setting, result in verification_results['security'].items():
            status = "PASS" if result['status'] == 'pass' else "FAIL"
            report += f"- {setting}: {status}"
            if result['status'] == 'fail':
                report += f" ({result['error']})\n"

        return report

    def verify_all(self) -> Dict[str, Any]:
        """Perform all verification checks"""
        results = {
            'docker_images': self.verify_docker_images(),
            'k8s_resources': self.verify_kubernetes_resources(),
            'backup': self.verify_backup_system(),
            'monitoring': self.verify_monitoring_system(),
            'security': self.verify_security_settings()
        }
        
        # Generate and save report
        report = self.generate_report(results)
        self._save_report(report)
        
        return results

    def _save_report(self, report: str) -> None:
        """Save verification report"""
        try:
            # Use Windows path for reports
            output_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'logs',
                'verification',
                'production_report.md'
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(report)
            
            self.logger.info(f"Verification report saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save verification report: {str(e)}")
            raise

def main():
    """Main entry point"""
    try:
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/verification/verification.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logger = logging.getLogger(__name__)

        # Load configuration
        config_path = os.getenv('VERIFICATION_CONFIG', 'config/verification.yaml')
        logger.info(f"Using config path: {config_path}")
        verifier = ProductionVerifier(config_path)
        
        # Perform verification
        logger.info("Starting verification process...")
        results = verifier.verify_all()
        logger.info("Verification completed")
        
        # Print summary
        logger.info("\nVerification Summary:")
        logger.info("-" * 50)
        
        # Check for failures
        has_failures = False
        for category, result in results.items():
            logger.info(f"\n{category.replace('_', ' ').title()}:")
            for component, status in result.items():
                if status['status'] == 'fail':
                    has_failures = True
                    logger.error(f"FAIL {component}: {status['error']}")
                else:
                    logger.info(f"PASS {component}")
        
        logger.info("\n-" * 50)
        
        if has_failures:
            logger.error("\nFAIL Verification FAILED - Please review the report for details")
            sys.exit(1)
        else:
            logger.info("\nPASS Verification PASSED - All checks successful")
            
    except Exception as e:
        logger.error(f"\nError: {str(e)}")
        import traceback
        logger.error("Traceback:")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
