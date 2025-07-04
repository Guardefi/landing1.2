"""
JSON Report Writer
==================

Generate structured JSON reports for programmatic consumption and API integration.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import BaseReporter, ReportContext


class JSONReporter(BaseReporter):
    """JSON report generator for structured data output"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        super().__init__(output_dir)
        self.supported_formats = ["json"]
        
    async def generate(
        self,
        context: ReportContext,
        output_path: Optional[Path] = None,
        indent: int = 2,
        include_metadata: bool = True,
        include_raw_data: bool = False,
        **kwargs
    ) -> Path:
        """
        Generate JSON report.
        
        Args:
            context: Report context with scan data
            output_path: Optional custom output path
            indent: JSON indentation level
            include_metadata: Whether to include report metadata
            include_raw_data: Whether to include complete raw scan data
            **kwargs: Additional options
            
        Returns:
            Path to generated JSON file
        """
        # Validate context
        errors = await self.validate_context(context)
        if errors:
            raise ValueError(f"Context validation failed: {'; '.join(errors)}")
            
        # Prepare output path
        if not output_path:
            filename = self.get_default_filename(context)
            output_path = self.output_dir / filename
            
        # Build JSON structure
        json_data = self._build_json_structure(
            context, include_metadata, include_raw_data
        )
        
        # Write JSON file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=indent, default=self._json_serializer, ensure_ascii=False)
            
        return output_path
        
    def _build_json_structure(
        self,
        context: ReportContext,
        include_metadata: bool,
        include_raw_data: bool
    ) -> Dict[str, Any]:
        """Build the complete JSON structure"""
        
        # Get aggregated statistics
        stats = context.get_aggregated_stats()
        
        # Base structure
        json_data = {
            "report_type": "smart_contract_security",
            "schema_version": "1.0",
            "generated_at": datetime.utcnow().isoformat(),
            "summary": self._build_summary_section(context, stats),
            "vulnerabilities": self._build_vulnerabilities_section(context),
            "scans": self._build_scans_section(context),
        }
        
        # Add metadata if requested
        if include_metadata:
            json_data["metadata"] = context.metadata.to_dict()
            
        # Add raw data if requested
        if include_raw_data:
            json_data["raw_scan_data"] = [
                scan.dict() for scan in context.scan_results
            ]
            
        # Add sections if any
        if context.sections:
            json_data["sections"] = [
                section.to_dict() for section in context.sections
            ]
            
        # Add charts data
        json_data["charts"] = self.prepare_charts_data(context)
        
        return json_data
        
    def _build_summary_section(self, context: ReportContext, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Build the summary section"""
        
        risk_assessments = []
        for scan in context.scan_results:
            risk_summary = scan.get_risk_summary()
            risk_assessments.append({
                "project_name": scan.project_name,
                "overall_risk": risk_summary["overall_risk"],
                "risk_score": risk_summary["risk_score"],
                "recommendation": risk_summary["recommendation"],
                "total_vulnerabilities": risk_summary["total_vulnerabilities"]
            })
            
        return {
            "total_scans": stats.get("total_scans", 0),
            "total_contracts": stats.get("total_contracts", 0),
            "total_vulnerabilities": stats.get("total_issues", 0),
            "severity_distribution": {
                "critical": stats.get("critical_issues", 0),
                "high": stats.get("high_issues", 0),
                "medium": stats.get("medium_issues", 0),
                "low": stats.get("low_issues", 0),
                "info": stats.get("info_issues", 0),
            },
            "projects": stats.get("projects", []),
            "scan_date_range": {
                "earliest": min(stats.get("scan_dates", [datetime.utcnow()])).isoformat(),
                "latest": max(stats.get("scan_dates", [datetime.utcnow()])).isoformat(),
            },
            "risk_assessments": risk_assessments,
        }
        
    def _build_vulnerabilities_section(self, context: ReportContext) -> List[Dict[str, Any]]:
        """Build the vulnerabilities section with enriched data"""
        
        vulnerabilities = []
        
        for scan in context.scan_results:
            for vuln in scan.vulnerabilities:
                vuln_data = vuln.dict()
                
                # Add scan context
                vuln_data["scan_context"] = {
                    "project_name": scan.project_name,
                    "scan_id": scan.id,
                    "scan_date": scan.created_at.isoformat(),
                }
                
                # Add computed fields
                vuln_data["computed"] = {
                    "risk_level": self._categorize_risk_score(vuln.risk_score),
                    "priority": self._calculate_priority(vuln),
                    "tags": self._generate_tags(vuln),
                }
                
                vulnerabilities.append(vuln_data)
                
        # Sort by risk score (descending)
        vulnerabilities.sort(key=lambda x: x.get("risk_score", 0), reverse=True)
        
        return vulnerabilities
        
    def _build_scans_section(self, context: ReportContext) -> List[Dict[str, Any]]:
        """Build the scans summary section"""
        
        scans = []
        
        for scan in context.scan_results:
            scan_data = {
                "id": scan.id,
                "project_name": scan.project_name,
                "project_version": scan.project_version,
                "status": scan.status,
                "created_at": scan.created_at.isoformat(),
                "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
                "contracts": [
                    {
                        "name": contract.name,
                        "address": contract.address,
                        "compiler_version": contract.compiler_version,
                        "optimization_enabled": contract.optimization_enabled,
                    }
                    for contract in scan.contracts
                ],
                "summary": {
                    "total_vulnerabilities": scan.total_issues,
                    "critical": scan.critical_issues,
                    "high": scan.high_issues,
                    "medium": scan.medium_issues,
                    "low": scan.low_issues,
                    "info": scan.info_issues,
                },
                "risk_assessment": scan.get_risk_summary(),
                "metrics": scan.metrics.dict() if scan.metrics else None,
            }
            
            scans.append(scan_data)
            
        return scans
        
    def _categorize_risk_score(self, risk_score: float) -> str:
        """Categorize numerical risk score into levels"""
        if risk_score >= 8.0:
            return "critical"
        elif risk_score >= 6.0:
            return "high"
        elif risk_score >= 4.0:
            return "medium"
        elif risk_score >= 2.0:
            return "low"
        else:
            return "minimal"
            
    def _calculate_priority(self, vuln) -> str:
        """Calculate vulnerability remediation priority"""
        if vuln.severity in ["critical"] or vuln.risk_score >= 8.0:
            return "immediate"
        elif vuln.severity in ["high"] or vuln.risk_score >= 6.0:
            return "high"
        elif vuln.severity in ["medium"] or vuln.risk_score >= 4.0:
            return "medium"
        else:
            return "low"
            
    def _generate_tags(self, vuln) -> List[str]:
        """Generate tags for vulnerability classification"""
        tags = []
        
        # Add severity tag
        tags.append(f"severity:{vuln.severity}")
        
        # Add category tag
        tags.append(f"category:{vuln.category}")
        
        # Add confidence level tag
        if vuln.confidence >= 0.9:
            tags.append("confidence:high")
        elif vuln.confidence >= 0.7:
            tags.append("confidence:medium")
        else:
            tags.append("confidence:low")
            
        # Add priority tag
        priority = self._calculate_priority(vuln)
        tags.append(f"priority:{priority}")
        
        # Add location tags if available
        if vuln.function_name:
            tags.append(f"function:{vuln.function_name}")
            
        # Add CWE tag if available
        if vuln.cwe_id:
            tags.append(f"cwe:{vuln.cwe_id}")
            
        return tags
        
    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for complex objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
            
    def get_file_extension(self) -> str:
        """Get file extension for JSON reports"""
        return "json"


class CompactJSONReporter(JSONReporter):
    """Compact JSON reporter for minimal file size"""
    
    async def generate(
        self,
        context: ReportContext,
        output_path: Optional[Path] = None,
        **kwargs
    ) -> Path:
        """Generate compact JSON with minimal data"""
        
        # Override defaults for compact format
        kwargs.update({
            "indent": None,  # No indentation
            "include_metadata": False,
            "include_raw_data": False,
        })
        
        return await super().generate(context, output_path, **kwargs)
        
    def _build_json_structure(
        self,
        context: ReportContext,
        include_metadata: bool,
        include_raw_data: bool
    ) -> Dict[str, Any]:
        """Build compact JSON structure"""
        
        stats = context.get_aggregated_stats()
        
        # Minimal structure
        return {
            "type": "security_report",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "scans": stats.get("total_scans", 0),
                "issues": {
                    "total": stats.get("total_issues", 0),
                    "critical": stats.get("critical_issues", 0),
                    "high": stats.get("high_issues", 0),
                    "medium": stats.get("medium_issues", 0),
                    "low": stats.get("low_issues", 0),
                }
            },
            "findings": [
                {
                    "id": vuln.id,
                    "title": vuln.title,
                    "severity": vuln.severity,
                    "score": vuln.risk_score,
                    "project": scan.project_name,
                    "function": vuln.function_name,
                    "line": vuln.line_number,
                }
                for scan in context.scan_results
                for vuln in scan.vulnerabilities
            ]
        }


class APIResponseJSONReporter(JSONReporter):
    """JSON reporter optimized for API responses"""
    
    def _build_json_structure(
        self,
        context: ReportContext,
        include_metadata: bool,
        include_raw_data: bool
    ) -> Dict[str, Any]:
        """Build API-optimized JSON structure"""
        
        base_structure = super()._build_json_structure(
            context, include_metadata, include_raw_data
        )
        
        # Add API-specific fields
        base_structure.update({
            "api_version": "v1",
            "pagination": {
                "page": 1,
                "per_page": len(context.scan_results),
                "total": len(context.scan_results),
            },
            "links": {
                "self": f"/api/v1/reports/{context.metadata.title}",
                "download": f"/api/v1/reports/{context.metadata.title}/download",
            },
            "status": "completed",
        })
        
        return base_structure

