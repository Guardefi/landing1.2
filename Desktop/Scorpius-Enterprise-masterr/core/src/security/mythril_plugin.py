"""Mythril scanner plugin for Scorpius Vulnerability Scanner

This module integrates the Mythril symbolic execution engine for EVM bytecode analysis.
Mythril can detect various security vulnerabilities in Ethereum smart contracts
through symbolic execution and constraint solving.
"""

import json
import logging
import os
import subprocess
import tempfile
import asyncio
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set

from scanners.base import BaseScannerPlugin
from core.models import (
    ScanType, Target, ScanConfig, VulnerabilityFinding,
    VulnerabilityLevel
)

logger = logging.getLogger("scorpius.scanners.mythril")

# Mapping of Mythril severity levels to our vulnerability levels
MYTHRIL_SEVERITY_TO_LEVEL = {
    "High": VulnerabilityLevel.HIGH,
    "Medium": VulnerabilityLevel.MEDIUM,
    "Low": VulnerabilityLevel.LOW,
    "Informational": VulnerabilityLevel.INFO
}


class MythrilPlugin(BaseScannerPlugin):
    """Mythril symbolic execution plugin for smart contract security analysis"""
    
    NAME = "mythril"
    DESCRIPTION = "Dynamic security analysis of EVM bytecode using Mythril symbolic execution engine"
    VERSION = "0.1.0"
    AUTHOR = "Scorpius Team"
    SUPPORTED_SCAN_TYPES = [ScanType.DYNAMIC, ScanType.FULL, ScanType.DEEP]
    DEPENDENCIES = ["mythril"]
    
    def __init__(self):
        """Initialize the Mythril plugin"""
        super().__init__()
        self.temp_dirs = []
        
    async def initialize(self) -> bool:
        """Initialize the Mythril plugin
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if self.initialized:
            return True
        
        # Call parent initialization, which checks dependencies
        if not await super().initialize():
            return False
        
        try:
            # Check if Mythril is installed and available
            proc = await asyncio.create_subprocess_exec(
                "myth", "version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                logger.error(f"Mythril is not installed or not in PATH")
                return False
                
            # Parse version to ensure compatibility
            version = stdout.decode().strip()
            logger.info(f"Found Mythril version: {version}")
            
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Mythril plugin: {e}")
            return False
    
    async def _check_dependency(self, dependency: str) -> bool:
        """Check if a specific dependency is available
        
        Args:
            dependency: The dependency to check
            
        Returns:
            bool: True if dependency is available, False otherwise
        """
        if dependency == "mythril":
            try:
                # Use pip to check if it's installed
                proc = await asyncio.create_subprocess_exec(
                    "pip", "show", "mythril",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                return proc.returncode == 0
            except Exception:
                return False
                
        return await super()._check_dependency(dependency)
    
    async def scan(self, target: Target, config: ScanConfig) -> List[VulnerabilityFinding]:
        """Perform a security scan using Mythril
        
        Args:
            target: Target to scan
            config: Configuration for the scan
            
        Returns:
            List[VulnerabilityFinding]: List of vulnerability findings
        """
        if not self.initialized:
            await self.initialize()
            if not self.initialized:
                logger.error("Cannot perform scan, Mythril plugin not initialized")
                return []
        
        logger.info(f"Starting Mythril scan for target {target.identifier}")
        
        # Mythril can analyze:
        # 1. Solidity source files
        # 2. Deployed contracts (by address)
        # 3. Bytecode
        
        if target.source_code:
            return await self._scan_source_files(target, config)
        elif target.identifier and target.blockchain:
            return await self._scan_deployed_contract(target, config)
        elif target.bytecode:
            return await self._scan_bytecode(target, config)
        else:
            logger.error("Target does not provide source code, address, or bytecode")
            return []
    
    async def _scan_source_files(self, target: Target, config: ScanConfig) -> List[VulnerabilityFinding]:
        """Scan Solidity source files with Mythril
        
        Args:
            target: Target with source code
            config: Scan configuration
            
        Returns:
            List[VulnerabilityFinding]: List of findings
        """
        # Create a temporary directory to save the source files
        temp_dir = tempfile.mkdtemp(prefix="mythril_scan_")
        self.temp_dirs.append(temp_dir)
        
        try:
            # Source code can be a dict of file paths to content or a single string
            if isinstance(target.source_code, dict):
                # Write each source file to the temporary directory
                for filename, content in target.source_code.items():
                    file_path = os.path.join(temp_dir, filename)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write(content)
                
                # Find the main contract file (usually the one with the contract name)
                main_file = next(
                    (f for f in target.source_code.keys() if target.name in f),
                    next(iter(target.source_code.keys()))
                )
                main_file_path = os.path.join(temp_dir, main_file)
            else:
                # Single source file
                main_file = f"{target.name if target.name else 'contract'}.sol"
                main_file_path = os.path.join(temp_dir, main_file)
                with open(main_file_path, 'w') as f:
                    f.write(str(target.source_code))
            
            # Run Mythril on the source code
            return await self._run_mythril_source(main_file_path, target, config)
            
        except Exception as e:
            logger.error(f"Error scanning source files with Mythril: {e}")
            return []
        finally:
            # Clean up
            await self._cleanup_temp_dir(temp_dir)
    
    async def _scan_deployed_contract(self, target: Target, config: ScanConfig) -> List[VulnerabilityFinding]:
        """Scan a deployed contract by its address
        
        Args:
            target: Target with contract address and blockchain
            config: Scan configuration
            
        Returns:
            List[VulnerabilityFinding]: List of findings
        """
        logger.info(f"Scanning deployed contract at {target.identifier} on {target.blockchain}")
        
        try:
            # Output JSON file
            temp_dir = tempfile.mkdtemp(prefix="mythril_address_scan_")
            self.temp_dirs.append(temp_dir)
            output_file = os.path.join(temp_dir, "mythril_results.json")
            
            # Map blockchain name to infura network names
            network_map = {
                "ethereum": "mainnet",
                "ropsten": "ropsten",
                "rinkeby": "rinkeby",
                "kovan": "kovan",
                "goerli": "goerli",
            }
            
            network = network_map.get(target.blockchain.lower(), target.blockchain)
            
            # Build Mythril command for a deployed contract
            cmd = [
                "myth", "analyze",
                "-a", target.identifier,
                "-o", "json",
                "--infura-id", config.custom_options.get("infura_api_key", ""),
                "--max-depth", str(config.max_depth),
                "-t", str(config.timeout),
                "--outform", "json",
                "-o", output_file
            ]
            
            # Add network if specified
            if network:
                cmd.extend(["--network", network])
            
            return await self._run_mythril_command(cmd, output_file, target)
            
        except Exception as e:
            logger.error(f"Error scanning deployed contract with Mythril: {e}")
            return []
    
    async def _scan_bytecode(self, target: Target, config: ScanConfig) -> List[VulnerabilityFinding]:
        """Scan contract bytecode with Mythril
        
        Args:
            target: Target with bytecode
            config: Scan configuration
            
        Returns:
            List[VulnerabilityFinding]: List of findings
        """
        logger.info("Scanning contract bytecode")
        
        try:
            # Output JSON file
            temp_dir = tempfile.mkdtemp(prefix="mythril_bytecode_scan_")
            self.temp_dirs.append(temp_dir)
            
            # Save bytecode to a file
            bytecode_file = os.path.join(temp_dir, "bytecode.hex")
            with open(bytecode_file, 'w') as f:
                f.write(target.bytecode if not target.bytecode.startswith('0x') else target.bytecode[2:])
                
            output_file = os.path.join(temp_dir, "mythril_results.json")
                
            # Build Mythril command for bytecode
            cmd = [
                "myth", "analyze",
                "-c", bytecode_file,
                "-o", "json",
                "--max-depth", str(config.max_depth),
                "-t", str(config.timeout),
                "--outform", "json",
                "-o", output_file
            ]
            
            return await self._run_mythril_command(cmd, output_file, target)
            
        except Exception as e:
            logger.error(f"Error scanning bytecode with Mythril: {e}")
            return []
        finally:
            # Clean up
            await self._cleanup_temp_dir(temp_dir)
    
    async def _run_mythril_source(self, file_path: str, target: Target, config: ScanConfig) -> List[VulnerabilityFinding]:
        """Run Mythril on a Solidity file
        
        Args:
            file_path: Path to the Solidity file
            target: Scan target
            config: Scan configuration
            
        Returns:
            List[VulnerabilityFinding]: List of findings
        """
        # Output JSON file
        output_file = os.path.join(os.path.dirname(file_path), "mythril_results.json")
        
        # Build Mythril command
        cmd = [
            "myth", "analyze", 
            file_path,
            "--solv", config.custom_options.get("solc_version", "0.8.0"),
            "--max-depth", str(config.max_depth),
            "-t", str(config.timeout),
            "--outform", "json",
            "-o", output_file
        ]
        
        # For deep scans, increase the transaction count and state exploration
        if config.scan_type == ScanType.DEEP:
            cmd.extend(["--transaction-count", "5", "--loop-bound", "6"])
            
        return await self._run_mythril_command(cmd, output_file, target)
    
    async def _run_mythril_command(self, cmd: List[str], output_file: str, target: Target) -> List[VulnerabilityFinding]:
        """Execute a Mythril command and parse the results
        
        Args:
            cmd: Mythril command to run
            output_file: Path to the output file
            target: Scan target
            
        Returns:
            List[VulnerabilityFinding]: List of vulnerability findings
        """
        logger.info(f"Running Mythril: {' '.join(cmd)}")
        
        try:
            # Execute Mythril
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""
            
            if stdout_str:
                logger.debug(f"Mythril stdout: {stdout_str}")
            
            # Check for errors
            if proc.returncode != 0 and not os.path.exists(output_file):
                logger.error(f"Mythril failed with return code {proc.returncode}: {stderr_str}")
                return []
            
            # Parse results from the JSON output
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    try:
                        mythril_data = json.load(f)
                        # Convert Mythril findings to our format
                        findings = self._parse_mythril_output(mythril_data, target)
                        logger.info(f"Mythril found {len(findings)} issues")
                        return findings
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse Mythril JSON output: {e}")
                        return []
            else:
                # Check if there's useful information in the stdout/stderr
                if "No issues found" in stdout_str or "No issues found" in stderr_str:
                    logger.info("Mythril completed without finding any issues")
                else:
                    logger.warning(f"Mythril completed but no output file was created")
                return []
                
        except Exception as e:
            logger.error(f"Error running Mythril: {e}")
            return []
    
    def _parse_mythril_output(self, mythril_data: Dict[str, Any], target: Target) -> List[VulnerabilityFinding]:
        """Parse Mythril output into VulnerabilityFinding objects
        
        Args:
            mythril_data: Mythril results data
            target: Scan target
            
        Returns:
            List[VulnerabilityFinding]: List of parsed vulnerability findings
        """
        findings = []
        
        # Process issues
        if isinstance(mythril_data, list):
            issues = mythril_data
        else:
            # Sometimes the output is nested under an "issues" key
            issues = mythril_data.get("issues", [])
        
        for issue in issues:
            # Skip issues without a severity
            if not issue.get("severity"):
                continue
                
            # Map Mythril severity to our severity levels
            severity_str = issue.get("severity", "Medium")
            severity = MYTHRIL_SEVERITY_TO_LEVEL.get(severity_str, VulnerabilityLevel.MEDIUM)
            
            # Generate a unique ID for this finding
            finding_id = f"MYTHRIL-{uuid.uuid4()}"
            
            # Extract location information
            location = issue.get("filename", "unknown")
            if location == "unknown" and isinstance(target.identifier, str):
                location = target.identifier
            
            line_number = None
            if "lineno" in issue:
                line_number = issue["lineno"]
            
            # Get code snippet if available
            snippet = issue.get("code", None)
            
            # Extract confidence (Mythril doesn't provide confidence directly)
            # For now, we'll use a fixed value based on severity
            confidence_map = {
                VulnerabilityLevel.HIGH: 0.8,
                VulnerabilityLevel.MEDIUM: 0.7,
                VulnerabilityLevel.LOW: 0.6,
                VulnerabilityLevel.INFO: 0.5
            }
            confidence = confidence_map.get(severity, 0.5)
            
            # Extract SWC ID if available
            swc_id = None
            if "swc-id" in issue:
                swc_id = f"SWC-{issue['swc-id']}"
            
            # Create finding object
            finding = VulnerabilityFinding(
                id=finding_id,
                vulnerability_type=issue.get("swc-title", issue.get("title", "Unknown Vulnerability")),
                title=issue.get("swc-title", issue.get("title", "Unknown Vulnerability")),
                description=issue.get("description", "No description provided"),
                severity=severity,
                confidence=confidence,
                location=location,
                line_number=line_number,
                snippet=snippet,
                source="mythril",
                cwe_id=swc_id,
                recommendation=issue.get("recommendation", None),
                tags=["dynamic-analysis", "symbolic-execution", "evm", 
                      issue.get("swc-title", "").lower().replace(" ", "-")],
                exploit_scenario=issue.get("exploit_scenario", None),
                metadata={"mythril_raw": issue}
            )
            
            findings.append(finding)
        
        return findings
    
    async def _cleanup_temp_dir(self, temp_dir: str) -> None:
        """Clean up a temporary directory
        
        Args:
            temp_dir: Path to the temporary directory
        """
        if os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
                if temp_dir in self.temp_dirs:
                    self.temp_dirs.remove(temp_dir)
                logger.debug(f"Removed temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary directory {temp_dir}: {e}")
    
    async def cleanup(self) -> None:
        """Clean up resources used by the plugin"""
        await super().cleanup()
        
        # Clean up any remaining temporary directories
        for temp_dir in list(self.temp_dirs):
            await self._cleanup_temp_dir(temp_dir)
