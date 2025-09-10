#!/usr/bin/env python3
"""
Aura V24 System Control Panel
=============================

Professional and robust full system startup control panel that serves as the true
control center for starting, monitoring, and analyzing the entire Aura system.
Provides comprehensive diagnostic capabilities, health checks, and system insights.

Features:
- Complete service lifecycle management
- Real-time health monitoring and diagnostics
- Port availability and conflict detection
- System resource monitoring (CPU, Memory, GPU)
- Service dependency management
- Configuration validation
- Log aggregation and analysis
- Performance metrics collection
- Network connectivity testing
- Interactive control interface

Usage:
    python system_control_panel.py [command] [options]
    
Commands:
    start    - Start all services
    stop     - Stop all services  
    restart  - Restart all services
    status   - Show service status
    health   - Run health checks
    diagnose - Run comprehensive diagnostics
    monitor  - Start monitoring dashboard
    config   - Validate configuration
    logs     - View system logs
    
Author: Aura V24 Autonomous System
"""

import os
import sys
import time
import json
import signal
import socket
import logging
import argparse
import threading
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass

# System monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("WARNING: psutil not available - resource monitoring disabled")

# Network utilities  
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("WARNING: requests not available - network checks disabled")

# Load environment configuration
try:
    from ..config import config, validate_system_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("WARNING: config module not available - using defaults")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('system_control.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    """Configuration for a managed service."""
    name: str
    command: List[str]
    cwd: str
    host: str
    port: int
    health_endpoint: Optional[str] = None
    depends_on: List[str] = None
    startup_timeout: int = 30
    shutdown_timeout: int = 10
    environment: Dict[str, str] = None
    required: bool = True

@dataclass
class ServiceStatus:
    """Current status of a service."""
    name: str
    running: bool = False
    pid: Optional[int] = None
    port_open: bool = False
    healthy: bool = False
    last_health_check: Optional[datetime] = None
    errors: List[str] = None
    start_time: Optional[datetime] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None

class SystemControlPanel:
    """Main system control panel for Aura V24."""
    
    def __init__(self):
        """Initialize the control panel."""
        self.services: Dict[str, ServiceConfig] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.status: Dict[str, ServiceStatus] = {}
        self.monitoring_active = False
        self.shutdown_requested = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self._setup_services()
        
        logger.info("🚀 Aura V24 System Control Panel initialized")
    
    def _setup_services(self):
        """Setup service configurations."""
        if CONFIG_AVAILABLE:
            # LM Studio (external service - we monitor but don't start)
            self.services['lm_studio'] = ServiceConfig(
                name='lm_studio',
                command=[],  # External service
                cwd='.',
                host=config.get('LM_STUDIO_HOST', 'localhost'),
                port=config.get_int('LM_STUDIO_PORT', 1234),
                health_endpoint='/v1/models',
                required=True
            )
            
            # AI Server
            self.services['ai_server'] = ServiceConfig(
                name='ai_server',
                command=[sys.executable, 'ai_server.py'],
                cwd='.',
                host=config.get('AI_SERVER_HOST', '0.0.0.0'),
                port=config.get_int('AI_SERVER_PORT', 8002),
                health_endpoint='/health',
                startup_timeout=60,
                required=True
            )
            
            # Backend Orchestrator  
            self.services['backend'] = ServiceConfig(
                name='backend',
                command=[sys.executable, '-m', 'uvicorn', 'backend.main:app', 
                        '--host', config.get('BACKEND_HOST', 'localhost'),
                        '--port', str(config.get_int('BACKEND_PORT', 8001))],
                cwd='.',
                host=config.get('BACKEND_HOST', 'localhost'),
                port=config.get_int('BACKEND_PORT', 8001),
                health_endpoint='/health',
                depends_on=['lm_studio'],
                required=True
            )
            
            # Sandbox Server (optional)
            if config.get_bool('SANDBOX_MODE', False):
                self.services['sandbox'] = ServiceConfig(
                    name='sandbox',
                    command=[sys.executable, 'sandbox_3d_server.py'],
                    cwd='.',
                    host=config.get('SANDBOX_SERVER_HOST', '0.0.0.0'),
                    port=config.get_int('SANDBOX_SERVER_PORT', 8003),
                    health_endpoint='/health',
                    required=False
                )
        else:
            # Fallback configuration
            self._setup_default_services()
        
        # Initialize status tracking
        for service_name in self.services:
            self.status[service_name] = ServiceStatus(
                name=service_name,
                errors=[]
            )
    
    def _setup_default_services(self):
        """Setup default service configuration when config module unavailable."""
        logger.warning("Using default service configuration")
        
        self.services = {
            'lm_studio': ServiceConfig(
                name='lm_studio',
                command=[],
                cwd='.',
                host='localhost',
                port=1234,
                health_endpoint='/v1/models',
                required=True
            ),
            'ai_server': ServiceConfig(
                name='ai_server', 
                command=[sys.executable, 'ai_server.py'],
                cwd='.',
                host='0.0.0.0',
                port=8002,
                health_endpoint='/health',
                required=True
            )
        }
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
        self.stop_all_services()
        sys.exit(0)
    
    def check_port_available(self, host: str, port: int) -> bool:
        """Check if a port is available on the given host."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception as e:
            logger.debug(f"Port check failed for {host}:{port} - {e}")
            return False
    
    def check_service_health(self, service_name: str) -> bool:
        """Check health of a specific service."""
        if service_name not in self.services:
            return False
        
        service = self.services[service_name]
        status = self.status[service_name]
        
        # Check if port is responding
        port_open = self.check_port_available(service.host, service.port)
        status.port_open = port_open
        
        if not port_open:
            return False
        
        # Check health endpoint if available
        if service.health_endpoint and REQUESTS_AVAILABLE:
            try:
                url = f"http://{service.host}:{service.port}{service.health_endpoint}"
                response = requests.get(url, timeout=5)
                healthy = response.status_code == 200
                status.healthy = healthy
                status.last_health_check = datetime.now()
                return healthy
            except Exception as e:
                status.errors.append(f"Health check failed: {e}")
                status.healthy = False
                return False
        
        # If no health endpoint, assume healthy if port is open
        status.healthy = True
        status.last_health_check = datetime.now()
        return True
    
    def get_process_info(self, pid: int) -> Dict[str, Any]:
        """Get detailed process information."""
        if not PSUTIL_AVAILABLE:
            return {}
        
        try:
            process = psutil.Process(pid)
            return {
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(),
                'status': process.status(),
                'create_time': datetime.fromtimestamp(process.create_time()),
                'cmdline': ' '.join(process.cmdline())
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {}
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific service."""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
        
        service = self.services[service_name]
        status = self.status[service_name]
        
        # Check if already running
        if status.running:
            logger.info(f"Service {service_name} is already running")
            return True
        
        # Check dependencies
        if service.depends_on:
            for dep in service.depends_on:
                if not self.status.get(dep, ServiceStatus(dep)).running:
                    logger.error(f"Cannot start {service_name}: dependency {dep} not running")
                    return False
        
        # Skip external services
        if not service.command:
            logger.info(f"Skipping external service: {service_name}")
            return self.check_service_health(service_name)
        
        logger.info(f"🚀 Starting service: {service_name}")
        
        try:
            # Setup environment
            env = os.environ.copy()
            if service.environment:
                env.update(service.environment)
            
            # Start process
            process = subprocess.Popen(
                service.command,
                cwd=service.cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.processes[service_name] = process
            status.running = True
            status.pid = process.pid
            status.start_time = datetime.now()
            status.errors.clear()
            
            logger.info(f"✅ Service {service_name} started with PID {process.pid}")
            
            # Wait for service to be ready
            ready = False
            for attempt in range(service.startup_timeout):
                time.sleep(1)
                if self.check_service_health(service_name):
                    ready = True
                    break
                
                # Check if process died
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    logger.error(f"Service {service_name} died during startup: {stderr}")
                    status.errors.append(f"Startup failed: {stderr}")
                    status.running = False
                    return False
            
            if ready:
                logger.info(f"🎉 Service {service_name} is ready and healthy")
                return True
            else:
                logger.warning(f"⏰ Service {service_name} started but health check timeout")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start service {service_name}: {e}")
            status.errors.append(f"Start failed: {e}")
            status.running = False
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service."""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
        
        service = self.services[service_name]
        status = self.status[service_name]
        
        if not status.running:
            logger.info(f"Service {service_name} is not running")
            return True
        
        # Skip external services
        if not service.command:
            logger.info(f"Cannot stop external service: {service_name}")
            return True
        
        logger.info(f"🛑 Stopping service: {service_name}")
        
        try:
            if service_name in self.processes:
                process = self.processes[service_name]
                
                # Try graceful shutdown first
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=service.shutdown_timeout)
                    logger.info(f"✅ Service {service_name} stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ Service {service_name} did not stop gracefully, forcing...")
                    process.kill()
                    process.wait()
                    logger.info(f"💥 Service {service_name} force stopped")
                
                del self.processes[service_name]
            
            status.running = False
            status.pid = None
            status.healthy = False
            status.port_open = False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop service {service_name}: {e}")
            status.errors.append(f"Stop failed: {e}")
            return False
    
    def start_all_services(self) -> bool:
        """Start all services in dependency order."""
        logger.info("🚀 Starting all Aura V24 services...")
        
        # Build dependency graph and start in order
        started = set()
        all_started = True
        
        # Multiple passes to handle dependencies
        max_attempts = len(self.services) * 2
        attempts = 0
        
        while len(started) < len(self.services) and attempts < max_attempts:
            attempts += 1
            progress_made = False
            
            for service_name, service in self.services.items():
                if service_name in started:
                    continue
                
                # Check if dependencies are met
                can_start = True
                if service.depends_on:
                    for dep in service.depends_on:
                        if dep not in started:
                            can_start = False
                            break
                
                if can_start:
                    if self.start_service(service_name):
                        started.add(service_name)
                        progress_made = True
                    else:
                        if service.required:
                            all_started = False
            
            if not progress_made:
                break
            
            time.sleep(2)  # Brief pause between services
        
        # Report results
        if len(started) == len(self.services):
            logger.info("🎉 All services started successfully!")
        else:
            failed = set(self.services.keys()) - started
            logger.error(f"❌ Failed to start services: {', '.join(failed)}")
            all_started = False
        
        return all_started
    
    def stop_all_services(self) -> bool:
        """Stop all services."""
        logger.info("🛑 Stopping all services...")
        
        # Stop in reverse dependency order
        stopped = set()
        all_stopped = True
        
        # Simple reverse order for now
        service_names = list(self.services.keys())
        service_names.reverse()
        
        for service_name in service_names:
            if self.stop_service(service_name):
                stopped.add(service_name)
            else:
                all_stopped = False
        
        if all_stopped:
            logger.info("✅ All services stopped successfully")
        else:
            logger.warning("⚠️ Some services failed to stop cleanly")
        
        return all_stopped
    
    def restart_all_services(self) -> bool:
        """Restart all services."""
        logger.info("🔄 Restarting all services...")
        
        stop_success = self.stop_all_services()
        time.sleep(3)  # Brief pause
        start_success = self.start_all_services()
        
        return stop_success and start_success
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        # Update service health
        for service_name in self.services:
            self.check_service_health(service_name)
            
            # Update process info if available
            status = self.status[service_name]
            if status.pid and PSUTIL_AVAILABLE:
                proc_info = self.get_process_info(status.pid)
                if proc_info:
                    status.memory_usage = proc_info.get('memory_mb')
                    status.cpu_usage = proc_info.get('cpu_percent')
        
        # Get system resources
        system_info = {}
        if PSUTIL_AVAILABLE:
            system_info = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'boot_time': datetime.fromtimestamp(psutil.boot_time()),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
        
        return {
            'timestamp': datetime.now(),
            'services': {name: {
                'running': status.running,
                'healthy': status.healthy,
                'pid': status.pid,
                'port_open': status.port_open,
                'memory_mb': status.memory_usage,
                'cpu_percent': status.cpu_usage,
                'start_time': status.start_time,
                'last_health_check': status.last_health_check,
                'errors': status.errors[-5:]  # Last 5 errors
            } for name, status in self.status.items()},
            'system': system_info
        }
    
    def run_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive system diagnostics."""
        logger.info("🔍 Running system diagnostics...")
        
        diagnostics = {
            'timestamp': datetime.now(),
            'configuration': {},
            'network': {},
            'services': {},
            'resources': {},
            'issues': []
        }
        
        # Configuration validation
        if CONFIG_AVAILABLE:
            config_issues = validate_system_config()
            diagnostics['configuration'] = {
                'status': 'valid' if not any(config_issues.values()) else 'issues',
                'issues': config_issues
            }
            
            if any(config_issues['missing']) or any(config_issues['invalid']):
                diagnostics['issues'].append("Configuration validation failed")
        
        # Network connectivity tests
        network_tests = {
            'localhost_reachable': self.check_port_available('127.0.0.1', 22),  # SSH typically available
            'internet_reachable': False
        }
        
        if REQUESTS_AVAILABLE:
            try:
                requests.get('https://api.github.com', timeout=5)
                network_tests['internet_reachable'] = True
            except:
                pass
        
        diagnostics['network'] = network_tests
        
        # Service diagnostics  
        service_diag = {}
        for service_name in self.services:
            service_diag[service_name] = {
                'configured': True,
                'port_available': not self.check_port_available(
                    self.services[service_name].host,
                    self.services[service_name].port
                ),
                'healthy': self.check_service_health(service_name)
            }
        
        diagnostics['services'] = service_diag
        
        # Resource diagnostics
        if PSUTIL_AVAILABLE:
            diagnostics['resources'] = {
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': psutil.virtual_memory().total / (1024**3),
                'disk_free_gb': psutil.disk_usage('/').free / (1024**3),
                'python_version': sys.version
            }
        
        # Identify critical issues
        running_services = sum(1 for s in self.status.values() if s.running)
        if running_services == 0:
            diagnostics['issues'].append("No services are running")
        
        port_conflicts = len(set(s.port for s in self.services.values())) != len(self.services)
        if port_conflicts:
            diagnostics['issues'].append("Port conflicts detected")
        
        return diagnostics
    
    def print_status_table(self):
        """Print formatted status table."""
        status = self.get_system_status()
        
        print(f"\n🤖 Aura V24 System Status - {status['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Services table
        print(f"{'Service':<15} {'Status':<10} {'Health':<8} {'Port':<8} {'PID':<8} {'Memory':<10}")
        print("-" * 80)
        
        for name, service_status in status['services'].items():
            status_str = "🟢 UP" if service_status['running'] else "🔴 DOWN"
            health_str = "✅" if service_status['healthy'] else "❌"
            port_str = "🟢" if service_status['port_open'] else "🔴"
            pid_str = str(service_status['pid']) if service_status['pid'] else "-"
            memory_str = f"{service_status['memory_mb']:.1f}MB" if service_status['memory_mb'] else "-"
            
            print(f"{name:<15} {status_str:<10} {health_str:<8} {port_str:<8} {pid_str:<8} {memory_str:<10}")
        
        # System resources
        if status['system']:
            print(f"\n💻 System Resources:")
            print(f"  CPU: {status['system'].get('cpu_percent', 'N/A')}%")
            print(f"  Memory: {status['system'].get('memory_percent', 'N/A')}%") 
            print(f"  Disk: {status['system'].get('disk_percent', 'N/A')}%")
        
        print()
    
    def start_monitoring(self, interval: int = 30):
        """Start continuous monitoring."""
        logger.info(f"📊 Starting system monitoring (interval: {interval}s)")
        self.monitoring_active = True
        
        def monitor_loop():
            while self.monitoring_active and not self.shutdown_requested:
                try:
                    self.print_status_table()
                    time.sleep(interval)
                except KeyboardInterrupt:
                    break
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        try:
            monitor_thread.join()
        except KeyboardInterrupt:
            self.monitoring_active = False
    
    def show_logs(self, service_name: Optional[str] = None, lines: int = 50):
        """Show system or service logs."""
        if service_name:
            if service_name not in self.processes:
                print(f"No active process for service: {service_name}")
                return
            
            process = self.processes[service_name]
            if process.stdout:
                # This is simplified - in practice you'd want to tail log files
                print(f"Recent output for {service_name}:")
                print("-" * 40)
        else:
            # Show system control log
            try:
                with open('system_control.log', 'r') as f:
                    log_lines = f.readlines()
                    for line in log_lines[-lines:]:
                        print(line.rstrip())
            except FileNotFoundError:
                print("No system log file found")

def main():
    """Main entry point with CLI interface."""
    parser = argparse.ArgumentParser(
        description='Aura V24 System Control Panel',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s start              # Start all services
  %(prog)s stop               # Stop all services  
  %(prog)s status             # Show service status
  %(prog)s health             # Run health checks
  %(prog)s diagnose           # Run full diagnostics
  %(prog)s monitor            # Start monitoring dashboard
  %(prog)s logs               # Show system logs
  %(prog)s logs ai_server     # Show service logs
        """
    )
    
    parser.add_argument(
        'command',
        choices=['start', 'stop', 'restart', 'status', 'health', 'diagnose', 'monitor', 'config', 'logs'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'service',
        nargs='?',
        help='Specific service name (for logs command)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Monitoring interval in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--lines',
        type=int, 
        default=50,
        help='Number of log lines to show (default: 50)'
    )
    
    args = parser.parse_args()
    
    # Initialize control panel
    try:
        control_panel = SystemControlPanel()
    except Exception as e:
        logger.error(f"Failed to initialize control panel: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'start':
            success = control_panel.start_all_services()
            if success:
                print("🎉 All services started successfully!")
                control_panel.print_status_table()
            else:
                print("❌ Some services failed to start")
                sys.exit(1)
        
        elif args.command == 'stop':
            success = control_panel.stop_all_services()
            if success:
                print("✅ All services stopped successfully")
            else:
                print("⚠️ Some services failed to stop cleanly")
        
        elif args.command == 'restart':
            success = control_panel.restart_all_services()
            if success:
                print("🔄 All services restarted successfully!")
                control_panel.print_status_table()
            else:
                print("❌ Restart failed")
                sys.exit(1)
        
        elif args.command == 'status':
            control_panel.print_status_table()
        
        elif args.command == 'health':
            print("🏥 Running health checks...")
            all_healthy = True
            for service_name in control_panel.services:
                healthy = control_panel.check_service_health(service_name)
                status_icon = "✅" if healthy else "❌"
                print(f"  {status_icon} {service_name}: {'Healthy' if healthy else 'Unhealthy'}")
                if not healthy:
                    all_healthy = False
            
            if all_healthy:
                print("\n🎉 All services are healthy!")
            else:
                print("\n⚠️ Some services are unhealthy")
                sys.exit(1)
        
        elif args.command == 'diagnose':
            diagnostics = control_panel.run_diagnostics()
            print(json.dumps(diagnostics, indent=2, default=str))
        
        elif args.command == 'monitor':
            print("📊 Starting monitoring dashboard (Ctrl+C to stop)...")
            control_panel.start_monitoring(args.interval)
        
        elif args.command == 'config':
            if CONFIG_AVAILABLE:
                issues = validate_system_config()
                if not any(issues.values()):
                    print("✅ Configuration is valid")
                else:
                    print("❌ Configuration issues found:")
                    for category, items in issues.items():
                        if items:
                            print(f"  {category.title()}: {', '.join(items)}")
                    sys.exit(1)
            else:
                print("⚠️ Configuration validation not available")
        
        elif args.command == 'logs':
            control_panel.show_logs(args.service, args.lines)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        control_panel.stop_all_services()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()