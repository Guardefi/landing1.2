"""
Report Diff Engine
==================

Compare and analyze differences between security scan results.
"""

import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from models import ScanResult, VulnerabilityFinding


@dataclass
class VulnerabilityDiff:
    """Represents the difference for a single vulnerability"""
    vuln_id: str
    status: str  # 'added', 'removed', 'modified', 'unchanged'
    base_vuln: Optional[VulnerabilityFinding] = None
    compare_vuln: Optional[VulnerabilityFinding] = None
    changes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.changes is None:
            self.changes = {}


@dataclass 
class ScanDiff:
    """Represents the complete difference between two scans"""
    base_scan_id: str
    compare_scan_id: str
    base_project: str
    compare_project: str
    diff_timestamp: datetime
    
    # Summary statistics
    vulnerabilities_added: int = 0
    vulnerabilities_removed: int = 0
    vulnerabilities_modified: int = 0
    vulnerabilities_unchanged: int = 0
    
    # Detailed changes
    added_vulnerabilities: List[VulnerabilityFinding] = None
    removed_vulnerabilities: List[VulnerabilityFinding] = None
    modified_vulnerabilities: List[VulnerabilityDiff] = None
    unchanged_vulnerabilities: List[VulnerabilityFinding] = None
    
    # Severity changes
    severity_changes: Dict[str, Dict[str, int]] = None
    
    # Risk score changes
    risk_score_delta: float = 0.0
    
    def __post_init__(self):
        if self.added_vulnerabilities is None:
            self.added_vulnerabilities = []
        if self.removed_vulnerabilities is None:
            self.removed_vulnerabilities = []
        if self.modified_vulnerabilities is None:
            self.modified_vulnerabilities = []
        if self.unchanged_vulnerabilities is None:
            self.unchanged_vulnerabilities = []
        if self.severity_changes is None:
            self.severity_changes = {}


class ReportDiffEngine:
    """Engine for comparing and analyzing differences between scan results"""
    
    def __init__(self):
        self.similarity_threshold = 0.8  # Threshold for considering vulnerabilities similar
        
    async def compare_scans(
        self,
        base_scan: ScanResult,
        compare_scan: ScanResult,
        detailed: bool = True
    ) -> ScanDiff:
        """
        Compare two scan results and generate a comprehensive diff.
        
        Args:
            base_scan: Base scan result for comparison
            compare_scan: Scan result to compare against base
            detailed: Whether to include detailed change analysis
            
        Returns:
            ScanDiff object containing all differences
        """
        
        diff = ScanDiff(
            base_scan_id=base_scan.id,
            compare_scan_id=compare_scan.id,
            base_project=base_scan.project_name,
            compare_project=compare_scan.project_name,
            diff_timestamp=datetime.utcnow()
        )
        
        # Create vulnerability mappings for efficient comparison
        base_vulns = {self._generate_vuln_key(v): v for v in base_scan.vulnerabilities}
        compare_vulns = {self._generate_vuln_key(v): v for v in compare_scan.vulnerabilities}
        
        base_keys = set(base_vulns.keys())
        compare_keys = set(compare_vulns.keys())
        
        # Find exact matches first
        exact_matches = base_keys & compare_keys
        base_unmatched = base_keys - compare_keys
        compare_unmatched = compare_keys - base_keys
        
        # Handle exact matches (potentially modified)
        for key in exact_matches:
            base_vuln = base_vulns[key]
            compare_vuln = compare_vulns[key]
            
            if detailed:
                vuln_diff = self._compare_vulnerabilities(base_vuln, compare_vuln)
                if vuln_diff.status == 'modified':
                    diff.modified_vulnerabilities.append(vuln_diff)
                    diff.vulnerabilities_modified += 1
                else:
                    diff.unchanged_vulnerabilities.append(base_vuln)
                    diff.vulnerabilities_unchanged += 1
            else:
                # Quick comparison for unchanged detection
                if self._vulnerabilities_equal(base_vuln, compare_vuln):
                    diff.unchanged_vulnerabilities.append(base_vuln)
                    diff.vulnerabilities_unchanged += 1
                else:
                    diff.vulnerabilities_modified += 1
        
        # Handle fuzzy matching for remaining vulnerabilities
        if detailed and (base_unmatched or compare_unmatched):
            fuzzy_matches = self._find_fuzzy_matches(
                [base_vulns[k] for k in base_unmatched],
                [compare_vulns[k] for k in compare_unmatched]
            )
            
            matched_base = set()
            matched_compare = set()
            
            for base_vuln, compare_vuln, similarity in fuzzy_matches:
                if similarity >= self.similarity_threshold:
                    vuln_diff = self._compare_vulnerabilities(base_vuln, compare_vuln)
                    vuln_diff.changes['similarity_score'] = similarity
                    diff.modified_vulnerabilities.append(vuln_diff)
                    diff.vulnerabilities_modified += 1
                    
                    matched_base.add(self._generate_vuln_key(base_vuln))
                    matched_compare.add(self._generate_vuln_key(compare_vuln))
            
            # Update unmatched sets
            base_unmatched -= matched_base
            compare_unmatched -= matched_compare
        
        # Handle truly added and removed vulnerabilities
        for key in base_unmatched:
            diff.removed_vulnerabilities.append(base_vulns[key])
            diff.vulnerabilities_removed += 1
            
        for key in compare_unmatched:
            diff.added_vulnerabilities.append(compare_vulns[key])
            diff.vulnerabilities_added += 1
        
        # Calculate severity changes
        diff.severity_changes = self._calculate_severity_changes(base_scan, compare_scan)
        
        # Calculate risk score delta
        base_risk = base_scan.get_risk_summary()["risk_score"]
        compare_risk = compare_scan.get_risk_summary()["risk_score"]
        diff.risk_score_delta = compare_risk - base_risk
        
        return diff
    
    def _generate_vuln_key(self, vuln: VulnerabilityFinding) -> str:
        """Generate a unique key for vulnerability matching"""
        
        # Use title, category, and function for matching
        key_components = [
            vuln.title.lower().strip(),
            vuln.category.value,
            vuln.function_name or "",
            vuln.contract_name or "",
        ]
        
        key_string = "|".join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _vulnerabilities_equal(self, vuln1: VulnerabilityFinding, vuln2: VulnerabilityFinding) -> bool:
        """Check if two vulnerabilities are exactly equal"""
        
        # Compare key fields
        return (
            vuln1.title == vuln2.title and
            vuln1.description == vuln2.description and
            vuln1.severity == vuln2.severity and
            vuln1.category == vuln2.category and
            vuln1.function_name == vuln2.function_name and
            vuln1.contract_name == vuln2.contract_name and
            vuln1.line_number == vuln2.line_number and
            abs(vuln1.risk_score - vuln2.risk_score) < 0.1
        )
    
    def _compare_vulnerabilities(
        self, 
        base_vuln: VulnerabilityFinding, 
        compare_vuln: VulnerabilityFinding
    ) -> VulnerabilityDiff:
        """Compare two vulnerabilities and identify changes"""
        
        changes = {}
        
        # Check for changes in key fields
        if base_vuln.title != compare_vuln.title:
            changes['title'] = {'from': base_vuln.title, 'to': compare_vuln.title}
            
        if base_vuln.description != compare_vuln.description:
            changes['description'] = {'from': base_vuln.description, 'to': compare_vuln.description}
            
        if base_vuln.severity != compare_vuln.severity:
            changes['severity'] = {'from': base_vuln.severity.value, 'to': compare_vuln.severity.value}
            
        if abs(base_vuln.risk_score - compare_vuln.risk_score) >= 0.1:
            changes['risk_score'] = {'from': base_vuln.risk_score, 'to': compare_vuln.risk_score}
            
        if abs(base_vuln.confidence - compare_vuln.confidence) >= 0.05:
            changes['confidence'] = {'from': base_vuln.confidence, 'to': compare_vuln.confidence}
            
        if base_vuln.line_number != compare_vuln.line_number:
            changes['line_number'] = {'from': base_vuln.line_number, 'to': compare_vuln.line_number}
            
        if base_vuln.recommendation != compare_vuln.recommendation:
            changes['recommendation'] = {'from': base_vuln.recommendation, 'to': compare_vuln.recommendation}
        
        # Determine status
        status = 'modified' if changes else 'unchanged'
        
        return VulnerabilityDiff(
            vuln_id=base_vuln.id,
            status=status,
            base_vuln=base_vuln,
            compare_vuln=compare_vuln,
            changes=changes
        )
    
    def _find_fuzzy_matches(
        self,
        base_vulns: List[VulnerabilityFinding],
        compare_vulns: List[VulnerabilityFinding]
    ) -> List[Tuple[VulnerabilityFinding, VulnerabilityFinding, float]]:
        """Find fuzzy matches between vulnerability lists"""
        
        matches = []
        
        for base_vuln in base_vulns:
            for compare_vuln in compare_vulns:
                similarity = self._calculate_similarity(base_vuln, compare_vuln)
                if similarity > 0.5:  # Only consider reasonable matches
                    matches.append((base_vuln, compare_vuln, similarity))
        
        # Sort by similarity (descending) and return best matches
        matches.sort(key=lambda x: x[2], reverse=True)
        
        # Ensure one-to-one matching
        used_base = set()
        used_compare = set()
        final_matches = []
        
        for base_vuln, compare_vuln, similarity in matches:
            base_key = self._generate_vuln_key(base_vuln)
            compare_key = self._generate_vuln_key(compare_vuln)
            
            if base_key not in used_base and compare_key not in used_compare:
                final_matches.append((base_vuln, compare_vuln, similarity))
                used_base.add(base_key)
                used_compare.add(compare_key)
        
        return final_matches
    
    def _calculate_similarity(
        self, 
        vuln1: VulnerabilityFinding, 
        vuln2: VulnerabilityFinding
    ) -> float:
        """Calculate similarity score between two vulnerabilities"""
        
        scores = []
        
        # Title similarity (high weight)
        title_sim = self._string_similarity(vuln1.title, vuln2.title)
        scores.append(('title', title_sim, 0.4))
        
        # Category match (high weight)
        category_match = 1.0 if vuln1.category == vuln2.category else 0.0
        scores.append(('category', category_match, 0.3))
        
        # Function name similarity (medium weight)
        func_sim = self._string_similarity(vuln1.function_name or "", vuln2.function_name or "")
        scores.append(('function', func_sim, 0.2))
        
        # Description similarity (low weight)
        desc_sim = self._string_similarity(vuln1.description, vuln2.description)
        scores.append(('description', desc_sim, 0.1))
        
        # Calculate weighted average
        total_weight = sum(weight for _, _, weight in scores)
        weighted_sum = sum(score * weight for _, score, weight in scores)
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using Jaccard similarity"""
        
        if not str1 and not str2:
            return 1.0
        if not str1 or not str2:
            return 0.0
        
        # Convert to lowercase and split into words
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_severity_changes(
        self, 
        base_scan: ScanResult, 
        compare_scan: ScanResult
    ) -> Dict[str, Dict[str, int]]:
        """Calculate changes in severity distribution"""
        
        base_severity = {
            'critical': base_scan.critical_issues,
            'high': base_scan.high_issues,
            'medium': base_scan.medium_issues,
            'low': base_scan.low_issues,
            'info': base_scan.info_issues,
        }
        
        compare_severity = {
            'critical': compare_scan.critical_issues,
            'high': compare_scan.high_issues,
            'medium': compare_scan.medium_issues,
            'low': compare_scan.low_issues,
            'info': compare_scan.info_issues,
        }
        
        changes = {}
        for severity in base_severity:
            base_count = base_severity[severity]
            compare_count = compare_severity[severity]
            delta = compare_count - base_count
            
            changes[severity] = {
                'base': base_count,
                'compare': compare_count,
                'delta': delta
            }
        
        return changes
    
    def generate_diff_summary(self, diff: ScanDiff) -> Dict[str, Any]:
        """Generate a human-readable summary of the diff"""
        
        total_changes = (
            diff.vulnerabilities_added + 
            diff.vulnerabilities_removed + 
            diff.vulnerabilities_modified
        )
        
        # Determine overall trend
        if diff.vulnerabilities_added > diff.vulnerabilities_removed:
            trend = "deteriorated"
        elif diff.vulnerabilities_removed > diff.vulnerabilities_added:
            trend = "improved"  
        else:
            trend = "stable"
        
        # Calculate severity trend
        critical_delta = diff.severity_changes.get('critical', {}).get('delta', 0)
        high_delta = diff.severity_changes.get('high', {}).get('delta', 0)
        
        if critical_delta > 0 or high_delta > 0:
            severity_trend = "worsened"
        elif critical_delta < 0 or high_delta < 0:
            severity_trend = "improved"
        else:
            severity_trend = "stable"
        
        return {
            "summary": f"Found {total_changes} changes between scans",
            "overall_trend": trend,
            "severity_trend": severity_trend,
            "risk_score_change": diff.risk_score_delta,
            "key_changes": {
                "added": diff.vulnerabilities_added,
                "removed": diff.vulnerabilities_removed,
                "modified": diff.vulnerabilities_modified,
                "unchanged": diff.vulnerabilities_unchanged,
            },
            "severity_changes": diff.severity_changes,
            "recommendations": self._generate_recommendations(diff),
        }
    
    def _generate_recommendations(self, diff: ScanDiff) -> List[str]:
        """Generate actionable recommendations based on the diff"""
        
        recommendations = []
        
        if diff.vulnerabilities_added > 0:
            recommendations.append(
                f"Review and address {diff.vulnerabilities_added} newly identified vulnerabilities"
            )
        
        if diff.vulnerabilities_removed > 0:
            recommendations.append(
                f"Verify that {diff.vulnerabilities_removed} resolved vulnerabilities are truly fixed"
            )
        
        critical_delta = diff.severity_changes.get('critical', {}).get('delta', 0)
        if critical_delta > 0:
            recommendations.append(
                f"Immediate attention required: {critical_delta} new critical vulnerabilities found"
            )
        
        if diff.risk_score_delta > 1.0:
            recommendations.append(
                "Overall risk has increased significantly - prioritize security review"
            )
        elif diff.risk_score_delta < -1.0:
            recommendations.append(
                "Security posture has improved - continue current practices"
            )
        
        if not recommendations:
            recommendations.append("No significant changes detected - maintain current security practices")
        
        return recommendations


class DiffReportGenerator:
    """Generate reports specifically for scan comparisons"""
    
    def __init__(self, diff_engine: ReportDiffEngine):
        self.diff_engine = diff_engine
    
    async def generate_diff_report(
        self,
        base_scan: ScanResult,
        compare_scan: ScanResult,
        output_format: str = "html"
    ) -> Dict[str, Any]:
        """
        Generate a complete diff report.
        
        Args:
            base_scan: Base scan for comparison
            compare_scan: Scan to compare against base
            output_format: Format for the report (html, json, markdown)
            
        Returns:
            Dictionary containing the complete diff report
        """
        
        # Generate diff
        diff = await self.diff_engine.compare_scans(base_scan, compare_scan, detailed=True)
        
        # Generate summary
        summary = self.diff_engine.generate_diff_summary(diff)
        
        # Build complete report
        report = {
            "metadata": {
                "report_type": "scan_comparison",
                "generated_at": datetime.utcnow().isoformat(),
                "base_scan": {
                    "id": base_scan.id,
                    "project": base_scan.project_name,
                    "date": base_scan.created_at.isoformat(),
                },
                "compare_scan": {
                    "id": compare_scan.id,
                    "project": compare_scan.project_name,
                    "date": compare_scan.created_at.isoformat(),
                },
            },
            "summary": summary,
            "detailed_changes": {
                "added_vulnerabilities": [v.dict() for v in diff.added_vulnerabilities],
                "removed_vulnerabilities": [v.dict() for v in diff.removed_vulnerabilities],
                "modified_vulnerabilities": [
                    {
                        "vulnerability_id": vd.vuln_id,
                        "changes": vd.changes,
                        "base": vd.base_vuln.dict() if vd.base_vuln else None,
                        "compare": vd.compare_vuln.dict() if vd.compare_vuln else None,
                    }
                    for vd in diff.modified_vulnerabilities
                ],
            },
            "statistics": {
                "vulnerabilities_added": diff.vulnerabilities_added,
                "vulnerabilities_removed": diff.vulnerabilities_removed,
                "vulnerabilities_modified": diff.vulnerabilities_modified,
                "vulnerabilities_unchanged": diff.vulnerabilities_unchanged,
                "severity_changes": diff.severity_changes,
                "risk_score_delta": diff.risk_score_delta,
            }
        }
        
        return report

