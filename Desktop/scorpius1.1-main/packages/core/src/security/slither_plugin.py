"""Slither scanner plugin for Scorpius Vulnerability Scanner

This module integrates the Slither static analyzer for Solidity smart contracts.
Slither is a static analysis framework that can detect vulnerabilities in
Ethereum smart contracts.
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

logger = logging.getLogger("scorpius.scanners.slither")

# Mapping of Slither detector impact levels to our vulnerability levels
SLITHER_IMPACT_TO_LEVEL = {
    "High": VulnerabilityLevel.HIGH,
    "Medium": VulnerabilityLevel.MEDIUM,
    "Low": VulnerabilityLevel.LOW,
    "Informational": VulnerabilityLevel.INFO,
    "Optimization": VulnerabilityLevel.INFO
}

# Mapping of Slither detector confidence to our confidence score
SLITHER_CONFIDENCE_TO_SCORE = {
    "High": 0.9,
    "Medium": 0.7,
    "Low": 0.4
}


class SlitherPlugin(BaseScannerPlugin):
    """Slither static analysis plugin for smart contracts"""
    
    NAME = "slither"
    DESCRIPTION = "Static analysis of Solidity smart contracts using Slither"
    VERSION = "0.1.0"
    AUTHOR = "Scorpius Team"
    SUPPORTED_SCAN_TYPES = [ScanType.STATIC, ScanType.FULL, ScanType.QUICK]
    DEPENDENCIES = ["slither-analyzer"]
    
    def __init__(self):
        """Initialize the Slither plugin"""
        super().__init__()
        self.temp_dirs = []
        
    async def initialize(self) -> bool:
        """Initialize the Slither plugin
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if self.initialized:
            return True
        
        # Call parent initialization, which checks dependencies
        if not await super().initialize():
            return False
        
        try:
            # Check if Slither is installed and available
            proc = await asyncio.create_subprocess_exec(
                "slither", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                logger.error(f"Slither is not installed or not in PATH")
                return False
                
            # Parse version to ensure compatibility
            version = stdout.decode().strip()
            logger.info(f"Found Slither version: {version}")
            
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Slither plugin: {e}")
            return False
    
    async def _check_dependency(self, dependency: str) -> bool:
        """Check if a specific dependency is available
        
        Args:
            dependency: The dependency to check
            
        Returns:
            bool: True if dependency is available, False otherwise
        """
        if dependency == "slither-analyzer":
            try:
                # Use pip to check if it's installed
                proc = await asyncio.create_subprocess_exec(
                    "pip", "show", "slither-analyzer",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                return proc.returncode == 0
            except Exception:
                return False
                
        return await super()._check_dependency(dependency)
    
    async def scan(self, target: Target, config: ScanConfig) -> List[VulnerabilityFinding]:
        """Perform a security scan using Slither
        
        Args:
            target: Target to scan
            config: Configuration for the scan
            
        Returns:
            List[VulnerabilityFinding]: List of vulnerability findings
        """
        if not self.initialized:
            await self.initialize()
            if not self.initialized:
                logger.error("Cannot perform scan, Slither plugin not initialized")
                return []
        
        logger.info(f"Starting Slither scan for target {target.identifier}")
        
        # There are multiple ways to scan a contract, depending on what's available:
        # 1. Source code in target.source_code
        # 2. Contract address in target.identifier (for deployed contracts)
        # 3. Bytecode in target.bytecode
        
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
        """Scan Solidity source files with Slither
        
        Args:
            target: Target with source code
            config: Scan configuration
            
        Returns:
            List[VulnerabilityFinding]: List of findings
        """
        # Create a temporary directory to save the source files
        temp_dir = tempfile.mkdtemp(prefix="slither_scan_")
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
            
            # Run Slither on the source code
            return await self._run_slither(main_file_path, target, config)
            
        except Exception as e:
            logger.error(f"Error scanning source files with Slither: {e}")
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
            # This would use Slither's ability to analyze a remote contract
            # by fetching the verified source code from Etherscan or similar
            # Not fully implemented here as it requires API keys and network setup
            
            # Example command:
            # slither {target.identifier} --etherscan-apikey {config.custom_options.get('etherscan_api_key')}
            
            # For now, we'll log a warning
            logger.warning("Scanning deployed contracts not fully implemented. Provide source code for best results.")
            return []
            
        except Exception as e:
            logger.error(f"Error scanning deployed contract with Slither: {e}")
            return []
    
    async def _scan_bytecode(self, target: Target, config: ScanConfig) -> List[VulnerabilityFinding]:
        """Scan contract bytecode with Slither
        
        Args:
            target: Target with bytecode
            config: Scan configuration
            
        Returns:
            List[VulnerabilityFinding]: List of findings
        """
        logger.info("Scanning contract bytecode")
        
        try:
            # Slither has limited support for pure bytecode analysis
            # For better results, we should use another tool like Mythril for bytecode
            logger.warning("Slither has limited support for bytecode analysis. Bytecode analysis might not be comprehensive.")
            
            # Not fully implemented here
            return []
            
        except Exception as e:
            logger.error(f"Error scanning bytecode with Slither: {e}")
            return []
    
    async def _run_slither(self, file_path: str, target: Target, config: ScanConfig) -> List[VulnerabilityFinding]:
        """Run Slither on a Solidity file
        
        Args:
            file_path: Path to the Solidity file
            target: Scan target
            config: Scan configuration
            
        Returns:
            List[VulnerabilityFinding]: List of findings
        """
        # Output JSON file
        output_file = os.path.join(os.path.dirname(file_path), "slither_results.json")
        
        # Build Slither command
        cmd = [
            "slither", 
            file_path, 
            "--json", output_file
        ]
        
        # Add configuration options
        detectors_filter = config.custom_options.get("slither_detectors")
        if detectors_filter:
            cmd.extend(["--detect", detectors_filter])
            
        # For limited scans, use custom detector settings if specified
        if config.custom_options.get("quick_scan", False):
            cmd.extend(["--detect", "high"])
        
        logger.info(f"Running Slither: {' '.join(cmd)}")
        
        try:
            # Execute Slither
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            # Check for errors
            if proc.returncode != 0 and not os.path.exists(output_file):
                logger.error(f"Slither failed: {stderr.decode()}")
                return []
            
            # Parse results from the JSON output
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    slither_data = json.load(f)
                
                # Convert Slither findings to our format
                findings = self._parse_slither_output(slither_data, target)
                logger.info(f"Slither found {len(findings)} issues")
                return findings
            else:
                logger.warning("Slither completed but no output file was created")
                return []
                
        except Exception as e:
            logger.error(f"Error running Slither: {e}")
            return []
    
    def _parse_slither_output(self, slither_data: Dict[str, Any], target: Target) -> List[VulnerabilityFinding]:
        """Parse Slither output into VulnerabilityFinding objects
        
        Args:
            slither_data: Slither results data
            target: Scan target
            
        Returns:
            List[VulnerabilityFinding]: List of parsed vulnerability findings
        """
        findings = []
        
        # Process detectors results
        for detector_result in slither_data.get("results", {}).get("detectors", []):
            # Skip results without impact
            if not detector_result.get("impact"):
                continue
                
            # Map Slither severity to our severity levels
            impact = detector_result.get("impact")
            severity = SLITHER_IMPACT_TO_LEVEL.get(impact, VulnerabilityLevel.MEDIUM)
            
            # Map Slither confidence to our confidence score
            confidence_str = detector_result.get("confidence", "Medium")
            confidence = SLITHER_CONFIDENCE_TO_SCORE.get(confidence_str, 0.5)
            
            # Generate a unique ID for this finding
            finding_id = f"SLITHER-{uuid.uuid4()}"
            
            # Extract location information
            location = "unknown"
            line_number = None
            snippet = None
            
            if detector_result.get("elements") and len(detector_result["elements"]) > 0:
                element = detector_result["elements"][0]
                if element.get("source_mapping") and element["source_mapping"].get("filename_absolute"):
                    file_path = element["source_mapping"]["filename_absolute"]
                    location = os.path.basename(file_path)
                    
                    if element["source_mapping"].get("lines") and len(element["source_mapping"]["lines"]) > 0:
                        line_number = element["source_mapping"]["lines"][0]
                        
                # Get code snippet if available
                if element.get("code"):
                    snippet = element["code"]
            
            # Create finding object
            finding = VulnerabilityFinding(
                id=finding_id,
                vulnerability_type=detector_result.get("check", "unknown_vulnerability"),
                title=detector_result.get("check", "Unknown Vulnerability"),
                description=detector_result.get("description", "No description provided"),
                severity=severity,
                confidence=confidence,
                location=location,
                line_number=line_number,
                snippet=snippet,
                source="slither",
                recommendation=detector_result.get("recommendation", None),
                cwe_id=detector_result.get("cwe", None),
                tags=["static-analysis", "solidity", detector_result.get("check", "").lower().replace(" ", "-")],
                metadata={"slither_raw": detector_result}
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
