"""
Scorpius Reporting Service - SARIF Generator
Static Analysis Results Interchange Format (SARIF) report generation
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from uuid import uuid4

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SARIFGenerationError(Exception):
    """SARIF Generation error"""
    pass


class SARIFGenerator:
    """SARIF 2.1.0 compliant report generator"""
    
    def __init__(self):
        self.settings = settings
        self.schema_version = self.settings.SARIF_SCHEMA_VERSION
    
    async def generate_report(
        self,
        scan_results: List[Dict[str, Any]],
        tool_info: Dict[str, Any],
        run_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate SARIF compliant report
        
        Args:
            scan_results: List of scan results
            tool_info: Information about the analysis tool
            run_metadata: Additional run metadata
            
        Returns:
            SARIF report as dictionary
        """
        try:
            # Create SARIF structure
            sarif_report = {
                "version": self.schema_version,
                "$schema": f"https://json.schemastore.org/sarif-{self.schema_version}.json",
                "runs": [
                    await self._create_run(scan_results, tool_info, run_metadata)
                ]
            }
            
            # Validate if enabled
            if self.settings.SARIF_VALIDATION_ENABLED:
                await self._validate_sarif(sarif_report)
            
            logger.info(f"Generated SARIF report with {len(scan_results)} results")
            return sarif_report
            
        except Exception as e:
            logger.error(f"SARIF generation error: {e}")
            raise SARIFGenerationError(f"Failed to generate SARIF: {str(e)}")
    
    async def _create_run(
        self,
        scan_results: List[Dict[str, Any]],
        tool_info: Dict[str, Any],
        run_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create SARIF run object"""
        
        # Create tool object
        tool = {
            "driver": {
                "name": tool_info.get("name", "Unknown Tool"),
                "version": tool_info.get("version", "0.0.0"),
                "informationUri": tool_info.get("url", ""),
                "organization": tool_info.get("organization", ""),
                "rules": await self._extract_rules(scan_results)
            }
        }
        
        # Create run object
        run = {
            "tool": tool,
            "invocation": await self._create_invocation(run_metadata),
            "results": await self._create_results(scan_results),
            "columnKind": "utf16CodeUnits"
        }
        
        # Add run metadata if provided
        if run_metadata:
            run["properties"] = run_metadata
        
        return run
    
    async def _create_invocation(self, run_metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create SARIF invocation object"""
        
        invocation = {
            "executionSuccessful": True,
            "startTimeUtc": datetime.now(timezone.utc).isoformat(),
            "endTimeUtc": datetime.now(timezone.utc).isoformat(),
            "machine": "scorpius-reporting-service"
        }
        
        if run_metadata:
            if "command_line" in run_metadata:
                invocation["commandLine"] = run_metadata["command_line"]
            if "working_directory" in run_metadata:
                invocation["workingDirectory"] = {
                    "uri": run_metadata["working_directory"]
                }
            if "environment_variables" in run_metadata:
                invocation["environmentVariables"] = run_metadata["environment_variables"]
        
        return invocation
    
    async def _extract_rules(self, scan_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract unique rules from scan results"""
        
        rules_dict = {}
        
        for result in scan_results:
            rule_id = result.get("rule_id")
            if rule_id and rule_id not in rules_dict:
                rule = {
                    "id": rule_id,
                    "name": result.get("rule_name", rule_id),
                    "shortDescription": {
                        "text": result.get("rule_description", f"Rule {rule_id}")
                    },
                    "fullDescription": {
                        "text": result.get("rule_full_description", result.get("rule_description", f"Rule {rule_id}"))
                    },
                    "defaultConfiguration": {
                        "level": self._map_level(result.get("level", "warning"))
                    }
                }
                
                # Add additional rule properties
                if "rule_category" in result:
                    rule["properties"] = rule.get("properties", {})
                    rule["properties"]["category"] = result["rule_category"]
                
                if "rule_tags" in result:
                    rule["properties"] = rule.get("properties", {})
                    rule["properties"]["tags"] = result["rule_tags"]
                
                rules_dict[rule_id] = rule
        
        return list(rules_dict.values())
    
    async def _create_results(self, scan_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create SARIF results array"""
        
        sarif_results = []
        
        for result in scan_results:
            sarif_result = {
                "ruleId": result.get("rule_id"),
                "ruleIndex": 0,  # Would need to map to actual rule index
                "level": self._map_level(result.get("level", "warning")),
                "message": {
                    "text": result.get("message", "No message provided")
                },
                "locations": await self._create_locations(result.get("locations", []))
            }
            
            # Add additional properties
            if "properties" in result:
                sarif_result["properties"] = result["properties"]
            
            # Add fingerprints for result tracking
            if "fingerprint" in result:
                sarif_result["fingerprints"] = {
                    "primaryLocationLineHash": result["fingerprint"]
                }
            
            # Add fix suggestions if available
            if "fixes" in result:
                sarif_result["fixes"] = await self._create_fixes(result["fixes"])
            
            # Add code flows if available
            if "code_flows" in result:
                sarif_result["codeFlows"] = await self._create_code_flows(result["code_flows"])
            
            sarif_results.append(sarif_result)
        
        return sarif_results
    
    async def _create_locations(self, locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create SARIF locations array"""
        
        sarif_locations = []
        
        for location in locations:
            sarif_location = {
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": location.get("file_path", "unknown")
                    }
                }
            }
            
            # Add region information if available
            if any(key in location for key in ["line", "column", "start_line", "end_line"]):
                region = {}
                
                if "line" in location:
                    region["startLine"] = location["line"]
                if "column" in location:
                    region["startColumn"] = location["column"]
                if "start_line" in location:
                    region["startLine"] = location["start_line"]
                if "end_line" in location:
                    region["endLine"] = location["end_line"]
                if "start_column" in location:
                    region["startColumn"] = location["start_column"]
                if "end_column" in location:
                    region["endColumn"] = location["end_column"]
                
                sarif_location["physicalLocation"]["region"] = region
            
            # Add context region if available
            if "context" in location:
                sarif_location["physicalLocation"]["contextRegion"] = {
                    "startLine": location["context"].get("start_line", 1),
                    "endLine": location["context"].get("end_line", 1),
                    "snippet": {
                        "text": location["context"].get("text", "")
                    }
                }
            
            sarif_locations.append(sarif_location)
        
        return sarif_locations
    
    async def _create_fixes(self, fixes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create SARIF fixes array"""
        
        sarif_fixes = []
        
        for fix in fixes:
            sarif_fix = {
                "description": {
                    "text": fix.get("description", "Suggested fix")
                },
                "artifactChanges": []
            }
            
            if "changes" in fix:
                for change in fix["changes"]:
                    artifact_change = {
                        "artifactLocation": {
                            "uri": change.get("file_path", "unknown")
                        },
                        "replacements": []
                    }
                    
                    if "replacements" in change:
                        for replacement in change["replacements"]:
                            sarif_replacement = {
                                "deletedRegion": {
                                    "startLine": replacement.get("start_line", 1),
                                    "endLine": replacement.get("end_line", 1),
                                    "startColumn": replacement.get("start_column", 1),
                                    "endColumn": replacement.get("end_column", 1)
                                },
                                "insertedContent": {
                                    "text": replacement.get("new_text", "")
                                }
                            }
                            artifact_change["replacements"].append(sarif_replacement)
                    
                    sarif_fix["artifactChanges"].append(artifact_change)
            
            sarif_fixes.append(sarif_fix)
        
        return sarif_fixes
    
    async def _create_code_flows(self, code_flows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create SARIF code flows array"""
        
        sarif_code_flows = []
        
        for flow in code_flows:
            sarif_flow = {
                "threadFlows": []
            }
            
            if "thread_flows" in flow:
                for thread_flow in flow["thread_flows"]:
                    sarif_thread_flow = {
                        "locations": []
                    }
                    
                    if "locations" in thread_flow:
                        for location in thread_flow["locations"]:
                            sarif_location = {
                                "location": (await self._create_locations([location]))[0],
                                "executionOrder": location.get("execution_order", 0)
                            }
                            
                            if "message" in location:
                                sarif_location["message"] = {
                                    "text": location["message"]
                                }
                            
                            sarif_thread_flow["locations"].append(sarif_location)
                    
                    sarif_flow["threadFlows"].append(sarif_thread_flow)
            
            sarif_code_flows.append(sarif_flow)
        
        return sarif_code_flows
    
    def _map_level(self, level: str) -> str:
        """Map severity level to SARIF level"""
        
        level_mapping = {
            "error": "error",
            "warning": "warning",
            "info": "note",
            "note": "note",
            "critical": "error",
            "high": "error",
            "medium": "warning",
            "low": "note"
        }
        
        return level_mapping.get(level.lower(), "warning")
    
    async def _validate_sarif(self, sarif_report: Dict[str, Any]) -> bool:
        """Validate SARIF report structure"""
        
        try:
            # Basic structure validation
            required_fields = ["version", "runs"]
            for field in required_fields:
                if field not in sarif_report:
                    raise SARIFGenerationError(f"Missing required field: {field}")
            
            # Validate runs
            if not isinstance(sarif_report["runs"], list) or len(sarif_report["runs"]) == 0:
                raise SARIFGenerationError("SARIF report must contain at least one run")
            
            for run in sarif_report["runs"]:
                if "tool" not in run:
                    raise SARIFGenerationError("Run must contain tool information")
                
                if "results" not in run:
                    raise SARIFGenerationError("Run must contain results")
            
            logger.info("SARIF validation passed")
            return True
            
        except Exception as e:
            logger.error(f"SARIF validation failed: {e}")
            raise SARIFGenerationError(f"SARIF validation failed: {str(e)}")
    
    def get_schema_version(self) -> str:
        """Get SARIF schema version"""
        return self.schema_version
    
    async def convert_to_html(self, sarif_report: Dict[str, Any]) -> str:
        """Convert SARIF report to HTML format"""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SARIF Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .result {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .error {{ border-left: 5px solid #d32f2f; }}
                .warning {{ border-left: 5px solid #f57c00; }}
                .note {{ border-left: 5px solid #1976d2; }}
                .location {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; border-radius: 3px; }}
                .code {{ background-color: #f0f0f0; padding: 10px; font-family: monospace; white-space: pre; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>SARIF Report</h1>
                <p>Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p>Schema Version: {sarif_report.get('version', 'Unknown')}</p>
            </div>
        """
        
        for run in sarif_report.get("runs", []):
            tool_name = run.get("tool", {}).get("driver", {}).get("name", "Unknown Tool")
            html_content += f"<h2>Tool: {tool_name}</h2>"
            
            for result in run.get("results", []):
                level = result.get("level", "warning")
                rule_id = result.get("ruleId", "unknown")
                message = result.get("message", {}).get("text", "No message")
                
                html_content += f"""
                <div class="result {level}">
                    <h3>{rule_id} ({level.upper()})</h3>
                    <p>{message}</p>
                """
                
                for location in result.get("locations", []):
                    physical_location = location.get("physicalLocation", {})
                    artifact_location = physical_location.get("artifactLocation", {})
                    region = physical_location.get("region", {})
                    
                    file_path = artifact_location.get("uri", "unknown")
                    start_line = region.get("startLine", "unknown")
                    
                    html_content += f"""
                    <div class="location">
                        <strong>File:</strong> {file_path}<br>
                        <strong>Line:</strong> {start_line}
                    </div>
                    """
                
                html_content += "</div>"
        
        html_content += """
        </body>
        </html>
        """
        
        return html_content
