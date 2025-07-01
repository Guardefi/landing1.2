"""
SARIF Report Writer
===================

Generate SARIF (Static Analysis Results Interchange Format) reports 
for integration with security tools and CI/CD pipelines.
"""

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import BaseReporter, ReportContext


class SARIFReporter(BaseReporter):
    """SARIF v2.1.0 report generator for security tool integration"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        super().__init__(output_dir)
        self.supported_formats = ["sarif"]
        
    async def generate(
        self,
        context: ReportContext,
        output_path: Optional[Path] = None,
        tool_name: str = "Scorpius Security Scanner",
        tool_version: str = "1.0.0",
        **kwargs
    ) -> Path:
        """
        Generate SARIF report.
        
        Args:
            context: Report context with scan data
            output_path: Optional custom output path
            tool_name: Name of the scanning tool
            tool_version: Version of the scanning tool
            **kwargs: Additional options
            
        Returns:
            Path to generated SARIF file
        """
        # Validate context
        errors = await self.validate_context(context)
        if errors:
            raise ValueError(f"Context validation failed: {'; '.join(errors)}")
            
        # Prepare output path
        if not output_path:
            filename = self.get_default_filename(context)
            output_path = self.output_dir / filename
            
        # Build SARIF structure
        sarif_data = self._build_sarif_structure(context, tool_name, tool_version)
        
        # Write SARIF file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sarif_data, f, indent=2, default=self._json_serializer)
            
        return output_path
        
    def _build_sarif_structure(
        self,
        context: ReportContext,
        tool_name: str,
        tool_version: str
    ) -> Dict[str, Any]:
        """Build the complete SARIF v2.1.0 structure"""
        
        return {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                self._build_run(context, tool_name, tool_version)
            ]
        }
        
    def _build_run(
        self,
        context: ReportContext,
        tool_name: str,
        tool_version: str
    ) -> Dict[str, Any]:
        """Build a SARIF run object"""
        
        return {
            "tool": self._build_tool(tool_name, tool_version),
            "artifacts": self._build_artifacts(context),
            "results": self._build_results(context),
            "invocations": self._build_invocations(context),
            "properties": {
                "reportMetadata": context.metadata.to_dict(),
                "summary": context.get_aggregated_stats(),
            }
        }
        
    def _build_tool(self, tool_name: str, tool_version: str) -> Dict[str, Any]:
        """Build SARIF tool object"""
        
        return {
            "driver": {
                "name": tool_name,
                "version": tool_version,
                "informationUri": "https://scorpius.security",
                "organization": "Scorpius Security",
                "shortDescription": {
                    "text": "Smart contract security analysis tool"
                },
                "fullDescription": {
                    "text": "Enterprise-grade smart contract vulnerability scanner and reporting engine"
                },
                "rules": self._build_rules(tool_name)
            }
        }
        
    def _build_rules(self, tool_name: str) -> List[Dict[str, Any]]:
        """Build SARIF rules from vulnerability categories"""
        
        # Define common smart contract vulnerability rules
        rules = [
            {
                "id": "reentrancy",
                "name": "Reentrancy",
                "shortDescription": {
                    "text": "Reentrancy vulnerability"
                },
                "fullDescription": {
                    "text": "Function allows recursive calls that can lead to unexpected behavior and fund drainage"
                },
                "defaultConfiguration": {
                    "level": "error"
                },
                "helpUri": "https://docs.scorpius.security/rules/reentrancy",
                "properties": {
                    "category": "security",
                    "cwe": "CWE-362"
                }
            },
            {
                "id": "access_control",
                "name": "Access Control",
                "shortDescription": {
                    "text": "Access control vulnerability"
                },
                "fullDescription": {
                    "text": "Improper access controls that may allow unauthorized actions"
                },
                "defaultConfiguration": {
                    "level": "error"
                },
                "helpUri": "https://docs.scorpius.security/rules/access-control",
                "properties": {
                    "category": "security",
                    "cwe": "CWE-284"
                }
            },
            {
                "id": "arithmetic",
                "name": "Arithmetic Issues",
                "shortDescription": {
                    "text": "Integer overflow/underflow"
                },
                "fullDescription": {
                    "text": "Arithmetic operations that may result in overflow or underflow"
                },
                "defaultConfiguration": {
                    "level": "warning"
                },
                "helpUri": "https://docs.scorpius.security/rules/arithmetic",
                "properties": {
                    "category": "security",
                    "cwe": "CWE-190"
                }
            },
            {
                "id": "unchecked_calls",
                "name": "Unchecked External Calls",
                "shortDescription": {
                    "text": "Unchecked external call"
                },
                "fullDescription": {
                    "text": "External call return value not checked, may lead to silent failures"
                },
                "defaultConfiguration": {
                    "level": "warning"
                },
                "helpUri": "https://docs.scorpius.security/rules/unchecked-calls",
                "properties": {
                    "category": "security",
                    "cwe": "CWE-252"
                }
            },
            {
                "id": "denial_of_service",
                "name": "Denial of Service",
                "shortDescription": {
                    "text": "Denial of service vulnerability"
                },
                "fullDescription": {
                    "text": "Code patterns that may lead to denial of service attacks"
                },
                "defaultConfiguration": {
                    "level": "warning"
                },
                "helpUri": "https://docs.scorpius.security/rules/dos",
                "properties": {
                    "category": "security",
                    "cwe": "CWE-400"
                }
            }
        ]
        
        return rules
        
    def _build_artifacts(self, context: ReportContext) -> List[Dict[str, Any]]:
        """Build SARIF artifacts (analyzed files)"""
        
        artifacts = []
        artifact_map = {}
        
        for scan in context.scan_results:
            for contract in scan.contracts:
                if contract.name not in artifact_map:
                    artifact = {
                        "location": {
                            "uri": f"contracts/{contract.name}.sol"
                        },
                        "description": {
                            "text": f"Smart contract: {contract.name}"
                        },
                        "properties": {
                            "contractAddress": contract.address,
                            "compilerVersion": contract.compiler_version,
                            "optimizationEnabled": contract.optimization_enabled,
                        }
                    }
                    
                    if contract.source_code:
                        artifact["contents"] = {
                            "text": contract.source_code
                        }
                        
                    artifacts.append(artifact)
                    artifact_map[contract.name] = len(artifacts) - 1
                    
        return artifacts
        
    def _build_results(self, context: ReportContext) -> List[Dict[str, Any]]:
        """Build SARIF results (vulnerabilities)"""
        
        results = []
        
        for scan in context.scan_results:
            for vuln in scan.vulnerabilities:
                result = {
                    "ruleId": vuln.category.value,
                    "ruleIndex": self._get_rule_index(vuln.category.value),
                    "message": {
                        "text": vuln.description
                    },
                    "level": self._severity_to_sarif_level(vuln.severity),
                    "locations": self._build_locations(vuln, scan),
                    "properties": {
                        "riskScore": vuln.risk_score,
                        "confidence": vuln.confidence,
                        "projectName": scan.project_name,
                        "scanId": scan.id,
                        "vulnerabilityId": vuln.id,
                        "category": vuln.category.value,
                        "severity": vuln.severity.value,
                    }
                }
                
                # Add code flows if available
                if vuln.code_snippet:
                    result["codeFlows"] = [{
                        "threadFlows": [{
                            "locations": [{
                                "location": {
                                    "physicalLocation": {
                                        "artifactLocation": {
                                            "uri": f"contracts/{vuln.contract_name or 'unknown'}.sol"
                                        },
                                        "region": {
                                            "startLine": vuln.line_number or 1,
                                            "snippet": {
                                                "text": vuln.code_snippet
                                            }
                                        }
                                    }
                                }
                            }]
                        }]
                    }]
                    
                # Add fixes if recommendation is available
                if vuln.recommendation:
                    result["fixes"] = [{
                        "description": {
                            "text": vuln.recommendation
                        }
                    }]
                    
                # Add related locations
                if vuln.function_name:
                    result["relatedLocations"] = [{
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": f"contracts/{vuln.contract_name or 'unknown'}.sol"
                            },
                            "region": {
                                "startLine": vuln.line_number or 1
                            }
                        },
                        "message": {
                            "text": f"Function: {vuln.function_name}"
                        }
                    }]
                    
                results.append(result)
                
        return results
        
    def _build_locations(self, vuln, scan) -> List[Dict[str, Any]]:
        """Build SARIF location objects for a vulnerability"""
        
        locations = []
        
        location = {
            "physicalLocation": {
                "artifactLocation": {
                    "uri": f"contracts/{vuln.contract_name or 'unknown'}.sol"
                },
                "region": {}
            }
        }
        
        # Add line/column information if available
        if vuln.line_number:
            location["physicalLocation"]["region"]["startLine"] = vuln.line_number
            if vuln.column_number:
                location["physicalLocation"]["region"]["startColumn"] = vuln.column_number
                
        # Add code snippet if available
        if vuln.code_snippet:
            location["physicalLocation"]["region"]["snippet"] = {
                "text": vuln.code_snippet
            }
            
        locations.append(location)
        return locations
        
    def _build_invocations(self, context: ReportContext) -> List[Dict[str, Any]]:
        """Build SARIF invocation objects (scan runs)"""
        
        invocations = []
        
        for scan in context.scan_results:
            invocation = {
                "executionSuccessful": scan.status == "completed",
                "startTimeUtc": scan.created_at.isoformat(),
                "machine": "scorpius-scanner",
                "properties": {
                    "scanId": scan.id,
                    "projectName": scan.project_name,
                    "projectVersion": scan.project_version,
                }
            }
            
            if scan.completed_at:
                invocation["endTimeUtc"] = scan.completed_at.isoformat()
                
            if scan.metrics:
                invocation["properties"]["metrics"] = {
                    "linesAnalyzed": scan.metrics.lines_analyzed,
                    "functionsAnalyzed": scan.metrics.functions_analyzed,
                    "contractsAnalyzed": scan.metrics.contracts_analyzed,
                    "durationSeconds": scan.metrics.duration_seconds,
                }
                
            invocations.append(invocation)
            
        return invocations
        
    def _severity_to_sarif_level(self, severity: str) -> str:
        """Convert vulnerability severity to SARIF level"""
        
        mapping = {
            "critical": "error",
            "high": "error", 
            "medium": "warning",
            "low": "note",
            "info": "note"
        }
        
        return mapping.get(severity.lower(), "warning")
        
    def _get_rule_index(self, category: str) -> int:
        """Get rule index for a category"""
        
        # Map categories to rule indices (based on _build_rules order)
        category_map = {
            "reentrancy": 0,
            "access_control": 1,
            "arithmetic": 2,
            "unchecked_calls": 3,
            "denial_of_service": 4,
        }
        
        return category_map.get(category, 0)
        
    def _json_serializer(self, obj) -> str:
        """Custom JSON serializer for datetime objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)
        
    def get_file_extension(self) -> str:
        """Get file extension for SARIF reports"""
        return "sarif"


class EnhancedSARIFReporter(SARIFReporter):
    """Enhanced SARIF reporter with additional security tool integrations"""
    
    def _build_tool(self, tool_name: str, tool_version: str) -> Dict[str, Any]:
        """Build enhanced SARIF tool object with taxonomies"""
        
        base_tool = super()._build_tool(tool_name, tool_version)
        
        # Add security taxonomies
        base_tool["driver"]["supportedTaxonomies"] = [
            {
                "name": "CWE",
                "index": 0,
                "guid": str(uuid.uuid4())
            },
            {
                "name": "OWASP-Top-10",
                "index": 1,
                "guid": str(uuid.uuid4())
            }
        ]
        
        # Add notifications for scan-level issues
        base_tool["driver"]["notifications"] = [
            {
                "id": "scan-timeout",
                "shortDescription": {
                    "text": "Scan timeout"
                },
                "fullDescription": {
                    "text": "Analysis was terminated due to timeout"
                }
            },
            {
                "id": "parse-error",
                "shortDescription": {
                    "text": "Parse error" 
                },
                "fullDescription": {
                    "text": "Unable to parse contract source code"
                }
            }
        ]
        
        return base_tool
        
    def _build_results(self, context: ReportContext) -> List[Dict[str, Any]]:
        """Build enhanced SARIF results with taxonomies"""
        
        results = super()._build_results(context)
        
        # Enhance results with taxonomy references
        for result in results:
            if "properties" in result:
                props = result["properties"]
                
                # Add CWE mapping
                category = props.get("category", "")
                cwe_id = self._get_cwe_for_category(category)
                if cwe_id:
                    result["taxa"] = [
                        {
                            "toolComponent": {
                                "name": "CWE",
                                "index": 0
                            },
                            "id": cwe_id
                        }
                    ]
                    
        return results
        
    def _get_cwe_for_category(self, category: str) -> Optional[str]:
        """Get CWE ID for vulnerability category"""
        
        cwe_mapping = {
            "reentrancy": "CWE-362",
            "access_control": "CWE-284", 
            "arithmetic": "CWE-190",
            "unchecked_calls": "CWE-252",
            "denial_of_service": "CWE-400",
            "front_running": "CWE-362",
            "time_manipulation": "CWE-829",
            "authorization": "CWE-285",
        }
        
        return cwe_mapping.get(category)

