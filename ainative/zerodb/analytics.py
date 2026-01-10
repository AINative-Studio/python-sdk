"""
ZeroDB Analytics Module

Provides analytics and insights for ZeroDB operations.
"""

from typing import TYPE_CHECKING, Dict, Any, Optional, List
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from ..client import AINativeClient


class AnalyticsClient:
    """Client for ZeroDB analytics operations."""

    def __init__(self, client: "AINativeClient"):
        """
        Initialize analytics client.

        Args:
            client: Parent AINative client instance
        """
        self.client = client
        # Analytics are accessed via /projects/{project_id}/database/analytics/*
        self.base_path = "/projects"
    
    def get_usage(
        self,
        project_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: str = "daily",
    ) -> Dict[str, Any]:
        """
        Get usage analytics.

        Args:
            project_id: Project ID (required)
            start_date: Start date for analytics
            end_date: End date for analytics
            granularity: Data granularity (hourly, daily, weekly, monthly)

        Returns:
            Usage analytics data
        """
        params = {"granularity": granularity}

        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        return self.client.get(f"{self.base_path}/{project_id}/database/analytics/usage", params=params)
    
    def get_performance_metrics(
        self,
        project_id: str,
        metric_type: str = "all",
    ) -> Dict[str, Any]:
        """
        Get performance metrics.

        Args:
            project_id: Project ID (required)
            metric_type: Type of metrics (latency, throughput, errors, all)

        Returns:
            Performance metrics data
        """
        params = {"metric_type": metric_type}

        return self.client.get(f"{self.base_path}/{project_id}/database/analytics/performance", params=params)
    
    def get_storage_stats(
        self,
        project_id: str,
    ) -> Dict[str, Any]:
        """
        Get storage statistics.

        Args:
            project_id: Project ID (required)

        Returns:
            Storage statistics including size, vector count, etc.
        """
        return self.client.get(f"{self.base_path}/{project_id}/database/analytics/storage")
    
    def get_query_insights(
        self,
        project_id: str,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Get query pattern insights.

        Args:
            project_id: Project ID (required)
            limit: Maximum number of insights

        Returns:
            Query insights and patterns
        """
        params = {"limit": limit}

        return self.client.get(f"{self.base_path}/{project_id}/database/analytics/queries", params=params)
    
    def get_cost_analysis(
        self,
        project_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get cost analysis and projections.

        Args:
            project_id: Project ID (required)
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Cost analysis data
        """
        params = {}

        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        return self.client.get(f"{self.base_path}/{project_id}/database/analytics/costs", params=params)
    
    def get_trends(
        self,
        project_id: str,
        metric: str,
        period: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Get trend data for specific metrics.

        Args:
            project_id: Project ID (required)
            metric: Metric name (vectors, queries, storage, errors)
            period: Number of days to analyze

        Returns:
            Trend data points
        """
        params = {
            "metric": metric,
            "period": period,
        }

        response = self.client.get(f"{self.base_path}/{project_id}/database/analytics/trends", params=params)
        return response.get("data", [])
    
    def get_anomalies(
        self,
        project_id: str,
        severity: str = "all",
    ) -> List[Dict[str, Any]]:
        """
        Get detected anomalies in usage patterns.

        Args:
            project_id: Project ID (required)
            severity: Severity filter (low, medium, high, critical, all)

        Returns:
            List of detected anomalies
        """
        params = {"severity": severity}

        response = self.client.get(f"{self.base_path}/{project_id}/database/analytics/anomalies", params=params)
        return response.get("anomalies", [])
    
    def export_report(
        self,
        project_id: str,
        report_type: str = "summary",
        format: str = "json",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Export analytics report.

        Args:
            project_id: Project ID (required)
            report_type: Type of report (summary, detailed, custom)
            format: Export format (json, csv, pdf)
            start_date: Start date for report
            end_date: End date for report

        Returns:
            Report data or download URL
        """
        data = {
            "report_type": report_type,
            "format": format,
        }

        if start_date:
            data["start_date"] = start_date.isoformat()
        if end_date:
            data["end_date"] = end_date.isoformat()

        return self.client.post(f"{self.base_path}/{project_id}/database/analytics/export", data=data)