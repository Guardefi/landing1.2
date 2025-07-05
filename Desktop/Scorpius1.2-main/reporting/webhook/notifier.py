"""
Enterprise Reporting Webhook Notifier
=====================================

Webhook notification system for report generation events and scan results.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

# Handle both relative and absolute imports
try:
    from ..models import ScanResult, Report, VulnerabilityFinding
except ImportError:
    # Fall back to absolute imports
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from models import ScanResult, Report, VulnerabilityFinding

logger = logging.getLogger(__name__)


class WebhookEvent:
    """Webhook event data structure"""
    
    def __init__(
        self,
        event_type: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "metadata": self.metadata
        }


class WebhookNotifier:
    """Webhook notification manager"""
    
    def __init__(self, webhook_urls: List[str], timeout: int = 30, max_retries: int = 3):
        self.webhook_urls = webhook_urls
        self.timeout = timeout
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not AIOHTTP_AVAILABLE:
            logger.warning("aiohttp not available, webhook notifications disabled")
    
    async def __aenter__(self):
        """Async context manager entry"""
        if AIOHTTP_AVAILABLE:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def send_webhook(self, url: str, event: WebhookEvent) -> bool:
        """Send webhook notification to a single URL"""
        if not AIOHTTP_AVAILABLE or not self.session:
            logger.warning("Cannot send webhook - aiohttp not available")
            return False
        
        payload = event.to_dict()
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Scorpius-Reporter/1.0"
        }
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.post(
                    url,
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook sent successfully to {url}")
                        return True
                    else:
                        logger.warning(f"Webhook failed with status {response.status}: {url}")
                        
            except asyncio.TimeoutError:
                logger.error(f"Webhook timeout (attempt {attempt + 1}): {url}")
            except Exception as e:
                logger.error(f"Webhook error (attempt {attempt + 1}): {url} - {e}")
            
            if attempt < self.max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error(f"Webhook failed after {self.max_retries} attempts: {url}")
        return False
    
    async def send_webhooks(self, event: WebhookEvent) -> List[bool]:
        """Send webhook notification to all configured URLs"""
        if not self.webhook_urls:
            return []
        
        tasks = [self.send_webhook(url, event) for url in self.webhook_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Webhook task failed for {self.webhook_urls[i]}: {result}")
                success_results.append(False)
            else:
                success_results.append(result)
        
        return success_results
    
    async def notify_scan_completed(self, scan_result: ScanResult):
        """Notify when a scan is completed"""
        event = WebhookEvent(
            event_type="scan.completed",
            data={
                "scan_id": scan_result.scan_id,
                "target_address": scan_result.target_info.get("address"),
                "findings_count": len(scan_result.findings),
                "high_severity_count": len([
                    f for f in scan_result.findings 
                    if f.severity == "HIGH"
                ]),
                "critical_severity_count": len([
                    f for f in scan_result.findings 
                    if f.severity == "CRITICAL"
                ]),
                "execution_time": scan_result.execution_time,
                "status": scan_result.status
            },
            metadata={
                "scanner_version": scan_result.version,
                "timestamp": scan_result.timestamp.isoformat()
            }
        )
        
        await self.send_webhooks(event)
    
    async def notify_report_generated(self, report: Report):
        """Notify when a report is generated"""
        event = WebhookEvent(
            event_type="report.generated",
            data={
                "report_id": str(report.id),
                "scan_id": report.scan_id,
                "format": report.format,
                "status": report.status,
                "file_path": report.file_path,
                "file_size": report.file_size
            },
            metadata={
                "created_at": report.created_at.isoformat(),
                "template": report.template_name,
                "theme": report.theme_name
            }
        )
        
        await self.send_webhooks(event)
    
    async def notify_critical_vulnerability(self, vulnerability: VulnerabilityFinding):
        """Notify when a critical vulnerability is found"""
        if vulnerability.severity != "CRITICAL":
            return
        
        event = WebhookEvent(
            event_type="vulnerability.critical",
            data={
                "vulnerability_id": vulnerability.id,
                "scan_id": vulnerability.scan_id,
                "title": vulnerability.title,
                "severity": vulnerability.severity,
                "type": vulnerability.type,
                "cvss_score": vulnerability.cvss_score,
                "description": vulnerability.description[:500] + "..." if len(vulnerability.description) > 500 else vulnerability.description,
                "location": vulnerability.location
            },
            metadata={
                "cwe_id": vulnerability.cwe_id,
                "references": vulnerability.references[:3] if vulnerability.references else []  # Limit references
            }
        )
        
        await self.send_webhooks(event)
    
    async def notify_scan_failed(self, scan_id: str, error_message: str):
        """Notify when a scan fails"""
        event = WebhookEvent(
            event_type="scan.failed",
            data={
                "scan_id": scan_id,
                "error_message": error_message,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        await self.send_webhooks(event)
    
    async def notify_custom_event(self, event_type: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Send custom webhook event"""
        event = WebhookEvent(
            event_type=event_type,
            data=data,
            metadata=metadata
        )
        
        await self.send_webhooks(event)


class WebhookManager:
    """Global webhook manager for the application"""
    
    def __init__(self):
        self.webhook_urls: List[str] = []
        self.enabled = False
        self.timeout = 30
        self.max_retries = 3
    
    def configure(
        self,
        webhook_urls: List[str],
        enabled: bool = True,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Configure webhook settings"""
        self.webhook_urls = webhook_urls
        self.enabled = enabled
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Validate URLs
        valid_urls = []
        for url in webhook_urls:
            try:
                parsed = urlparse(url)
                if parsed.scheme in ("http", "https") and parsed.netloc:
                    valid_urls.append(url)
                else:
                    logger.warning(f"Invalid webhook URL: {url}")
            except Exception as e:
                logger.error(f"Error parsing webhook URL {url}: {e}")
        
        self.webhook_urls = valid_urls
        logger.info(f"Configured {len(self.webhook_urls)} webhook URLs")
    
    async def send_notification(self, event_type: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Send webhook notification"""
        if not self.enabled or not self.webhook_urls:
            return
        
        async with WebhookNotifier(
            webhook_urls=self.webhook_urls,
            timeout=self.timeout,
            max_retries=self.max_retries
        ) as notifier:
            await notifier.notify_custom_event(event_type, data, metadata)
    
    async def notify_scan_completed(self, scan_result: ScanResult):
        """Convenience method for scan completion notification"""
        if not self.enabled:
            return
        
        async with WebhookNotifier(
            webhook_urls=self.webhook_urls,
            timeout=self.timeout,
            max_retries=self.max_retries
        ) as notifier:
            await notifier.notify_scan_completed(scan_result)
    
    async def notify_report_generated(self, report: Report):
        """Convenience method for report generation notification"""
        if not self.enabled:
            return
        
        async with WebhookNotifier(
            webhook_urls=self.webhook_urls,
            timeout=self.timeout,
            max_retries=self.max_retries
        ) as notifier:
            await notifier.notify_report_generated(report)
    
    async def notify_critical_vulnerability(self, vulnerability: VulnerabilityFinding):
        """Convenience method for critical vulnerability notification"""
        if not self.enabled:
            return
        
        async with WebhookNotifier(
            webhook_urls=self.webhook_urls,
            timeout=self.timeout,
            max_retries=self.max_retries
        ) as notifier:
            await notifier.notify_critical_vulnerability(vulnerability)


# Global webhook manager instance
webhook_manager = WebhookManager()


def get_webhook_manager() -> WebhookManager:
    """Get the global webhook manager instance"""
    return webhook_manager
