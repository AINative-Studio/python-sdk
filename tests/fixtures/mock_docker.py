"""
Mock Docker Fixtures for Testing

Provides reusable mock fixtures for Docker subprocess calls.
"""

import pytest
from unittest.mock import Mock, MagicMock
import subprocess


@pytest.fixture
def docker_compose_success():
    """Mock successful docker-compose command"""
    mock = Mock()
    mock.returncode = 0
    mock.stdout = "Success"
    mock.stderr = ""
    return mock


@pytest.fixture
def docker_compose_ps_all_running():
    """Mock docker-compose ps with all services running"""
    mock = Mock()
    mock.returncode = 0
    mock.stdout = """
NAME                SERVICE             STATUS              PORTS
zerodb-postgres     postgres            running             0.0.0.0:5432->5432/tcp
zerodb-qdrant       qdrant              running             0.0.0.0:6333->6333/tcp
zerodb-minio        minio               running             0.0.0.0:9000-9001->9000-9001/tcp
zerodb-redpanda     redpanda            running             0.0.0.0:9092->9092/tcp
zerodb-api          zerodb-api          running             0.0.0.0:8000->8000/tcp
zerodb-dashboard    dashboard           running             0.0.0.0:3000->3000/tcp
    """.strip()
    mock.stderr = ""
    return mock


@pytest.fixture
def docker_compose_ps_some_stopped():
    """Mock docker-compose ps with some services stopped"""
    mock = Mock()
    mock.returncode = 0
    mock.stdout = """
NAME                SERVICE             STATUS              PORTS
zerodb-postgres     postgres            running             0.0.0.0:5432->5432/tcp
zerodb-qdrant       qdrant              exited (1)
zerodb-minio        minio               exited (137)
zerodb-redpanda     redpanda            running             0.0.0.0:9092->9092/tcp
zerodb-api          zerodb-api          exited (1)
    """.strip()
    mock.stderr = ""
    return mock


@pytest.fixture
def docker_compose_ps_empty():
    """Mock docker-compose ps with no services"""
    mock = Mock()
    mock.returncode = 0
    mock.stdout = "NAME                SERVICE             STATUS              PORTS"
    mock.stderr = ""
    return mock


@pytest.fixture
def docker_daemon_not_running():
    """Mock Docker daemon not running error"""
    error = subprocess.CalledProcessError(
        1,
        'docker-compose',
        stderr="Cannot connect to the Docker daemon. Is the docker daemon running?"
    )
    return error


@pytest.fixture
def docker_port_already_allocated():
    """Mock port already in use error"""
    error = subprocess.CalledProcessError(
        1,
        'docker-compose',
        stderr="Bind for 0.0.0.0:5432 failed: port is already allocated"
    )
    return error


@pytest.fixture
def docker_insufficient_permissions():
    """Mock insufficient permissions error"""
    error = subprocess.CalledProcessError(
        1,
        'docker-compose',
        stderr="permission denied while trying to connect to the Docker daemon socket"
    )
    return error


@pytest.fixture
def docker_compose_logs_output():
    """Mock docker-compose logs output"""
    mock = Mock()
    mock.returncode = 0
    mock.stdout = """
postgres    | 2025-12-28 10:00:00 UTC [1] LOG:  database system is ready to accept connections
qdrant      | 2025-12-28 10:00:01 INFO: Starting Qdrant server
minio       | 2025-12-28 10:00:02 INFO: MinIO Object Storage Server
redpanda    | 2025-12-28 10:00:03 INFO: Started Redpanda broker
zerodb-api  | 2025-12-28 10:00:04 INFO: Application startup complete
    """.strip()
    mock.stderr = ""
    return mock


@pytest.fixture
def docker_compose_stats():
    """Mock docker-compose stats output"""
    mock = Mock()
    mock.returncode = 0
    mock.stdout = """
CONTAINER           CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O
zerodb-postgres     2.5%      128MiB / 2GiB         6.4%      1.2MB / 800kB     10MB / 5MB
zerodb-qdrant       1.2%      256MiB / 2GiB         12.8%     800kB / 500kB     5MB / 2MB
zerodb-minio        0.8%      64MiB / 1GiB          6.4%      500kB / 300kB     2MB / 1MB
zerodb-redpanda     1.5%      192MiB / 2GiB         9.6%      1MB / 600kB       8MB / 4MB
zerodb-api          3.0%      512MiB / 2GiB         25.6%     2MB / 1.5MB       15MB / 10MB
    """.strip()
    mock.stderr = ""
    return mock


@pytest.fixture
def docker_health_check_healthy():
    """Mock healthy health check response"""
    return {
        'postgres': {'status': 'healthy', 'checks': {'connection': True}},
        'qdrant': {'status': 'healthy', 'checks': {'api': True}},
        'minio': {'status': 'healthy', 'checks': {'api': True}},
        'redpanda': {'status': 'healthy', 'checks': {'kafka': True}},
        'zerodb-api': {'status': 'healthy', 'checks': {'api': True, 'database': True}}
    }


@pytest.fixture
def docker_health_check_unhealthy():
    """Mock unhealthy health check response"""
    return {
        'postgres': {'status': 'healthy', 'checks': {'connection': True}},
        'qdrant': {'status': 'unhealthy', 'checks': {'api': False}, 'error': 'Connection refused'},
        'minio': {'status': 'healthy', 'checks': {'api': True}},
        'redpanda': {'status': 'degraded', 'checks': {'kafka': True}, 'warning': 'High memory usage'},
        'zerodb-api': {'status': 'unhealthy', 'checks': {'api': True, 'database': False}, 'error': 'Database connection failed'}
    }


class DockerComposeMock:
    """
    Comprehensive Docker Compose mock helper class.

    Usage:
        @pytest.fixture
        def docker_mock():
            return DockerComposeMock()

        def test_something(docker_mock):
            docker_mock.set_running_services(['postgres', 'qdrant'])
            # ... test code ...
    """

    def __init__(self):
        self.services = {}
        self.logs = {}

    def set_running_services(self, service_names):
        """Set which services are running"""
        for name in service_names:
            self.services[name] = 'running'

    def set_stopped_services(self, service_names):
        """Set which services are stopped"""
        for name in service_names:
            self.services[name] = 'exited (1)'

    def add_log_entry(self, service, message):
        """Add log entry for service"""
        if service not in self.logs:
            self.logs[service] = []
        self.logs[service].append(message)

    def generate_ps_output(self):
        """Generate docker-compose ps output"""
        lines = ["NAME                SERVICE             STATUS              PORTS"]

        port_map = {
            'postgres': '0.0.0.0:5432->5432/tcp',
            'qdrant': '0.0.0.0:6333->6333/tcp',
            'minio': '0.0.0.0:9000-9001->9000-9001/tcp',
            'redpanda': '0.0.0.0:9092->9092/tcp',
            'zerodb-api': '0.0.0.0:8000->8000/tcp',
            'dashboard': '0.0.0.0:3000->3000/tcp'
        }

        for service, status in self.services.items():
            container_name = f"zerodb-{service}"
            ports = port_map.get(service, '')
            if status != 'running':
                ports = ''
            lines.append(f"{container_name:20}{service:20}{status:20}{ports}")

        return '\n'.join(lines)

    def generate_logs_output(self):
        """Generate docker-compose logs output"""
        lines = []
        for service, entries in self.logs.items():
            for entry in entries:
                lines.append(f"{service:15} | {entry}")
        return '\n'.join(lines)


@pytest.fixture
def docker_compose_helper():
    """Helper fixture for creating custom Docker Compose mocks"""
    return DockerComposeMock()
