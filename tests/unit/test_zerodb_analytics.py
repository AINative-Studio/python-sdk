"""
Unit tests for the ZeroDB analytics module.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from ainative.zerodb.analytics import AnalyticsClient


class TestAnalyticsClient:
    """Test AnalyticsClient class."""
    
    @pytest.fixture
    def analytics_client(self, client):
        """Create AnalyticsClient instance."""
        return AnalyticsClient(client)
    
    def test_init(self, client):
        """Test initialization."""
        analytics = AnalyticsClient(client)
        assert analytics.client == client
        assert analytics.base_path == "/zerodb/analytics"
    
    def test_get_usage_default_params(self, analytics_client, sample_analytics):
        """Test getting usage analytics with default parameters."""
        analytics_client.client.get.return_value = sample_analytics["usage"]
        
        result = analytics_client.get_usage()
        
        assert result == sample_analytics["usage"]
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["granularity"] == "daily"
        assert "project_id" not in params
        assert "start_date" not in params
        assert "end_date" not in params
    
    def test_get_usage_with_project_filter(self, analytics_client):
        """Test getting usage analytics for specific project."""
        usage_data = {"vectors_stored": 5000, "queries_executed": 2500}
        analytics_client.client.get.return_value = usage_data
        
        result = analytics_client.get_usage(project_id="proj_123")
        
        assert result == usage_data
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["project_id"] == "proj_123"
        assert params["granularity"] == "daily"
    
    def test_get_usage_with_date_range(self, analytics_client):
        """Test getting usage analytics with date range."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        usage_data = {"period": "January 2024"}
        analytics_client.client.get.return_value = usage_data
        
        result = analytics_client.get_usage(
            start_date=start_date,
            end_date=end_date,
            granularity="weekly"
        )
        
        assert result == usage_data
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["start_date"] == start_date.isoformat()
        assert params["end_date"] == end_date.isoformat()
        assert params["granularity"] == "weekly"
    
    def test_get_usage_all_params(self, analytics_client):
        """Test getting usage analytics with all parameters."""
        start_date = datetime(2024, 6, 1)
        end_date = datetime(2024, 6, 30)
        analytics_client.client.get.return_value = {}
        
        analytics_client.get_usage(
            project_id="proj_456",
            start_date=start_date,
            end_date=end_date,
            granularity="hourly"
        )
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["project_id"] == "proj_456"
        assert params["start_date"] == start_date.isoformat()
        assert params["end_date"] == end_date.isoformat()
        assert params["granularity"] == "hourly"
    
    def test_get_performance_metrics_default(self, analytics_client, sample_analytics):
        """Test getting performance metrics with defaults."""
        analytics_client.client.get.return_value = sample_analytics["performance"]
        
        result = analytics_client.get_performance_metrics()
        
        assert result == sample_analytics["performance"]
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["metric_type"] == "all"
        assert "project_id" not in params
    
    def test_get_performance_metrics_specific_type(self, analytics_client):
        """Test getting specific performance metrics."""
        latency_data = {"avg_latency_ms": 15, "p99_latency_ms": 45}
        analytics_client.client.get.return_value = latency_data
        
        result = analytics_client.get_performance_metrics(
            project_id="proj_123",
            metric_type="latency"
        )
        
        assert result == latency_data
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["project_id"] == "proj_123"
        assert params["metric_type"] == "latency"
    
    def test_get_performance_metric_types(self, analytics_client):
        """Test different performance metric types."""
        analytics_client.client.get.return_value = {}
        
        metric_types = ["latency", "throughput", "errors", "all"]
        
        for metric_type in metric_types:
            analytics_client.get_performance_metrics(metric_type=metric_type)
            
            call_args = analytics_client.client.get.call_args
            params = call_args[1]["params"]
            assert params["metric_type"] == metric_type
            
            analytics_client.client.get.reset_mock()
    
    def test_get_storage_stats_no_filter(self, analytics_client):
        """Test getting storage statistics without project filter."""
        storage_data = {
            "total_vectors": 50000,
            "storage_bytes": 1073741824,
            "index_size_bytes": 104857600
        }
        analytics_client.client.get.return_value = storage_data
        
        result = analytics_client.get_storage_stats()
        
        assert result == storage_data
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert len(params) == 0  # No parameters
    
    def test_get_storage_stats_with_project(self, analytics_client):
        """Test getting storage statistics for specific project."""
        project_storage = {
            "vectors": 10000,
            "storage_bytes": 209715200,
            "namespaces": ["default", "documents"]
        }
        analytics_client.client.get.return_value = project_storage
        
        result = analytics_client.get_storage_stats(project_id="proj_789")
        
        assert result == project_storage
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["project_id"] == "proj_789"
    
    def test_get_query_insights_default(self, analytics_client):
        """Test getting query insights with defaults."""
        insights_data = {
            "top_queries": [
                {"query_type": "vector_search", "count": 1500},
                {"query_type": "memory_search", "count": 800}
            ],
            "avg_response_time": 25.4
        }
        analytics_client.client.get.return_value = insights_data
        
        result = analytics_client.get_query_insights()
        
        assert result == insights_data
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["limit"] == 100
        assert "project_id" not in params
    
    def test_get_query_insights_with_params(self, analytics_client):
        """Test getting query insights with parameters."""
        insights_data = {"project_specific_insights": True}
        analytics_client.client.get.return_value = insights_data
        
        result = analytics_client.get_query_insights(
            project_id="proj_456",
            limit=50
        )
        
        assert result == insights_data
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["project_id"] == "proj_456"
        assert params["limit"] == 50
    
    def test_get_cost_analysis_no_filters(self, analytics_client, sample_analytics):
        """Test getting cost analysis without filters."""
        analytics_client.client.get.return_value = sample_analytics["costs"]
        
        result = analytics_client.get_cost_analysis()
        
        assert result == sample_analytics["costs"]
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert len(params) == 0
    
    def test_get_cost_analysis_with_filters(self, analytics_client):
        """Test getting cost analysis with filters."""
        start_date = datetime(2024, 3, 1)
        end_date = datetime(2024, 3, 31)
        cost_data = {
            "period": "March 2024",
            "storage_cost": 15.75,
            "compute_cost": 32.50
        }
        analytics_client.client.get.return_value = cost_data
        
        result = analytics_client.get_cost_analysis(
            project_id="proj_cost",
            start_date=start_date,
            end_date=end_date
        )
        
        assert result == cost_data
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["project_id"] == "proj_cost"
        assert params["start_date"] == start_date.isoformat()
        assert params["end_date"] == end_date.isoformat()
    
    def test_get_trends_basic(self, analytics_client):
        """Test getting trend data."""
        trend_data = [
            {"date": "2024-01-01", "value": 100},
            {"date": "2024-01-02", "value": 150},
            {"date": "2024-01-03", "value": 200}
        ]
        analytics_client.client.get.return_value = {"data": trend_data}
        
        result = analytics_client.get_trends("vectors")
        
        assert result == trend_data
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["metric"] == "vectors"
        assert params["period"] == 30  # Default
        assert "project_id" not in params
    
    def test_get_trends_with_params(self, analytics_client):
        """Test getting trends with parameters."""
        analytics_client.client.get.return_value = {"data": []}
        
        result = analytics_client.get_trends(
            metric="queries",
            project_id="proj_trend",
            period=90
        )
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["metric"] == "queries"
        assert params["project_id"] == "proj_trend"
        assert params["period"] == 90
    
    def test_get_trends_different_metrics(self, analytics_client):
        """Test getting trends for different metrics."""
        analytics_client.client.get.return_value = {"data": []}
        
        metrics = ["vectors", "queries", "storage", "errors"]
        
        for metric in metrics:
            analytics_client.get_trends(metric)
            
            call_args = analytics_client.client.get.call_args
            params = call_args[1]["params"]
            assert params["metric"] == metric
            
            analytics_client.client.get.reset_mock()
    
    def test_get_trends_empty_data(self, analytics_client):
        """Test getting trends when no data is available."""
        analytics_client.client.get.return_value = {}
        
        result = analytics_client.get_trends("vectors")
        
        assert result == []
    
    def test_get_anomalies_default(self, analytics_client):
        """Test getting anomalies with defaults."""
        anomaly_data = [
            {
                "id": "anom_1",
                "type": "spike",
                "metric": "query_latency",
                "severity": "high",
                "detected_at": "2024-01-01T12:00:00Z"
            }
        ]
        analytics_client.client.get.return_value = {"anomalies": anomaly_data}
        
        result = analytics_client.get_anomalies()
        
        assert result == anomaly_data
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["severity"] == "all"
        assert "project_id" not in params
    
    def test_get_anomalies_with_filters(self, analytics_client):
        """Test getting anomalies with filters."""
        analytics_client.client.get.return_value = {"anomalies": []}
        
        result = analytics_client.get_anomalies(
            project_id="proj_anom",
            severity="critical"
        )
        
        call_args = analytics_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["project_id"] == "proj_anom"
        assert params["severity"] == "critical"
    
    def test_get_anomalies_severity_levels(self, analytics_client):
        """Test getting anomalies with different severity levels."""
        analytics_client.client.get.return_value = {"anomalies": []}
        
        severities = ["low", "medium", "high", "critical", "all"]
        
        for severity in severities:
            analytics_client.get_anomalies(severity=severity)
            
            call_args = analytics_client.client.get.call_args
            params = call_args[1]["params"]
            assert params["severity"] == severity
            
            analytics_client.client.get.reset_mock()
    
    def test_get_anomalies_empty(self, analytics_client):
        """Test getting anomalies when none exist."""
        analytics_client.client.get.return_value = {}
        
        result = analytics_client.get_anomalies()
        
        assert result == []
    
    def test_export_report_default(self, analytics_client):
        """Test exporting report with defaults."""
        export_response = {
            "report_id": "rpt_123",
            "download_url": "https://api.ainative.studio/reports/rpt_123.json",
            "expires_at": "2024-01-02T00:00:00Z"
        }
        analytics_client.client.post.return_value = export_response
        
        result = analytics_client.export_report()
        
        assert result == export_response
        
        call_args = analytics_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["report_type"] == "summary"
        assert data["format"] == "json"
        assert "project_id" not in data
        assert "start_date" not in data
        assert "end_date" not in data
    
    def test_export_report_full_params(self, analytics_client):
        """Test exporting report with all parameters."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        export_response = {"report_id": "rpt_456"}
        analytics_client.client.post.return_value = export_response
        
        result = analytics_client.export_report(
            report_type="detailed",
            project_id="proj_export",
            format="pdf",
            start_date=start_date,
            end_date=end_date
        )
        
        assert result == export_response
        
        call_args = analytics_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["report_type"] == "detailed"
        assert data["project_id"] == "proj_export"
        assert data["format"] == "pdf"
        assert data["start_date"] == start_date.isoformat()
        assert data["end_date"] == end_date.isoformat()
    
    def test_export_report_different_formats(self, analytics_client):
        """Test exporting reports in different formats."""
        analytics_client.client.post.return_value = {"report_id": "test"}
        
        formats = ["json", "csv", "pdf"]
        
        for format_type in formats:
            analytics_client.export_report(format=format_type)
            
            call_args = analytics_client.client.post.call_args
            data = call_args[1]["data"]
            assert data["format"] == format_type
            
            analytics_client.client.post.reset_mock()
    
    def test_export_report_types(self, analytics_client):
        """Test exporting different report types."""
        analytics_client.client.post.return_value = {"report_id": "test"}
        
        report_types = ["summary", "detailed", "custom"]
        
        for report_type in report_types:
            analytics_client.export_report(report_type=report_type)
            
            call_args = analytics_client.client.post.call_args
            data = call_args[1]["data"]
            assert data["report_type"] == report_type
            
            analytics_client.client.post.reset_mock()


class TestAnalyticsClientIntegration:
    """Test AnalyticsClient integration scenarios."""
    
    @pytest.fixture
    def analytics_client(self, client):
        return AnalyticsClient(client)
    
    def test_comprehensive_analytics_workflow(self, analytics_client, sample_analytics):
        """Test complete analytics workflow."""
        # Setup mock responses
        usage_response = sample_analytics["usage"]
        performance_response = sample_analytics["performance"]
        costs_response = sample_analytics["costs"]
        storage_response = {"total_vectors": 25000, "storage_gb": 2.5}
        trends_response = {"data": [{"date": "2024-01-01", "value": 100}]}
        anomalies_response = {"anomalies": [{"id": "anom_1", "severity": "medium"}]}
        export_response = {"report_id": "rpt_final", "status": "generating"}
        
        analytics_client.client.get.side_effect = [
            usage_response,
            performance_response,
            storage_response,
            costs_response,
            trends_response,
            anomalies_response
        ]
        analytics_client.client.post.return_value = export_response
        
        # Get usage analytics
        usage = analytics_client.get_usage(project_id="proj_comprehensive")
        assert usage == usage_response
        
        # Get performance metrics
        performance = analytics_client.get_performance_metrics(
            project_id="proj_comprehensive",
            metric_type="latency"
        )
        assert performance == performance_response
        
        # Get storage statistics
        storage = analytics_client.get_storage_stats(project_id="proj_comprehensive")
        assert storage == storage_response
        
        # Get cost analysis
        costs = analytics_client.get_cost_analysis(project_id="proj_comprehensive")
        assert costs == costs_response
        
        # Get trend data
        trends = analytics_client.get_trends(
            metric="queries",
            project_id="proj_comprehensive"
        )
        assert trends == trends_response["data"]
        
        # Get anomalies
        anomalies = analytics_client.get_anomalies(
            project_id="proj_comprehensive",
            severity="medium"
        )
        assert anomalies == anomalies_response["anomalies"]
        
        # Export comprehensive report
        report = analytics_client.export_report(
            report_type="detailed",
            project_id="proj_comprehensive",
            format="pdf"
        )
        assert report == export_response
    
    def test_time_series_analysis(self, analytics_client):
        """Test time series analysis across different periods."""
        # Mock responses for different time periods
        daily_data = {"data": [{"date": "2024-01-01", "vectors": 1000}]}
        weekly_data = {"data": [{"week": "2024-W01", "vectors": 7000}]}
        monthly_data = {"data": [{"month": "2024-01", "vectors": 30000}]}
        
        analytics_client.client.get.side_effect = [daily_data, weekly_data, monthly_data]
        
        # Daily trends
        daily_trends = analytics_client.get_trends("vectors", period=7)
        assert daily_trends == daily_data["data"]
        
        # Weekly trends
        weekly_trends = analytics_client.get_trends("vectors", period=30)
        assert weekly_trends == weekly_data["data"]
        
        # Monthly trends
        monthly_trends = analytics_client.get_trends("vectors", period=365)
        assert monthly_trends == monthly_data["data"]
    
    def test_multi_project_analytics(self, analytics_client):
        """Test analytics across multiple projects."""
        projects = ["proj_1", "proj_2", "proj_3"]
        
        # Mock responses for each project
        project_responses = [
            {"vectors_stored": 1000 + i * 500, "queries_executed": 500 + i * 250}
            for i in range(len(projects))
        ]
        
        analytics_client.client.get.side_effect = project_responses
        
        project_analytics = []
        for i, project_id in enumerate(projects):
            usage = analytics_client.get_usage(project_id=project_id)
            project_analytics.append({
                "project_id": project_id,
                "usage": usage
            })
            assert usage == project_responses[i]
        
        assert len(project_analytics) == 3
    
    def test_granularity_variations(self, analytics_client):
        """Test analytics with different granularities."""
        granularities = ["hourly", "daily", "weekly", "monthly"]
        
        mock_responses = [
            {"granularity": granularity, "data_points": 24 if granularity == "hourly" else 30}
            for granularity in granularities
        ]
        
        analytics_client.client.get.side_effect = mock_responses
        
        for i, granularity in enumerate(granularities):
            result = analytics_client.get_usage(granularity=granularity)
            assert result == mock_responses[i]
    
    def test_cost_optimization_analysis(self, analytics_client):
        """Test cost optimization analysis workflow."""
        # Current costs
        current_costs = {
            "storage_cost": 50.00,
            "compute_cost": 100.00,
            "total_cost": 150.00,
            "optimization_potential": 25.00
        }
        
        # Usage patterns
        usage_patterns = {
            "peak_hours": ["09:00-12:00", "14:00-17:00"],
            "low_usage_periods": ["22:00-06:00"],
            "storage_efficiency": 0.75
        }
        
        # Performance vs cost correlation
        performance_cost = {
            "cost_per_query": 0.001,
            "latency_cost_ratio": 0.5,
            "optimization_recommendations": [
                "Implement caching for frequently accessed vectors",
                "Consider batch processing during low-usage periods"
            ]
        }
        
        analytics_client.client.get.side_effect = [
            current_costs,
            usage_patterns,
            performance_cost
        ]
        
        # Analyze current costs
        costs = analytics_client.get_cost_analysis(
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now()
        )
        assert costs == current_costs
        
        # Analyze usage for optimization
        usage = analytics_client.get_usage(granularity="hourly")
        assert usage == usage_patterns
        
        # Get performance insights for cost optimization
        performance = analytics_client.get_performance_metrics(metric_type="all")
        assert performance == performance_cost
    
    def test_anomaly_detection_workflow(self, analytics_client):
        """Test anomaly detection and analysis workflow."""
        # Different severity anomalies
        critical_anomalies = {
            "anomalies": [
                {
                    "id": "crit_1",
                    "type": "latency_spike",
                    "severity": "critical",
                    "impact": "high",
                    "detected_at": "2024-01-01T10:00:00Z"
                }
            ]
        }
        
        high_anomalies = {
            "anomalies": [
                {
                    "id": "high_1",
                    "type": "query_volume_spike",
                    "severity": "high",
                    "impact": "medium"
                },
                {
                    "id": "high_2",
                    "type": "error_rate_increase",
                    "severity": "high",
                    "impact": "medium"
                }
            ]
        }
        
        all_anomalies = {
            "anomalies": critical_anomalies["anomalies"] + high_anomalies["anomalies"]
        }
        
        analytics_client.client.get.side_effect = [
            critical_anomalies,
            high_anomalies,
            all_anomalies
        ]
        
        # Get critical anomalies first
        critical = analytics_client.get_anomalies(severity="critical")
        assert len(critical) == 1
        assert critical[0]["severity"] == "critical"
        
        # Get high severity anomalies
        high = analytics_client.get_anomalies(severity="high")
        assert len(high) == 2
        
        # Get all anomalies for comprehensive analysis
        all_results = analytics_client.get_anomalies(severity="all")
        assert len(all_results) == 3
    
    def test_report_generation_scenarios(self, analytics_client):
        """Test different report generation scenarios."""
        report_scenarios = [
            {
                "type": "summary",
                "format": "json",
                "expected_fields": ["overview", "key_metrics", "summary"]
            },
            {
                "type": "detailed",
                "format": "pdf",
                "expected_fields": ["detailed_analysis", "charts", "recommendations"]
            },
            {
                "type": "custom",
                "format": "csv",
                "expected_fields": ["raw_data", "custom_metrics"]
            }
        ]
        
        mock_responses = [
            {
                "report_id": f"rpt_{scenario['type']}",
                "format": scenario["format"],
                "status": "completed",
                "download_url": f"https://api.ainative.studio/reports/rpt_{scenario['type']}.{scenario['format']}"
            }
            for scenario in report_scenarios
        ]
        
        analytics_client.client.post.side_effect = mock_responses
        
        for i, scenario in enumerate(report_scenarios):
            result = analytics_client.export_report(
                report_type=scenario["type"],
                format=scenario["format"],
                project_id="proj_reports"
            )
            
            assert result["report_id"] == f"rpt_{scenario['type']}"
            assert result["format"] == scenario["format"]
            assert "download_url" in result
    
    def test_error_handling_scenarios(self, analytics_client):
        """Test error handling in analytics operations."""
        from ainative.exceptions import APIError
        
        # Test various error scenarios
        error_scenarios = [
            (404, "Project not found"),
            (400, "Invalid date range"),
            (429, "Rate limit exceeded"),
            (500, "Internal server error")
        ]
        
        for status_code, error_message in error_scenarios:
            analytics_client.client.get.side_effect = APIError(
                error_message, 
                status_code=status_code
            )
            
            with pytest.raises(APIError) as exc_info:
                analytics_client.get_usage(project_id="invalid_project")
            
            assert exc_info.value.status_code == status_code
            
            # Reset for next test
            analytics_client.client.get.side_effect = None
    
    def test_date_range_validation_scenarios(self, analytics_client):
        """Test various date range scenarios."""
        analytics_client.client.get.return_value = {"valid": True}
        
        # Test different date range combinations
        base_date = datetime(2024, 1, 1)
        date_scenarios = [
            # Same day
            (base_date, base_date),
            # One week
            (base_date, base_date + timedelta(days=7)),
            # One month
            (base_date, base_date + timedelta(days=30)),
            # One year
            (base_date, base_date + timedelta(days=365)),
            # Custom range
            (datetime(2024, 3, 15), datetime(2024, 8, 20))
        ]
        
        for start_date, end_date in date_scenarios:
            analytics_client.get_usage(
                start_date=start_date,
                end_date=end_date
            )
            
            call_args = analytics_client.client.get.call_args
            params = call_args[1]["params"]
            
            assert params["start_date"] == start_date.isoformat()
            assert params["end_date"] == end_date.isoformat()
            
            analytics_client.client.get.reset_mock()