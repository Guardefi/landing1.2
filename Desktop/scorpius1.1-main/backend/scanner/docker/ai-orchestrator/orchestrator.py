#!/usr/bin/env python3
"""
Scanner Orchestrator - Coordinates all scanner plugins and AI analysis
"""

import asyncio
import json
import logging
import os
import tempfile
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

import aiohttp

logger = logging.getLogger("scorpius.orchestrator")


class ScannerOrchestrator:
    """Orchestrates multiple scanner plugins and AI analysis"""
    
    def __init__(self, scanner_endpoints: Dict[str, str], ai_analyzer: Optional[Any] = None):
        """
        Initialize the orchestrator
        
        Args:
            scanner_endpoints: Dictionary mapping scanner names to their endpoints
            ai_analyzer: AI analyzer instance
        """
        self.scanner_endpoints = scanner_endpoints
        self.ai_analyzer = ai_analyzer
        self.session = None
        self.scanner_status = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def is_healthy(self) -> bool:
        """Check if orchestrator is healthy"""
        return self.ai_analyzer is not None and len(self.scanner_endpoints) > 0
    
    async def get_connected_scanners(self) -> List[str]:
        """Get list of connected scanners"""
        connected = []
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        for scanner_name, endpoint in self.scanner_endpoints.items():
            try:
                async with self.session.get(f"{endpoint}/health", timeout=5) as response:
                    if response.status == 200:
                        connected.append(scanner_name)
                        self.scanner_status[scanner_name] = "healthy"
                    else:
                        self.scanner_status[scanner_name] = "unhealthy"
            except Exception as e:
                logger.warning(f"Scanner {scanner_name} health check failed: {e}")
                self.scanner_status[scanner_name] = "unreachable"
        
        return connected
    
    async def run_comprehensive_scan(
        self,
        target_path: str,
        options: Dict[str, Any],
        scan_id: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive scan across all scanners with AI analysis
        
        Args:
            target_path: Path to target file
            options: Scan options
            scan_id: Unique scan identifier
            progress_callback: Optional callback for progress updates
            
        Returns:
            Comprehensive scan results
        """
        logger.info(f"Starting comprehensive scan {scan_id} for {target_path}")
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        # Initialize results structure
        results = {
            "scan_id": scan_id,
            "target_path": target_path,
            "slither_findings": [],
            "mythril_findings": [],
            "manticore_findings": [],
            "simulation_results": {},
            "exploit_simulations": [],
            "attack_vectors": [],
            "ai_findings": [],
            "risk_assessment": {},
            "exploit_prediction": {},
            "comprehensive_report": {},
            "recommendations": [],
            "scan_metadata": {
                "start_time": datetime.now().isoformat(),
                "scanners_used": [],
                "ai_analysis_enabled": self.ai_analyzer is not None,
                "simulation_enabled": "simulation" in self.scanner_endpoints,
                "total_findings": 0
            }
        }
        
        try:
            # Step 1: Run all scanner plugins in parallel
            if progress_callback:
                progress_callback(10, "starting_scanner_plugins")
            
            scanner_tasks = []
            for scanner_name, endpoint in self.scanner_endpoints.items():
                if self.scanner_status.get(scanner_name, "unknown") != "unreachable":
                    task = asyncio.create_task(
                        self._run_scanner_plugin(scanner_name, endpoint, target_path, options)
                    )
                    scanner_tasks.append((scanner_name, task))
            
            # Wait for all scanner tasks to complete
            scanner_results = {}
            for scanner_name, task in scanner_tasks:
                try:
                    if progress_callback:
                        progress_callback(20 + (len(scanner_results) * 15), f"running_{scanner_name}")
                    
                    result = await task
                    scanner_results[scanner_name] = result
                    results["scan_metadata"]["scanners_used"].append(scanner_name)
                    logger.info(f"Scanner {scanner_name} completed successfully")
                    
                except Exception as e:
                    logger.error(f"Scanner {scanner_name} failed: {e}")
                    scanner_results[scanner_name] = {"error": str(e), "findings": []}
            
            # Step 2: Process scanner results
            if progress_callback:
                progress_callback(65, "processing_scanner_results")
            
            # Extract findings from each scanner
            results["slither_findings"] = scanner_results.get("slither", {}).get("findings", [])
            results["mythril_findings"] = scanner_results.get("mythril", {}).get("findings", [])
            results["manticore_findings"] = scanner_results.get("manticore", {}).get("findings", [])
            
            # Extract simulation results
            if "simulation" in scanner_results:
                simulation_data = scanner_results["simulation"]
                results["simulation_results"] = simulation_data.get("simulation_results", {})
                results["exploit_simulations"] = simulation_data.get("exploit_simulations", [])
                results["attack_vectors"] = simulation_data.get("attack_vectors", [])
                logger.info("Simulation results processed successfully")
            
            # Step 3: AI Analysis
            if self.ai_analyzer and progress_callback:
                progress_callback(70, "ai_analysis")
            
            if self.ai_analyzer:
                try:
                    # Read source code
                    source_code = None
                    if os.path.exists(target_path):
                        with open(target_path, 'r') as f:
                            source_code = f.read()
                    
                    # Run AI analysis with scanner results as context
                    ai_results = await self.ai_analyzer.analyze_with_scanner_context(
                        source_code=source_code,
                        target_path=target_path,
                        scanner_results=scanner_results,
                        options=options
                    )
                    
                    results["ai_findings"] = ai_results.get("findings", [])
                    results["risk_assessment"] = ai_results.get("risk_assessment", {})
                    results["exploit_prediction"] = ai_results.get("exploit_prediction", {})
                    results["recommendations"] = ai_results.get("recommendations", [])
                    
                    logger.info("AI analysis completed successfully")
                    
                except Exception as e:
                    logger.error(f"AI analysis failed: {e}")
                    results["ai_findings"] = []
                    results["risk_assessment"] = {"error": str(e)}
                    results["exploit_prediction"] = {"error": str(e)}
            
            # Step 4: Generate comprehensive report
            if progress_callback:
                progress_callback(90, "generating_report")
            
            results["comprehensive_report"] = self._generate_comprehensive_report(
                results, scanner_results
            )
            
            # Step 5: Calculate final metrics
            all_findings = (
                results["slither_findings"] +
                results["mythril_findings"] +
                results["manticore_findings"] +
                results["ai_findings"]
            )
            
            results["scan_metadata"]["total_findings"] = len(all_findings)
            results["scan_metadata"]["end_time"] = datetime.now().isoformat()
            results["scan_metadata"]["status"] = "completed"
            
            if progress_callback:
                progress_callback(100, "completed")
            
            logger.info(f"Comprehensive scan {scan_id} completed with {len(all_findings)} total findings")
            
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive scan {scan_id} failed: {e}")
            results["scan_metadata"]["status"] = "error"
            results["scan_metadata"]["error"] = str(e)
            results["scan_metadata"]["end_time"] = datetime.now().isoformat()
            raise
    
    async def _run_scanner_plugin(
        self,
        scanner_name: str,
        endpoint: str,
        target_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a single scanner plugin"""
        try:
            logger.info(f"Running scanner {scanner_name} at {endpoint}")
            
            # Upload file to scanner
            with open(target_path, 'rb') as f:
                file_content = f.read()
            
            # Create multipart form data
            form_data = aiohttp.FormData()
            form_data.add_field('file', file_content, filename=os.path.basename(target_path))
            form_data.add_field('options', json.dumps(options))
            
            # Start scan
            async with self.session.post(
                f"{endpoint}/scan/upload",
                data=form_data,
                timeout=30
            ) as response:
                if response.status != 200:
                    raise Exception(f"Failed to start scan: {response.status}")
                
                scan_response = await response.json()
                scan_id = scan_response["scan_id"]
            
            # Poll for results
            max_wait_time = 300  # 5 minutes
            poll_interval = 2
            waited = 0
            
            while waited < max_wait_time:
                await asyncio.sleep(poll_interval)
                waited += poll_interval
                
                try:
                    async with self.session.get(
                        f"{endpoint}/scan/{scan_id}/results",
                        timeout=10
                    ) as response:
                        if response.status == 200:
                            results = await response.json()
                            return {
                                "scanner": scanner_name,
                                "scan_id": scan_id,
                                "findings": results.get("findings", []),
                                "metadata": results.get("metadata", {})
                            }
                        elif response.status == 202:
                            # Still processing
                            continue
                        else:
                            raise Exception(f"Scanner returned error: {response.status}")
                            
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.warning(f"Error polling scanner {scanner_name}: {e}")
                    continue
            
            raise Exception(f"Scanner {scanner_name} timed out after {max_wait_time} seconds")
            
        except Exception as e:
            logger.error(f"Scanner {scanner_name} failed: {e}")
            return {
                "scanner": scanner_name,
                "error": str(e),
                "findings": []
            }
    
    def _generate_comprehensive_report(
        self,
        results: Dict[str, Any],
        scanner_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        all_findings = (
            results["slither_findings"] +
            results["mythril_findings"] +
            results["manticore_findings"] +
            results["ai_findings"]
        )
        
        # Categorize findings by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        vulnerability_types = {}
        
        for finding in all_findings:
            severity = finding.get("severity", "unknown").lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
            
            vuln_type = finding.get("category", "unknown")
            vulnerability_types[vuln_type] = vulnerability_types.get(vuln_type, 0) + 1
        
        # Calculate overall risk score
        risk_score = (
            severity_counts["critical"] * 10 +
            severity_counts["high"] * 7 +
            severity_counts["medium"] * 4 +
            severity_counts["low"] * 2 +
            severity_counts["info"] * 1
        )
        
        # Generate security grade
        if risk_score == 0:
            security_grade = "A+"
        elif risk_score <= 5:
            security_grade = "A"
        elif risk_score <= 15:
            security_grade = "B"
        elif risk_score <= 30:
            security_grade = "C"
        elif risk_score <= 50:
            security_grade = "D"
        else:
            security_grade = "F"
        
        return {
            "overall_risk_score": risk_score,
            "security_grade": security_grade,
            "total_findings": len(all_findings),
            "severity_distribution": severity_counts,
            "vulnerability_types": vulnerability_types,
            "scanner_coverage": {
                "slither": len(results["slither_findings"]),
                "mythril": len(results["mythril_findings"]),
                "manticore": len(results["manticore_findings"]),
                "ai_analysis": len(results["ai_findings"])
            },
            "unique_vulnerabilities": len(set(
                f"{finding.get('category', 'unknown')}-{finding.get('location', {}).get('line', 0)}"
                for finding in all_findings
            )),
            "confidence_score": self._calculate_confidence_score(all_findings),
            "priority_findings": self._get_priority_findings(all_findings),
            "false_positive_likelihood": self._estimate_false_positives(all_findings),
            "remediation_priority": self._prioritize_remediation(all_findings)
        }
    
    def _calculate_confidence_score(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score for findings"""
        if not findings:
            return 0.0
        
        total_confidence = sum(
            finding.get("confidence", 0.5) for finding in findings
        )
        return total_confidence / len(findings)
    
    def _get_priority_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get high priority findings that need immediate attention"""
        priority_findings = []
        
        for finding in findings:
            severity = finding.get("severity", "").lower()
            confidence = finding.get("confidence", 0.0)
            
            if severity in ["critical", "high"] and confidence > 0.7:
                priority_findings.append({
                    "id": finding.get("id", "unknown"),
                    "title": finding.get("title", "Unknown"),
                    "severity": severity,
                    "confidence": confidence,
                    "location": finding.get("location", {})
                })
        
        # Sort by severity and confidence
        priority_findings.sort(
            key=lambda x: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(x["severity"], 0),
                x["confidence"]
            ),
            reverse=True
        )
        
        return priority_findings[:10]  # Top 10 priority findings
    
    def _estimate_false_positives(self, findings: List[Dict[str, Any]]) -> float:
        """Estimate false positive rate"""
        if not findings:
            return 0.0
        
        low_confidence_count = sum(
            1 for finding in findings 
            if finding.get("confidence", 1.0) < 0.6
        )
        
        return low_confidence_count / len(findings)
    
    def _prioritize_remediation(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Prioritize remediation actions"""
        remediation_actions = []
        
        # Group findings by category
        categories = {}
        for finding in findings:
            category = finding.get("category", "unknown")
            if category not in categories:
                categories[category] = []
            categories[category].append(finding)
        
        # Prioritize based on severity and count
        for category, category_findings in categories.items():
            critical_count = sum(
                1 for f in category_findings 
                if f.get("severity", "").lower() == "critical"
            )
            high_count = sum(
                1 for f in category_findings 
                if f.get("severity", "").lower() == "high"
            )
            
            if critical_count > 0:
                remediation_actions.append(f"URGENT: Address {critical_count} critical {category} vulnerabilities")
            elif high_count > 0:
                remediation_actions.append(f"HIGH: Fix {high_count} high-severity {category} issues")
        
        return remediation_actions[:5]  # Top 5 remediation actions 