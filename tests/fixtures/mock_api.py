"""
Mock API Response Fixtures for Testing

Provides reusable mock fixtures for AINative API responses.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta


@pytest.fixture
def mock_project_list_response():
    """Mock project list API response"""
    return {
        'projects': [
            {
                'id': 'proj_local_1',
                'name': 'Local Dev Project',
                'description': 'Local development project',
                'status': 'active',
                'created_at': '2025-12-01T10:00:00Z',
                'updated_at': '2025-12-28T09:00:00Z',
                'row_count': 100
            },
            {
                'id': 'proj_local_2',
                'name': 'Test Project',
                'description': 'Test project',
                'status': 'active',
                'created_at': '2025-12-15T14:00:00Z',
                'updated_at': '2025-12-28T10:00:00Z',
                'row_count': 50
            }
        ],
        'total': 2,
        'has_more': False
    }


@pytest.fixture
def mock_table_list_response():
    """Mock table list API response"""
    return {
        'tables': [
            {
                'id': 'table_1',
                'name': 'users',
                'schema': {
                    'fields': {
                        'id': 'uuid',
                        'email': 'string',
                        'name': 'string',
                        'created_at': 'timestamp'
                    },
                    'indexes': ['email']
                },
                'row_count': 100,
                'created_at': '2025-12-01T10:00:00Z',
                'updated_at': '2025-12-28T09:00:00Z'
            },
            {
                'id': 'table_2',
                'name': 'products',
                'schema': {
                    'fields': {
                        'id': 'uuid',
                        'name': 'string',
                        'price': 'number',
                        'in_stock': 'boolean'
                    },
                    'indexes': ['name']
                },
                'row_count': 50,
                'created_at': '2025-12-10T12:00:00Z',
                'updated_at': '2025-12-28T08:00:00Z'
            }
        ]
    }


@pytest.fixture
def mock_vector_stats_response():
    """Mock vector statistics API response"""
    return {
        'total_vectors': 1000,
        'dimensions': 1536,
        'namespaces': {
            'default': {
                'count': 800,
                'size_bytes': 1234567
            },
            'embeddings': {
                'count': 200,
                'size_bytes': 308642
            }
        },
        'index_type': 'hnsw',
        'distance_metric': 'cosine'
    }


@pytest.fixture
def mock_sync_diff_response():
    """Mock sync diff API response"""
    return {
        'schema_diff': {
            'tables_added': ['products', 'orders'],
            'tables_removed': ['old_logs'],
            'tables_modified': [
                {
                    'table': 'users',
                    'columns_added': ['phone'],
                    'columns_removed': ['legacy_id'],
                    'columns_modified': [
                        {'column': 'email', 'old_type': 'string', 'new_type': 'string(255)'}
                    ]
                }
            ]
        },
        'data_diff': {
            'users': {
                'rows_added': 5,
                'rows_updated': 3,
                'rows_deleted': 2
            },
            'products': {
                'rows_added': 10,
                'rows_updated': 0,
                'rows_deleted': 0
            }
        },
        'vectors_diff': {
            'default': {
                'vectors_added': 15,
                'vectors_removed': 3
            }
        },
        'summary': {
            'total_changes': 38,
            'estimated_sync_time_seconds': 5.2
        }
    }


@pytest.fixture
def mock_health_check_response():
    """Mock health check API response"""
    return {
        'status': 'healthy',
        'version': '1.0.0',
        'services': {
            'database': {
                'status': 'healthy',
                'response_time_ms': 2.3,
                'connections': 15,
                'max_connections': 100
            },
            'vector_store': {
                'status': 'healthy',
                'response_time_ms': 1.8,
                'total_vectors': 1000
            },
            'object_storage': {
                'status': 'healthy',
                'response_time_ms': 5.1,
                'total_files': 25,
                'total_size_bytes': 10485760
            }
        },
        'timestamp': '2025-12-28T10:00:00Z'
    }


@pytest.fixture
def mock_memory_list_response():
    """Mock memory list API response"""
    return {
        'memories': [
            {
                'id': 'mem_1',
                'content': 'User prefers dark mode',
                'tags': ['preference', 'ui'],
                'priority': 'low',
                'created_at': '2025-12-28T09:00:00Z'
            },
            {
                'id': 'mem_2',
                'content': 'Critical bug in payment processing',
                'tags': ['bug', 'urgent'],
                'priority': 'critical',
                'created_at': '2025-12-28T10:00:00Z'
            }
        ],
        'total': 2
    }


@pytest.fixture
def mock_event_list_response():
    """Mock event list API response"""
    return {
        'events': [
            {
                'id': 'evt_1',
                'type': 'user.created',
                'data': {'user_id': 'user_123', 'email': 'test@example.com'},
                'timestamp': '2025-12-28T09:00:00Z'
            },
            {
                'id': 'evt_2',
                'type': 'order.placed',
                'data': {'order_id': 'order_456', 'total': 99.99},
                'timestamp': '2025-12-28T09:30:00Z'
            }
        ],
        'total': 2
    }


class APIResponseBuilder:
    """
    Helper class for building custom API response mocks.

    Usage:
        builder = APIResponseBuilder()
        response = builder.table('users').rows(100).schema({'id': 'uuid'}).build()
    """

    def __init__(self):
        self.data = {}

    def table(self, name, table_id=None):
        """Add table to response"""
        self.data.setdefault('tables', []).append({
            'id': table_id or f'table_{name}',
            'name': name,
            'schema': {},
            'row_count': 0,
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'updated_at': datetime.utcnow().isoformat() + 'Z'
        })
        return self

    def rows(self, count):
        """Set row count for last table"""
        if self.data.get('tables'):
            self.data['tables'][-1]['row_count'] = count
        return self

    def schema(self, fields):
        """Set schema for last table"""
        if self.data.get('tables'):
            self.data['tables'][-1]['schema'] = {'fields': fields, 'indexes': []}
        return self

    def vector_stats(self, total, dimensions=1536):
        """Add vector statistics"""
        self.data['vector_stats'] = {
            'total_vectors': total,
            'dimensions': dimensions,
            'namespaces': {'default': {'count': total, 'size_bytes': total * dimensions * 4}}
        }
        return self

    def health_status(self, status='healthy'):
        """Add health status"""
        self.data['health'] = {
            'status': status,
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        return self

    def build(self):
        """Build and return the response"""
        return self.data


@pytest.fixture
def api_response_builder():
    """Fixture for API response builder"""
    return APIResponseBuilder()


@pytest.fixture
def mock_client_with_tables(mock_table_list_response):
    """Mock client pre-configured with table list (v3.0 signature with project_id)"""
    client = MagicMock()
    # Update mocks to match v3.0 API signature: list_tables(project_id, ...)
    client.zerodb.tables.list_tables.return_value = mock_table_list_response
    client.zerodb.tables.query_rows.return_value = {
        'rows': [
            {'id': '1', 'email': 'user1@example.com'},
            {'id': '2', 'email': 'user2@example.com'}
        ],
        'total': 2
    }
    return client


@pytest.fixture
def mock_client_with_vectors(mock_vector_stats_response):
    """Mock client pre-configured with vector stats"""
    client = MagicMock()
    client.zerodb.vectors.describe_index_stats.return_value = mock_vector_stats_response
    client.zerodb.vectors.search.return_value = [
        {'id': 'vec_1', 'score': 0.95, 'metadata': {'text': 'Sample 1'}},
        {'id': 'vec_2', 'score': 0.87, 'metadata': {'text': 'Sample 2'}}
    ]
    return client


@pytest.fixture
def mock_client_empty():
    """Mock client with empty responses (v3.0 signatures with project_id)"""
    client = MagicMock()
    client.zerodb.tables.list_tables.return_value = {'tables': []}
    client.zerodb.vectors.describe_index_stats.return_value = {
        'total_vectors': 0,
        'dimensions': 1536,
        'namespaces': {}
    }
    client.zerodb.memory.list.return_value = {'memories': [], 'total': 0}
    return client


@pytest.fixture
def mock_api_error_responses():
    """Mock API error responses"""
    return {
        'not_found': {
            'status_code': 404,
            'detail': 'Resource not found'
        },
        'unauthorized': {
            'status_code': 401,
            'detail': 'Invalid API key'
        },
        'rate_limited': {
            'status_code': 429,
            'detail': 'Rate limit exceeded'
        },
        'server_error': {
            'status_code': 500,
            'detail': 'Internal server error'
        },
        'validation_error': {
            'status_code': 422,
            'detail': 'Validation error',
            'errors': [
                {'field': 'email', 'message': 'Invalid email format'}
            ]
        }
    }
