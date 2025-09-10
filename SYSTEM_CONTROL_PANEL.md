# Aura V24 System Control Panel Documentation

## Overview

The Aura V24 System Control Panel is a professional, enterprise-grade control center for managing the complete Aura autonomous design system. It provides comprehensive service lifecycle management, real-time monitoring, diagnostics, and configuration validation.

## Features

### 🚀 Service Management
- **Complete Lifecycle Control**: Start, stop, restart all services with dependency management
- **Health Monitoring**: Real-time health checks with detailed status reporting
- **Process Tracking**: Monitor PID, memory usage, CPU consumption for each service
- **Graceful Shutdown**: Proper service termination with configurable timeouts

### 🔍 System Diagnostics
- **Configuration Validation**: Comprehensive validation of all system settings
- **Port Conflict Detection**: Automatic detection and reporting of port conflicts
- **Network Connectivity**: Test internal and external network connectivity
- **Resource Monitoring**: CPU, memory, disk usage tracking
- **Service Dependencies**: Verify all service dependencies are met

### 📊 Monitoring & Analytics
- **Real-time Dashboard**: Live system status with automatic refresh
- **Performance Metrics**: Track service performance and resource usage
- **Log Aggregation**: Centralized log viewing and analysis
- **Alert System**: Intelligent alerting for system issues

### ⚙️ Configuration Management
- **Centralized Environment**: Complete .env configuration system
- **Variable Validation**: Type checking and validation for all settings
- **Fallback Mechanisms**: Graceful degradation when configuration is missing
- **Hot Reloading**: Dynamic configuration updates without service restart

## Quick Start

### 1. Installation

```bash
# Install required dependencies
pip install python-dotenv psutil requests

# Copy environment configuration
cp .env.example .env

# Edit configuration for your system
nano .env
```

### 2. Basic Usage

```bash
# Check system status
python system_control_panel.py status

# Run health checks
python system_control_panel.py health

# Start all services
python system_control_panel.py start

# Monitor system in real-time
python system_control_panel.py monitor

# Run full diagnostics
python system_control_panel.py diagnose
```

## Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `start` | Start all services in dependency order | `python system_control_panel.py start` |
| `stop` | Stop all services gracefully | `python system_control_panel.py stop` |
| `restart` | Restart all services | `python system_control_panel.py restart` |
| `status` | Show current service status | `python system_control_panel.py status` |
| `health` | Run health checks on all services | `python system_control_panel.py health` |
| `diagnose` | Comprehensive system diagnostics | `python system_control_panel.py diagnose` |
| `monitor` | Start real-time monitoring dashboard | `python system_control_panel.py monitor` |
| `config` | Validate system configuration | `python system_control_panel.py config` |
| `logs` | View system or service logs | `python system_control_panel.py logs [service]` |

## Configuration Guide

### Environment Variables

The system uses a comprehensive `.env` file for configuration. Key sections include:

#### Core System Settings
```bash
ENVIRONMENT=development
DEBUG_MODE=true
LOG_LEVEL=INFO
SYSTEM_NAME=Aura V24 Autonomous Design Engine
```

#### LM Studio Configuration
```bash
LM_STUDIO_HOST=localhost
LM_STUDIO_PORT=1234
LM_STUDIO_MODEL_NAME=meta-llama-3.1-8b-instruct
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
```

#### Service Ports (Prevent Conflicts)
```bash
LM_STUDIO_PORT=1234         # External LM Studio server
AI_SERVER_PORT=8002         # Main AI server with Shap-E
BACKEND_PORT=8001           # Backend orchestrator
SANDBOX_SERVER_PORT=8003    # Sandbox testing server
```

#### Blender Integration
```bash
# Windows
BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.5\blender.exe

# Linux/Mac
BLENDER_PATH=/usr/bin/blender
```

### Configuration Validation

The system automatically validates your configuration:

```bash
python system_control_panel.py config
```

Common validation issues:
- **Blender Path**: Ensure Blender executable exists and is accessible
- **Port Conflicts**: Each service must use a unique port
- **Directory Permissions**: Output and cache directories must be writable
- **API Keys**: Validate external service credentials

## Services Architecture

### Service Dependencies

```
┌─────────────┐
│ LM Studio   │ ← External service (port 1234)
│ (External)  │
└─────────────┘
       │
       ▼
┌─────────────┐    ┌─────────────┐
│ Backend     │    │ AI Server   │
│ (port 8001) │    │ (port 8002) │
└─────────────┘    └─────────────┘
       │                   │
       ▼                   ▼
┌─────────────────────────────────┐
│ Blender Integration             │
│ (Native addon execution)        │
└─────────────────────────────────┘
```

### Service Descriptions

| Service | Port | Description | Health Endpoint |
|---------|------|-------------|-----------------|
| LM Studio | 1234 | External LLM service for text generation | `/v1/models` |
| AI Server | 8002 | Shap-E integration for 3D model generation | `/health` |
| Backend | 8001 | FastAPI orchestrator for workflow management | `/health` |
| Sandbox | 8003 | Testing environment (optional) | `/health` |

## Health Monitoring

### Health Check Levels

1. **Port Connectivity**: Is the service port responding?
2. **HTTP Health**: Does the health endpoint return 200 OK?
3. **Service Logic**: Are internal components functioning?
4. **Dependencies**: Are required services available?

### Health Status Indicators

| Symbol | Status | Description |
|--------|--------|-------------|
| 🟢 | Healthy | Service fully operational |
| 🟡 | Degraded | Service running but with issues |
| 🔴 | Unhealthy | Service down or failing |
| ⚪ | Unknown | Unable to determine status |

## Monitoring Dashboard

### Real-time Status Display

```
🤖 Aura V24 System Status - 2025-09-10 17:10:38
================================================================================
Service         Status     Health   Port     PID      Memory    
--------------------------------------------------------------------------------
lm_studio       🟢 UP      ✅        🟢      1234     -         
ai_server       🟢 UP      ✅        🟢      5678     245.3MB   
backend         🟢 UP      ✅        🟢      9012     89.7MB    
sandbox         🔴 DOWN    ❌        🔴      -        -         

💻 System Resources:
  CPU: 15.2%
  Memory: 32.1%
  Disk: 63.8%
```

### Monitoring Options

```bash
# Start monitoring with default 30-second interval
python system_control_panel.py monitor

# Custom interval (60 seconds)
python system_control_panel.py monitor --interval 60
```

## Diagnostics

### Comprehensive System Analysis

The diagnostics system provides deep insights into:

- **Configuration Issues**: Missing or invalid settings
- **Network Connectivity**: Internal and external reachability
- **Resource Availability**: CPU, memory, disk space
- **Service Health**: Detailed health analysis
- **Dependency Validation**: Service dependency verification

### Sample Diagnostic Output

```json
{
  "timestamp": "2025-09-10 17:10:51.777017",
  "configuration": {
    "status": "valid",
    "issues": {
      "missing": [],
      "invalid": [],
      "warnings": ["Low memory limit may affect performance"]
    }
  },
  "network": {
    "localhost_reachable": true,
    "internet_reachable": true
  },
  "services": {
    "lm_studio": {
      "configured": true,
      "port_available": false,
      "healthy": true
    }
  },
  "resources": {
    "cpu_count": 4,
    "memory_total_gb": 15.62,
    "disk_free_gb": 25.88,
    "python_version": "3.12.3"
  },
  "issues": []
}
```

## Troubleshooting

### Common Issues

#### 1. Port Conflicts
**Problem**: Service fails to start due to port already in use
**Solution**: 
```bash
# Check port usage
netstat -tulpn | grep :8002

# Update .env to use different port
echo "AI_SERVER_PORT=8003" >> .env
```

#### 2. Blender Path Issues
**Problem**: Blender executable not found
**Solution**:
```bash
# Find Blender installation
which blender  # Linux/Mac
where blender  # Windows

# Update .env with correct path
echo "BLENDER_PATH=/usr/local/bin/blender" >> .env
```

#### 3. Permission Errors
**Problem**: Cannot create output directories
**Solution**:
```bash
# Fix permissions
chmod 755 output/ models/ cache/

# Or change to user-writable location
echo "OUTPUT_DIR=~/aura_output" >> .env
```

#### 4. LM Studio Connection
**Problem**: Cannot connect to LM Studio
**Solution**:
```bash
# Verify LM Studio is running
curl http://localhost:1234/v1/models

# Check configuration
python system_control_panel.py config

# Update URL if needed
echo "LM_STUDIO_URL=http://localhost:1234/v1/chat/completions" >> .env
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Set debug mode in .env
echo "DEBUG_MODE=true" >> .env
echo "LOG_LEVEL=DEBUG" >> .env

# Run with verbose output
python system_control_panel.py start
```

## Advanced Usage

### Custom Service Configuration

Add your own services to the control panel:

```python
# In system_control_panel.py, add to _setup_services():
self.services['my_service'] = ServiceConfig(
    name='my_service',
    command=[sys.executable, 'my_service.py'],
    cwd='.',
    host='localhost',
    port=8004,
    health_endpoint='/health',
    depends_on=['ai_server'],
    required=False
)
```

### Environment Validation Rules

Customize validation in `config.py`:

```python
def validate_custom_config(self) -> Dict[str, List[str]]:
    issues = {'missing': [], 'invalid': [], 'warnings': []}
    
    # Add custom validation logic
    if not self.get('MY_API_KEY'):
        issues['missing'].append('MY_API_KEY is required')
    
    return issues
```

### Monitoring Integration

Export metrics for external monitoring:

```bash
# Enable metrics endpoint
echo "METRICS_ENABLED=true" >> .env
echo "METRICS_PORT=9090" >> .env

# Access Prometheus-style metrics
curl http://localhost:9090/metrics
```

## Security Considerations

### Configuration Security

- **Never commit `.env` files**: Already added to `.gitignore`
- **Use secure file permissions**: `chmod 600 .env`
- **Rotate API keys regularly**: Update and restart services
- **Validate input**: All configuration values are validated

### Network Security

- **Bind to localhost**: Services default to localhost for security
- **Use HTTPS**: Configure TLS for production deployments
- **API rate limiting**: Built-in rate limiting for external APIs
- **CORS configuration**: Properly configured CORS origins

## Production Deployment

### Systemd Service

Create a systemd service for automatic startup:

```ini
[Unit]
Description=Aura V24 System Control Panel
After=network.target

[Service]
Type=simple
User=aura
WorkingDirectory=/opt/aura
ExecStart=/opt/aura/venv/bin/python system_control_panel.py start
ExecStop=/opt/aura/venv/bin/python system_control_panel.py stop
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Docker Support

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8001 8002 8003

CMD ["python", "system_control_panel.py", "start"]
```

### Load Balancing

For high-availability deployments:

```bash
# Multiple AI server instances
AI_SERVER_PORT=8002,8003,8004
AI_SERVER_WORKERS=3

# Load balancer configuration
LOAD_BALANCER_ENABLED=true
LOAD_BALANCER_STRATEGY=round_robin
```

## API Reference

### Configuration API

```python
from config import config

# Get configuration values
lm_studio_url = config.get('LM_STUDIO_URL')
port = config.get_int('AI_SERVER_PORT', 8002)
debug = config.get_bool('DEBUG_MODE', False)

# Service-specific configuration
ai_config = config.get_service_config('ai_server')
monitoring_config = config.get_monitoring_config()

# Validation
issues = config.validate_configuration()
```

### Control Panel API

```python
from system_control_panel import SystemControlPanel

# Initialize control panel
panel = SystemControlPanel()

# Service management
panel.start_service('ai_server')
panel.stop_service('ai_server')
panel.restart_all_services()

# Status and diagnostics
status = panel.get_system_status()
diagnostics = panel.run_diagnostics()
health = panel.check_service_health('ai_server')
```

## Contributing

### Adding New Services

1. Define service in `ServiceConfig`
2. Add health endpoint to service
3. Update documentation
4. Test with control panel

### Extending Diagnostics

1. Add validation logic to `config.py`
2. Implement diagnostic checks in `run_diagnostics()`
3. Update health check endpoints
4. Test thoroughly

## Support

For issues and questions:

1. Check the troubleshooting guide above
2. Run system diagnostics: `python system_control_panel.py diagnose`
3. Enable debug logging: Set `DEBUG_MODE=true` in `.env`
4. Review service logs: `python system_control_panel.py logs [service]`

---

*This documentation covers Aura V24 System Control Panel. For general Aura documentation, see the main README.md file.*