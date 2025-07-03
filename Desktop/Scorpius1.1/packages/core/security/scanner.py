import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from fastapi import HTTPException
import docker
from docker.errors import APIError
import boto3
from botocore.exceptions import ClientError
import requests
import hashlib
import re
import subprocess
import logging
from datetime import datetime
import yaml

class SecurityScanner:
    def __init__(self, docker_client: docker.DockerClient = None):
        """
        Initialize security scanner
        
        Args:
            docker_client: Docker client instance
        """
        self.docker_client = docker_client or docker.from_env()
        self.scans_dir = Path("/tmp/scans")
        self.scans_dir.mkdir(exist_ok=True)

    def scan_image(self, image_name: str, config: Dict[str, Any]) -> Dict:
        """
        Scan a Docker image for vulnerabilities
        
        Args:
            image_name: Name of the Docker image to scan
            config: Security scanner configuration
            
        Returns:
            Dictionary containing scan results
        """
        try:
            # Pull the latest image
            self.docker_client.images.pull(image_name)
            
            # Run Trivy scan
            scan_id = os.urandom(16).hex()
            scan_path = self.scans_dir / f"scan_{scan_id}.json"
            
            # Create Trivy container
            container = self.docker_client.containers.create(
                image="aquasec/trivy:latest",
                command=f"--format json --output {scan_path} {image_name} "
                      f"--severity {config['trivy']['severity']} "
                      f"--ignore-unfixed {config['trivy']['ignore_unfixed']} "
                      f"--skip-files {config['trivy']['skip_files']} "
                      f"--skip-dirs {config['trivy']['skip_dirs']}",
                volumes={
                    str(self.scans_dir): {
                        'bind': '/scans',
                        'mode': 'rw'
                    }
                }
            )
            
            # Start and wait for container
            container.start()
            container.wait()
            
            # Get scan results
            with open(scan_path, 'r') as f:
                results = json.load(f)
            
            # Clean up
            container.remove()
            os.remove(scan_path)
            
            return results
            
        except APIError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error scanning image: {str(e)}"
            )

    def scan_code(self, path: str) -> Dict:
        """
        Scan code for security vulnerabilities
        
        Args:
            path: Path to code directory
            
        Returns:
            Dictionary containing scan results
        """
        try:
            # Run Bandit scan
            scan_id = os.urandom(16).hex()
            scan_path = self.scans_dir / f"code_scan_{scan_id}.json"
            
            # Create Bandit container
            container = self.docker_client.containers.create(
                image="banditsec/bandit",
                command=f"-r {path} -f json -o {scan_path}",
                volumes={
                    path: {
                        'bind': '/code',
                        'mode': 'ro'
                    },
                    str(self.scans_dir): {
                        'bind': '/scans',
                        'mode': 'rw'
                    }
                }
            )
            
            # Start and wait for container
            container.start()
            container.wait()
            
            # Get scan results
            with open(scan_path, 'r') as f:
                results = json.load(f)
            
            # Clean up
            container.remove()
            os.remove(scan_path)
            
            return results
            
        except APIError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error scanning code: {str(e)}"
            )

    def scan_dependencies(self, requirements_path: str) -> Dict:
        """
        Scan Python dependencies for vulnerabilities
        
        Args:
            requirements_path: Path to requirements.txt
            
        Returns:
            Dictionary containing scan results
        """
        try:
            # Run Safety scan
            scan_id = os.urandom(16).hex()
            scan_path = self.scans_dir / f"dep_scan_{scan_id}.json"
            
            # Create Safety container
            container = self.docker_client.containers.create(
                image="pyupio/safety",
                command=f"check --full-report --json -r {requirements_path} -o {scan_path}",
                volumes={
                    requirements_path: {
                        'bind': '/requirements.txt',
                        'mode': 'ro'
                    },
                    str(self.scans_dir): {
                        'bind': '/scans',
                        'mode': 'rw'
                    }
                }
            )
            
            # Start and wait for container
            container.start()
            container.wait()
            
            # Get scan results
            with open(scan_path, 'r') as f:
                results = json.load(f)
            
            # Clean up
            container.remove()
            os.remove(scan_path)
            
            return results
            
        except APIError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error scanning dependencies: {str(e)}"
            )

    def get_scan_status(self, scan_id: str) -> Optional[Dict]:
        """
        Get status of a scan
        
        Args:
            scan_id: ID of the scan
            
        Returns:
            Dictionary containing scan status or None if not found
        """
        scan_path = self.scans_dir / f"scan_{scan_id}.json"
        if scan_path.exists():
            with open(scan_path, 'r') as f:
                return json.load(f)
        return None

    def get_vulnerabilities(self, scan_results: Dict) -> List[Dict]:
        """
        Extract vulnerabilities from scan results
        
        Args:
            scan_results: Dictionary containing scan results
            
        Returns:
            List of vulnerabilities
        """
        vulnerabilities = []
        
        if 'Vulnerabilities' in scan_results:
            for vuln in scan_results['Vulnerabilities']:
                vulnerabilities.append({
                    'id': vuln.get('VulnerabilityID'),
                    'severity': vuln.get('Severity'),
                    'package': vuln.get('PkgName'),
                    'version': vuln.get('InstalledVersion'),
                    'description': vuln.get('Description'),
                    'fix': vuln.get('FixedVersion')
                })
        
        return vulnerabilities

    def generate_report(self, scan_results: Dict) -> Dict:
        """
        Generate a formatted report from scan results
        
        Args:
            scan_results: Dictionary containing scan results
            
        Returns:
            Formatted report
        """
        report = {
            'scan_id': os.urandom(16).hex(),
            'timestamp': time.time(),
            'vulnerabilities': self.get_vulnerabilities(scan_results),
            'summary': {
                'total_vulnerabilities': len(self.get_vulnerabilities(scan_results)),
                'critical': len([v for v in self.get_vulnerabilities(scan_results) 
                               if v['severity'] == 'CRITICAL']),
                'high': len([v for v in self.get_vulnerabilities(scan_results) 
                           if v['severity'] == 'HIGH']),
                'medium': len([v for v in self.get_vulnerabilities(scan_results) 
                             if v['severity'] == 'MEDIUM']),
                'low': len([v for v in self.get_vulnerabilities(scan_results) 
                           if v['severity'] == 'LOW'])
            }
        }
        
        return report
