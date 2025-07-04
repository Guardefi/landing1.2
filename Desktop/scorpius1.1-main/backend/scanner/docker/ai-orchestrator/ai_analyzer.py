#!/usr/bin/env python3
"""
AI Analyzer - Advanced vulnerability analysis using OpenAI and Anthropic APIs
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

import aiohttp

logger = logging.getLogger("scorpius.ai_analyzer")


class AIAnalyzer:
    """AI-powered vulnerability analyzer using OpenAI and Anthropic"""
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        """Initialize AI analyzer with API keys"""
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key
        self.session = None
        
        # Vulnerability patterns from your existing AI system
        self.vulnerability_patterns = {
            "reentrancy": {
                "patterns": [
                    "external call before state update",
                    "call.value() without reentrancy guard",
                    "transfer() in payable function without mutex",
                    "delegatecall with untrusted callee",
                ],
                "risk_multiplier": 2.5,
                "common_exploits": ["DAO attack", "cross-function reentrancy"],
            },
            "flash_loan_attack": {
                "patterns": [
                    "price oracle manipulation",
                    "single block arbitrage",
                    "governance token flash loan",
                    "AMM price manipulation",
                ],
                "risk_multiplier": 2.0,
                "common_exploits": ["Cream Finance", "bZx protocol"],
            },
            "access_control": {
                "patterns": [
                    "missing onlyOwner modifier",
                    "unprotected initialization",
                    "role-based access without checks",
                    "proxy admin functions",
                ],
                "risk_multiplier": 1.8,
                "common_exploits": ["admin key compromise", "initialization frontrunning"],
            },
            "oracle_manipulation": {
                "patterns": [
                    "single price oracle source",
                    "spot price usage",
                    "no TWAP implementation",
                    "flash loan oracle manipulation",
                ],
                "risk_multiplier": 2.2,
                "common_exploits": ["Harvest Finance", "Value DeFi"],
            },
        }
        
        # Recent exploit database for context
        self.exploit_database = {
            "recent_exploits": [
                {"type": "flash_loan", "date": "2024-01", "loss": 50000000},
                {"type": "reentrancy", "date": "2024-02", "loss": 25000000},
                {"type": "oracle_manipulation", "date": "2024-03", "loss": 75000000},
            ],
            "exploit_trends": {
                "flash_loan": {"frequency": 0.15, "avg_loss": 35000000},
                "reentrancy": {"frequency": 0.10, "avg_loss": 20000000},
                "oracle_manipulation": {"frequency": 0.12, "avg_loss": 45000000},
            },
        }
    
    def is_healthy(self) -> bool:
        """Check if AI analyzer is healthy"""
        return self.openai_api_key is not None or self.anthropic_api_key is not None
    
    async def analyze_with_scanner_context(
        self,
        source_code: Optional[str],
        target_path: str,
        scanner_results: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze with scanner context for enhanced intelligence"""
        logger.info("Starting AI analysis with scanner context")
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Step 1: Analyze scanner findings for patterns
            pattern_analysis = self._analyze_scanner_patterns(scanner_results)
            
            # Step 2: AI-enhanced vulnerability detection
            ai_findings = await self._ai_vulnerability_detection(
                source_code, scanner_results, pattern_analysis
            )
            
            # Step 3: Risk assessment
            risk_assessment = self._generate_risk_assessment(
                ai_findings, scanner_results, pattern_analysis
            )
            
            # Step 4: Exploit prediction
            exploit_prediction = self._predict_exploit_potential(
                ai_findings, scanner_results, risk_assessment
            )
            
            # Step 5: Generate recommendations
            recommendations = self._generate_recommendations(
                ai_findings, scanner_results, risk_assessment
            )
            
            return {
                "findings": ai_findings,
                "risk_assessment": risk_assessment,
                "exploit_prediction": exploit_prediction,
                "recommendations": recommendations,
                "pattern_analysis": pattern_analysis,
                "ai_metadata": {
                    "analysis_time": datetime.now().isoformat(),
                    "models_used": self._get_available_models(),
                    "confidence_level": self._calculate_overall_confidence(ai_findings)
                }
            }
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {
                "findings": [],
                "risk_assessment": {"error": str(e)},
                "exploit_prediction": {"error": str(e)},
                "recommendations": [],
                "pattern_analysis": {},
                "ai_metadata": {"error": str(e)}
            }
    
    def _analyze_scanner_patterns(self, scanner_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns across scanner results"""
        pattern_analysis = {
            "common_vulnerabilities": [],
            "severity_correlation": {},
            "location_clustering": {},
            "confidence_patterns": {},
            "false_positive_indicators": []
        }
        
        all_findings = []
        for scanner_name, results in scanner_results.items():
            if "findings" in results:
                for finding in results["findings"]:
                    finding["scanner_source"] = scanner_name
                    all_findings.append(finding)
        
        if not all_findings:
            return pattern_analysis
        
        # Find common vulnerabilities across scanners
        vulnerability_counts = {}
        for finding in all_findings:
            vuln_type = finding.get("category", "unknown")
            if vuln_type not in vulnerability_counts:
                vulnerability_counts[vuln_type] = {"count": 0, "scanners": set(), "severities": []}
            
            vulnerability_counts[vuln_type]["count"] += 1
            vulnerability_counts[vuln_type]["scanners"].add(finding.get("scanner_source", "unknown"))
            vulnerability_counts[vuln_type]["severities"].append(finding.get("severity", "unknown"))
        
        # Identify vulnerabilities found by multiple scanners (higher confidence)
        for vuln_type, data in vulnerability_counts.items():
            if len(data["scanners"]) > 1:
                pattern_analysis["common_vulnerabilities"].append({
                    "type": vuln_type,
                    "count": data["count"],
                    "scanner_agreement": len(data["scanners"]),
                    "scanners": list(data["scanners"]),
                    "severity_consensus": max(set(data["severities"]), key=data["severities"].count)
                })
        
        return pattern_analysis
    
    async def _ai_vulnerability_detection(
        self,
        source_code: Optional[str],
        scanner_results: Dict[str, Any],
        pattern_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Use AI models for enhanced vulnerability detection"""
        ai_findings = []
        
        if not source_code:
            return ai_findings
        
        # Create comprehensive analysis prompt
        prompt = self._build_comprehensive_prompt(source_code, scanner_results, pattern_analysis)
        
        # Try OpenAI first, then Anthropic as fallback
        if self.openai_api_key:
            try:
                ai_response = await self._query_openai(prompt)
                ai_findings.extend(self._parse_ai_response(ai_response, "openai"))
            except Exception as e:
                logger.warning(f"OpenAI analysis failed: {e}")
        
        if self.anthropic_api_key and len(ai_findings) == 0:  # Use as fallback
            try:
                ai_response = await self._query_anthropic(prompt)
                ai_findings.extend(self._parse_ai_response(ai_response, "anthropic"))
            except Exception as e:
                logger.warning(f"Anthropic analysis failed: {e}")
        
        # Add pattern-based findings
        pattern_findings = self._detect_known_patterns(source_code)
        ai_findings.extend(pattern_findings)
        
        return ai_findings
    
    def _build_comprehensive_prompt(
        self,
        source_code: str,
        scanner_results: Dict[str, Any],
        pattern_analysis: Dict[str, Any]
    ) -> str:
        """Build comprehensive analysis prompt"""
        
        # Summarize scanner findings
        scanner_summary = []
        for scanner_name, results in scanner_results.items():
            finding_count = len(results.get("findings", []))
            if finding_count > 0:
                scanner_summary.append(f"- {scanner_name}: {finding_count} findings")
        
        # Common vulnerabilities
        common_vulns = [cv["type"] for cv in pattern_analysis.get("common_vulnerabilities", [])]
        
        prompt = f"""
You are an expert smart contract security auditor. Analyze this Solidity contract for vulnerabilities.

SCANNER CONTEXT:
{chr(10).join(scanner_summary) if scanner_summary else "No scanner results available"}

COMMON VULNERABILITIES DETECTED:
{', '.join(common_vulns) if common_vulns else "None detected by multiple scanners"}

CONTRACT CODE:
```solidity
{source_code[:4000]}  # Truncate for API limits
```

Please provide a comprehensive security analysis focusing on:

1. **Critical Vulnerabilities**: Reentrancy, flash loan attacks, access control issues
2. **DeFi-Specific Risks**: Oracle manipulation, MEV vulnerabilities, governance attacks
3. **Business Logic Flaws**: Economic exploits, invariant violations
4. **False Positive Analysis**: Evaluate if scanner findings are likely false positives
5. **Novel Attack Vectors**: Identify potential new attack patterns

For each vulnerability found, provide:
- Vulnerability type and severity (critical/high/medium/low)
- Specific location (function name, line number if possible)
- Exploit scenario with step-by-step attack description
- Estimated financial impact
- Confidence level (0-1)
- Recommended remediation

Focus on actionable, high-confidence findings that pose real security risks.

Respond in JSON format:
{{
    "vulnerabilities": [
        {{
            "id": "unique-id",
            "title": "Vulnerability Title",
            "category": "vulnerability-type", 
            "severity": "critical|high|medium|low",
            "confidence": 0.95,
            "description": "Detailed description",
            "location": {{"function": "functionName", "line": 42}},
            "exploit_scenario": "Step by step attack",
            "financial_impact": "Estimated loss amount",
            "remediation": "How to fix"
        }}
    ]
}}
"""
        return prompt
    
    async def _query_openai(self, prompt: str) -> Dict[str, Any]:
        """Query OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4-turbo-preview",
            "messages": [
                {"role": "system", "content": "You are an expert smart contract security auditor."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000,
            "temperature": 0.1
        }
        
        async with self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        ) as response:
            if response.status != 200:
                raise Exception(f"OpenAI API error: {response.status}")
            
            result = await response.json()
            return result
    
    async def _query_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Query Anthropic API"""
        headers = {
            "x-api-key": self.anthropic_api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with self.session.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=60
        ) as response:
            if response.status != 200:
                raise Exception(f"Anthropic API error: {response.status}")
            
            result = await response.json()
            return result
    
    def _parse_ai_response(self, response: Dict[str, Any], model_type: str) -> List[Dict[str, Any]]:
        """Parse AI model response into findings"""
        findings = []
        
        try:
            if model_type == "openai":
                content = response["choices"][0]["message"]["content"]
            elif model_type == "anthropic":
                content = response["content"][0]["text"]
            else:
                return findings
            
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_data = json.loads(json_str)
                
                for vuln in parsed_data.get("vulnerabilities", []):
                    finding = {
                        "id": f"ai-{model_type}-{vuln.get('id', 'unknown')}",
                        "title": vuln.get("title", "AI-detected vulnerability"),
                        "category": vuln.get("category", "ai-analysis"),
                        "severity": vuln.get("severity", "medium"),
                        "confidence": vuln.get("confidence", 0.7),
                        "description": vuln.get("description", ""),
                        "location": vuln.get("location", {}),
                        "plugin": f"ai-{model_type}",
                        "exploit_scenario": vuln.get("exploit_scenario", ""),
                        "financial_impact": vuln.get("financial_impact", ""),
                        "remediation": vuln.get("remediation", ""),
                        "raw_output": vuln
                    }
                    findings.append(finding)
            
        except Exception as e:
            logger.error(f"Failed to parse {model_type} response: {e}")
        
        return findings
    
    def _detect_known_patterns(self, source_code: str) -> List[Dict[str, Any]]:
        """Detect known vulnerability patterns"""
        pattern_findings = []
        
        for vuln_type, pattern_data in self.vulnerability_patterns.items():
            for pattern in pattern_data["patterns"]:
                if pattern.lower() in source_code.lower():
                    finding = {
                        "id": f"pattern-{vuln_type}-{len(pattern_findings)}",
                        "title": f"Potential {vuln_type.replace('_', ' ').title()}",
                        "category": vuln_type,
                        "severity": self._pattern_to_severity(vuln_type, pattern_data["risk_multiplier"]),
                        "confidence": 0.6,  # Lower confidence for pattern matching
                        "description": f"Pattern detected: {pattern}",
                        "location": {"pattern": pattern},
                        "plugin": "ai-pattern-detector",
                        "raw_output": {"pattern": pattern, "vuln_type": vuln_type}
                    }
                    pattern_findings.append(finding)
        
        return pattern_findings
    
    def _pattern_to_severity(self, vuln_type: str, risk_multiplier: float) -> str:
        """Convert pattern risk to severity"""
        if risk_multiplier >= 2.0:
            return "high"
        elif risk_multiplier >= 1.5:
            return "medium"
        else:
            return "low"
    
    def _generate_risk_assessment(
        self,
        ai_findings: List[Dict[str, Any]],
        scanner_results: Dict[str, Any],
        pattern_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive risk assessment"""
        
        all_findings = ai_findings.copy()
        for scanner_data in scanner_results.values():
            all_findings.extend(scanner_data.get("findings", []))
        
        if not all_findings:
            return {
                "overall_score": 0.0,
                "risk_level": "minimal",
                "total_findings": 0,
                "critical_count": 0,
                "high_count": 0,
                "financial_risk": "minimal"
            }
        
        # Count by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in all_findings:
            severity = finding.get("severity", "low").lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Calculate overall risk score (0-10)
        risk_score = (
            severity_counts["critical"] * 3.0 +
            severity_counts["high"] * 2.0 +
            severity_counts["medium"] * 1.0 +
            severity_counts["low"] * 0.3
        )
        
        # Normalize to 0-10 scale
        risk_score = min(risk_score, 10.0)
        
        # Determine risk level
        if risk_score >= 8.0:
            risk_level = "critical"
        elif risk_score >= 6.0:
            risk_level = "high"
        elif risk_score >= 4.0:
            risk_level = "medium"
        elif risk_score >= 2.0:
            risk_level = "low"
        else:
            risk_level = "minimal"
        
        # Estimate financial risk
        if severity_counts["critical"] > 0:
            financial_risk = "total_loss_possible"
        elif severity_counts["high"] > 2:
            financial_risk = "significant_loss_likely"
        elif severity_counts["high"] > 0 or severity_counts["medium"] > 3:
            financial_risk = "moderate_loss_possible"
        else:
            financial_risk = "minimal"
        
        return {
            "overall_score": round(risk_score, 2),
            "risk_level": risk_level,
            "total_findings": len(all_findings),
            "severity_distribution": severity_counts,
            "critical_count": severity_counts["critical"],
            "high_count": severity_counts["high"],
            "financial_risk": financial_risk,
            "scanner_agreement": len(pattern_analysis.get("common_vulnerabilities", [])),
            "confidence_assessment": self._calculate_overall_confidence(all_findings)
        }
    
    def _predict_exploit_potential(
        self,
        ai_findings: List[Dict[str, Any]],
        scanner_results: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict exploit development potential"""
        
        exploit_factors = {
            "complexity": "medium",
            "time_to_exploit": 30,  # days
            "weaponization_likelihood": 0.3,
            "market_value": 0,
            "mass_exploitation_risk": 0.2
        }
        
        # Analyze critical vulnerabilities
        critical_count = risk_assessment.get("critical_count", 0)
        high_count = risk_assessment.get("high_count", 0)
        
        if critical_count > 0:
            exploit_factors["complexity"] = "low"
            exploit_factors["time_to_exploit"] = 7
            exploit_factors["weaponization_likelihood"] = 0.8
            exploit_factors["market_value"] = 50000
            exploit_factors["mass_exploitation_risk"] = 0.7
        elif high_count > 1:
            exploit_factors["complexity"] = "medium"
            exploit_factors["time_to_exploit"] = 14
            exploit_factors["weaponization_likelihood"] = 0.6
            exploit_factors["market_value"] = 25000
            exploit_factors["mass_exploitation_risk"] = 0.5
        
        # Check for known attack patterns
        for finding in ai_findings:
            category = finding.get("category", "").lower()
            if category in ["reentrancy", "flash_loan_attack", "oracle_manipulation"]:
                exploit_factors["weaponization_likelihood"] = min(
                    exploit_factors["weaponization_likelihood"] + 0.2, 0.9
                )
                exploit_factors["market_value"] += 10000
        
        return exploit_factors
    
    def _generate_recommendations(
        self,
        ai_findings: List[Dict[str, Any]],
        scanner_results: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable security recommendations"""
        recommendations = []
        
        # Priority recommendations based on risk level
        risk_level = risk_assessment.get("risk_level", "minimal")
        
        if risk_level in ["critical", "high"]:
            recommendations.append("🚨 URGENT: Halt all contract operations immediately")
            recommendations.append("🔒 Conduct emergency security review with external auditor")
            recommendations.append("💰 Consider bug bounty program before mainnet deployment")
        
        # Specific recommendations based on findings
        vulnerability_types = set()
        for finding in ai_findings:
            vulnerability_types.add(finding.get("category", "unknown"))
        
        for scanner_data in scanner_results.values():
            for finding in scanner_data.get("findings", []):
                vulnerability_types.add(finding.get("category", "unknown"))
        
        # Type-specific recommendations
        if "reentrancy" in vulnerability_types:
            recommendations.append("🛡️ Implement reentrancy guards using OpenZeppelin's ReentrancyGuard")
            recommendations.append("🔄 Follow checks-effects-interactions pattern")
        
        if "oracle_manipulation" in vulnerability_types:
            recommendations.append("📊 Implement time-weighted average price (TWAP) oracles")
            recommendations.append("🔗 Use multiple independent oracle sources")
        
        if "access_control" in vulnerability_types:
            recommendations.append("🔐 Implement role-based access control with OpenZeppelin AccessControl")
            recommendations.append("👥 Use multi-signature wallets for admin functions")
        
        if "flash_loan_attack" in vulnerability_types:
            recommendations.append("⚡ Add flash loan protection mechanisms")
            recommendations.append("🏦 Implement invariant checks for critical state changes")
        
        # General recommendations
        recommendations.extend([
            "🧪 Implement comprehensive unit and integration tests",
            "📋 Consider formal verification for critical functions",
            "🔍 Set up continuous monitoring and alerting systems",
            "📚 Conduct regular security audits and code reviews"
        ])
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _get_available_models(self) -> List[str]:
        """Get list of available AI models"""
        models = []
        if self.openai_api_key:
            models.append("openai-gpt4")
        if self.anthropic_api_key:
            models.append("anthropic-claude")
        return models
    
    def _calculate_overall_confidence(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score"""
        if not findings:
            return 0.0
        
        total_confidence = sum(finding.get("confidence", 0.5) for finding in findings)
        return round(total_confidence / len(findings), 2) 