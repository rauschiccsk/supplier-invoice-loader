#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Supplier Invoice Loader - Windows Service Installer
Supports Windows 11 and Windows Server 2012 R2

This script manages Windows service installation using NSSM or native Windows SC.
NSSM is preferred for better control and features.

Usage:
    python service_installer.py install    # Install service
    python service_installer.py remove     # Remove service
    python service_installer.py status     # Check service status
    python service_installer.py start      # Start service
    python service_installer.py stop       # Stop service
    python service_installer.py restart    # Restart service
    python service_installer.py configure  # Reconfigure service
"""

import os
import sys
import subprocess
import platform
import ctypes
import json
import shutil
import time
from pathlib import Path
from typing import Optional, Dict, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Service configuration
SERVICE_CONFIG = {
    'name': 'SupplierInvoiceLoader',
    'display_name': 'Supplier Invoice Loader',
    'description': 'Automated invoice processing system for supplier invoices',
    'start_type': 'auto',  # auto, manual, disabled
    'dependencies': [],  # Service dependencies if any
    'recovery_actions': {
        'first_failure': 'restart',
        'second_failure': 'restart',
        'subsequent_failures': 'restart',
        'reset_period': 86400,  # 24 hours in seconds
        'restart_delay': 60000  # 1 minute in milliseconds
    }
}


class WindowsServiceInstaller:
    """Windows Service Installer for Supplier Invoice Loader"""

    def __init__(self):
        self.project_root = Path(__file__).parent.resolve()
        self.python_path = sys.executable
        self.main_script = self.project_root / 'main.py'
        self.venv_path = self.project_root / 'venv'
        self.logs_dir = self.project_root / 'logs'
        self.service_name = SERVICE_CONFIG['name']
        self.nssm_path = None

        # Create logs directory
        self.logs_dir.mkdir(exist_ok=True)

        # Check for NSSM
        self._check_nssm()

        # Check Windows version
        self.windows_version = self._get_windows_version()
        logger.info(f"Windows version: {self.windows_version}")

    def _check_nssm(self) -> bool:
        """Check if NSSM is available"""
        # Check in PATH
        nssm_in_path = shutil.which('nssm.exe')
        if nssm_in_path:
            self.nssm_path = Path(nssm_in_path)
            logger.info(f"NSSM found in PATH: {self.nssm_path}")
            return True

        # Check in project tools directory
        tools_dir = self.project_root / 'tools'
        if tools_dir.exists():
            # Check for architecture-specific NSSM
            arch = 'win64' if platform.machine().endswith('64') else 'win32'
            nssm_exe = tools_dir / 'nssm' / arch / 'nssm.exe'
            if nssm_exe.exists():
                self.nssm_path = nssm_exe
                logger.info(f"NSSM found in tools: {self.nssm_path}")
                return True

        logger.warning("NSSM not found. Will use Windows SC command (limited features)")
        return False

    def _get_windows_version(self) -> str:
        """Get Windows version information"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            product_name = winreg.QueryValueEx(key, "ProductName")[0]
            build = winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
            winreg.CloseKey(key)
            return f"{product_name} (Build {build})"
        except:
            return platform.platform()

    def is_admin(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_as_admin(self):
        """Restart the script with administrator privileges"""
        if not self.is_admin():
            logger.info("Requesting administrator privileges...")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)

    def run_command(self, command: list, check: bool = True) -> Tuple[int, str, str]:
        """Run a command and return result"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr
        except Exception as e:
            return 1, "", str(e)

    def install_with_nssm(self) -> bool:
        """Install service using NSSM"""
        logger.info("Installing service using NSSM...")

        # Determine Python executable
        if self.venv_path.exists():
            python_exe = self.venv_path / 'Scripts' / 'python.exe'
            if not python_exe.exists():
                logger.error(f"Virtual environment Python not found: {python_exe}")
                return False
        else:
            python_exe = Path(self.python_path)

        # Install service
        cmd = [str(self.nssm_path), 'install', self.service_name, str(python_exe)]
        returncode, stdout, stderr = self.run_command(cmd)

        if returncode != 0 and 'already exists' not in stderr:
            logger.error(f"Failed to install service: {stderr}")
            return False

        # Configure service parameters
        configurations = [
            ['set', self.service_name, 'AppParameters', str(self.main_script)],
            ['set', self.service_name, 'AppDirectory', str(self.project_root)],
            ['set', self.service_name, 'DisplayName', SERVICE_CONFIG['display_name']],
            ['set', self.service_name, 'Description', SERVICE_CONFIG['description']],
            ['set', self.service_name, 'Start', 'SERVICE_AUTO_START'],

            # Output redirection
            ['set', self.service_name, 'AppStdout', str(self.logs_dir / 'service.log')],
            ['set', self.service_name, 'AppStderr', str(self.logs_dir / 'service_error.log')],
            ['set', self.service_name, 'AppStdoutCreationDisposition', '4'],
            ['set', self.service_name, 'AppStderrCreationDisposition', '4'],

            # Log rotation
            ['set', self.service_name, 'AppRotateFiles', '1'],
            ['set', self.service_name, 'AppRotateOnline', '1'],
            ['set', self.service_name, 'AppRotateSeconds', '86400'],  # Daily
            ['set', self.service_name, 'AppRotateBytes', '10485760'],  # 10MB

            # Environment variables
            ['set', self.service_name, 'AppEnvironmentExtra',
             f'PYTHONPATH={self.project_root}'],

            # Process priority
            ['set', self.service_name, 'AppPriority', 'NORMAL_PRIORITY_CLASS'],

            # Shutdown grace period
            ['set', self.service_name, 'AppStopMethodSkip', '0'],
            ['set', self.service_name, 'AppStopMethodConsole', '1500'],
            ['set', self.service_name, 'AppStopMethodWindow', '1500'],
            ['set', self.service_name, 'AppStopMethodThreads', '1500'],
        ]

        for config in configurations:
            cmd = [str(self.nssm_path)] + config
            returncode, stdout, stderr = self.run_command(cmd, check=False)
            if returncode != 0:
                logger.warning(f"Configuration warning: {' '.join(config[1:])}: {stderr}")

        # Set recovery actions
        self._set_recovery_actions()

        logger.info("Service installed successfully")
        return True

    def install_with_sc(self) -> bool:
        """Install service using Windows SC command"""
        logger.info("Installing service using Windows SC...")

        # Determine Python executable
        if self.venv_path.exists():
            python_exe = self.venv_path / 'Scripts' / 'python.exe'
        else:
            python_exe = Path(self.python_path)

        # Create service
        binpath = f'"{python_exe}" "{self.main_script}"'
        cmd = [
            'sc', 'create', self.service_name,
            'binpath=', binpath,
            'DisplayName=', SERVICE_CONFIG['display_name'],
            'start=', 'auto'
        ]

        returncode, stdout, stderr = self.run_command(cmd)

        if returncode != 0:
            if 'already exists' in stdout or 'already exists' in stderr:
                logger.warning("Service already exists")
            else:
                logger.error(f"Failed to create service: {stderr or stdout}")
                return False

        # Set description
        cmd = ['sc', 'description', self.service_name, SERVICE_CONFIG['description']]
        self.run_command(cmd, check=False)

        # Set recovery actions
        self._set_recovery_actions()

        logger.info("Service installed (basic configuration)")
        logger.warning("For full features, install NSSM from https://nssm.cc")

        return True

    def _set_recovery_actions(self):
        """Set service recovery actions"""
        recovery = SERVICE_CONFIG['recovery_actions']

        # Build recovery command
        cmd = [
            'sc', 'failure', self.service_name,
            'reset=', str(recovery['reset_period']),
            'actions=',
            f"restart/{recovery['restart_delay']}/restart/{recovery['restart_delay']}/restart/{recovery['restart_delay']}"
        ]

        returncode, stdout, stderr = self.run_command(cmd, check=False)
        if returncode == 0:
            logger.info("Recovery actions configured")
        else:
            logger.warning(f"Could not set recovery actions: {stderr or stdout}")

    def install_service(self) -> bool:
        """Install the Windows service"""
        self.run_as_admin()

        logger.info(f"Installing {SERVICE_CONFIG['display_name']}...")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Python: {self.python_path}")
        logger.info(f"Main script: {self.main_script}")

        # Check if main.py exists
        if not self.main_script.exists():
            logger.error(f"Main script not found: {self.main_script}")
            return False

        # Use NSSM if available, otherwise fall back to SC
        if self.nssm_path:
            success = self.install_with_nssm()
        else:
            success = self.install_with_sc()

        if success:
            # Create service info file
            self._save_service_info()
            logger.info("=" * 50)
            logger.info("Service installed successfully!")
            logger.info(f"Service name: {self.service_name}")
            logger.info("Commands:")
            logger.info(f"  Start:   net start {self.service_name}")
            logger.info(f"  Stop:    net stop {self.service_name}")
            logger.info(f"  Status:  sc query {self.service_name}")
            logger.info("=" * 50)

        return success

    def remove_service(self) -> bool:
        """Remove the Windows service"""
        self.run_as_admin()

        logger.info(f"Removing service {self.service_name}...")

        # Stop service first
        self.stop_service()
        time.sleep(2)

        # Remove using NSSM or SC
        if self.nssm_path:
            cmd = [str(self.nssm_path), 'remove', self.service_name, 'confirm']
        else:
            cmd = ['sc', 'delete', self.service_name]

        returncode, stdout, stderr = self.run_command(cmd)

        if returncode == 0:
            logger.info("Service removed successfully")
            # Remove service info file
            info_file = self.project_root / 'service_info.json'
            if info_file.exists():
                info_file.unlink()
            return True
        else:
            if 'does not exist' in stderr or 'FAILED 1060' in stderr:
                logger.warning("Service does not exist")
                return True
            logger.error(f"Failed to remove service: {stderr or stdout}")
            return False

    def start_service(self) -> bool:
        """Start the service"""
        logger.info(f"Starting service {self.service_name}...")

        cmd = ['net', 'start', self.service_name]
        returncode, stdout, stderr = self.run_command(cmd, check=False)

        if returncode == 0:
            logger.info("Service started successfully")
            return True
        elif 'already been started' in stdout or 'already been started' in stderr:
            logger.info("Service is already running")
            return True
        else:
            logger.error(f"Failed to start service: {stderr or stdout}")
            return False

    def stop_service(self) -> bool:
        """Stop the service"""
        logger.info(f"Stopping service {self.service_name}...")

        cmd = ['net', 'stop', self.service_name]
        returncode, stdout, stderr = self.run_command(cmd, check=False)

        if returncode == 0:
            logger.info("Service stopped successfully")
            return True
        elif 'is not started' in stdout or 'is not started' in stderr:
            logger.info("Service is not running")
            return True
        else:
            logger.error(f"Failed to stop service: {stderr or stdout}")
            return False

    def restart_service(self) -> bool:
        """Restart the service"""
        logger.info("Restarting service...")

        if self.stop_service():
            time.sleep(2)
            return self.start_service()
        return False

    def get_service_status(self) -> Dict[str, str]:
        """Get service status"""
        cmd = ['sc', 'query', self.service_name]
        returncode, stdout, stderr = self.run_command(cmd, check=False)

        status = {
            'exists': False,
            'state': 'NOT_INSTALLED',
            'win32_exit_code': '',
            'service_exit_code': '',
            'checkpoint': '',
            'wait_hint': ''
        }

        if returncode == 0:
            status['exists'] = True
            for line in stdout.split('\n'):
                if 'STATE' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        status['state'] = parts[3]
                elif 'WIN32_EXIT_CODE' in line:
                    status['win32_exit_code'] = line.split(':')[1].strip()
                elif 'SERVICE_EXIT_CODE' in line:
                    status['service_exit_code'] = line.split(':')[1].strip()

        return status

    def show_status(self):
        """Display service status"""
        status = self.get_service_status()

        print("\n" + "=" * 50)
        print(f"Service: {self.service_name}")
        print("=" * 50)

        if status['exists']:
            state_color = {
                'RUNNING': '\033[92m',  # Green
                'STOPPED': '\033[91m',  # Red
                'PAUSED': '\033[93m',  # Yellow
            }.get(status['state'], '\033[0m')

            print(f"Status: {state_color}{status['state']}\033[0m")
            print(f"Win32 Exit Code: {status['win32_exit_code']}")
            print(f"Service Exit Code: {status['service_exit_code']}")

            # Additional info from service_info.json
            info_file = self.project_root / 'service_info.json'
            if info_file.exists():
                with open(info_file, 'r') as f:
                    info = json.load(f)
                print(f"\nInstalled: {info.get('installed_date', 'Unknown')}")
                print(f"Python: {info.get('python_path', 'Unknown')}")
                print(f"Using NSSM: {info.get('using_nssm', False)}")
        else:
            print("Status: \033[91mNOT INSTALLED\033[0m")

        print("=" * 50)

    def configure_service(self):
        """Interactive service configuration"""
        logger.info("Service configuration...")

        if not self.get_service_status()['exists']:
            logger.error("Service not installed. Please install first.")
            return

        print("\nService Configuration Options:")
        print("1. Change startup type (auto/manual/disabled)")
        print("2. Configure recovery actions")
        print("3. View logs location")
        print("4. Set environment variables")
        print("5. Back to main menu")

        choice = input("\nSelect option (1-5): ").strip()

        if choice == '1':
            self._configure_startup_type()
        elif choice == '2':
            self._configure_recovery()
        elif choice == '3':
            print(f"\nLogs location: {self.logs_dir}")
            print(f"  Service log: {self.logs_dir / 'service.log'}")
            print(f"  Error log: {self.logs_dir / 'service_error.log'}")
        elif choice == '4':
            self._configure_environment()

    def _configure_startup_type(self):
        """Configure service startup type"""
        print("\nStartup Type:")
        print("1. Automatic")
        print("2. Manual")
        print("3. Disabled")

        choice = input("\nSelect (1-3): ").strip()

        start_type = {
            '1': 'auto',
            '2': 'demand',
            '3': 'disabled'
        }.get(choice)

        if start_type:
            cmd = ['sc', 'config', self.service_name, 'start=', start_type]
            returncode, stdout, stderr = self.run_command(cmd)

            if returncode == 0:
                logger.info(f"Startup type changed to: {start_type}")
            else:
                logger.error(f"Failed to change startup type: {stderr or stdout}")

    def _configure_recovery(self):
        """Configure recovery actions"""
        print("\nRecovery Configuration")
        print("Current: Restart on all failures")

        reset = input("Reset period in hours (default: 24): ").strip() or "24"
        delay = input("Restart delay in seconds (default: 60): ").strip() or "60"

        try:
            reset_seconds = int(reset) * 3600
            delay_ms = int(delay) * 1000

            cmd = [
                'sc', 'failure', self.service_name,
                'reset=', str(reset_seconds),
                'actions=', f"restart/{delay_ms}/restart/{delay_ms}/restart/{delay_ms}"
            ]

            returncode, stdout, stderr = self.run_command(cmd)

            if returncode == 0:
                logger.info("Recovery actions updated")
            else:
                logger.error(f"Failed to update recovery: {stderr or stdout}")
        except ValueError:
            logger.error("Invalid input")

    def _configure_environment(self):
        """Configure environment variables"""
        if not self.nssm_path:
            logger.warning("Environment configuration requires NSSM")
            return

        print("\nEnvironment Variables")
        print("Add variables in format: VAR_NAME=value")
        print("Leave empty to finish")

        env_vars = []
        while True:
            var = input("Environment variable: ").strip()
            if not var:
                break
            env_vars.append(var)

        if env_vars:
            env_string = '\n'.join(env_vars)
            cmd = [str(self.nssm_path), 'set', self.service_name,
                   'AppEnvironmentExtra', env_string]
            returncode, stdout, stderr = self.run_command(cmd)

            if returncode == 0:
                logger.info("Environment variables updated")
            else:
                logger.error(f"Failed to set environment: {stderr}")

    def _save_service_info(self):
        """Save service installation information"""
        info = {
            'service_name': self.service_name,
            'display_name': SERVICE_CONFIG['display_name'],
            'installed_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'python_path': str(self.python_path),
            'main_script': str(self.main_script),
            'project_root': str(self.project_root),
            'using_nssm': bool(self.nssm_path),
            'windows_version': self.windows_version
        }

        info_file = self.project_root / 'service_info.json'
        with open(info_file, 'w') as f:
            json.dump(info, f, indent=2)

    def download_nssm(self):
        """Download and install NSSM"""
        logger.info("Downloading NSSM...")

        import urllib.request
        import zipfile

        # NSSM download URL
        nssm_url = "https://nssm.cc/release/nssm-2.24.zip"

        # Create tools directory
        tools_dir = self.project_root / 'tools'
        tools_dir.mkdir(exist_ok=True)

        # Download
        zip_path = tools_dir / 'nssm.zip'
        try:
            urllib.request.urlretrieve(nssm_url, zip_path)

            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tools_dir)

            # Remove zip
            zip_path.unlink()

            # Find NSSM executable
            arch = 'win64' if platform.machine().endswith('64') else 'win32'
            nssm_exe = tools_dir / 'nssm-2.24' / arch / 'nssm.exe'

            if nssm_exe.exists():
                # Move to simpler path
                nssm_dir = tools_dir / 'nssm' / arch
                nssm_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(nssm_exe, nssm_dir / 'nssm.exe')

                # Clean up
                shutil.rmtree(tools_dir / 'nssm-2.24')

                self.nssm_path = nssm_dir / 'nssm.exe'
                logger.info(f"NSSM downloaded successfully: {self.nssm_path}")
                return True

        except Exception as e:
            logger.error(f"Failed to download NSSM: {e}")
            logger.info("Please download manually from https://nssm.cc")
            return False


def main():
    """Main entry point"""
    installer = WindowsServiceInstaller()

    # Parse command line arguments
    if len(sys.argv) < 2:
        # Interactive mode
        print("\n" + "=" * 50)
        print("Supplier Invoice Loader - Service Manager")
        print("=" * 50)
        print(f"Windows: {installer.windows_version}")
        print(f"Project: {installer.project_root}")
        print(f"NSSM: {'Available' if installer.nssm_path else 'Not found'}")

        # Show current status
        installer.show_status()

        print("\nOptions:")
        print("1. Install service")
        print("2. Remove service")
        print("3. Start service")
        print("4. Stop service")
        print("5. Restart service")
        print("6. Configure service")
        print("7. Show status")

        if not installer.nssm_path:
            print("8. Download NSSM (recommended)")

        print("9. Exit")

        choice = input("\nSelect option: ").strip()

        actions = {
            '1': installer.install_service,
            '2': installer.remove_service,
            '3': installer.start_service,
            '4': installer.stop_service,
            '5': installer.restart_service,
            '6': installer.configure_service,
            '7': installer.show_status,
            '8': installer.download_nssm if not installer.nssm_path else None,
            '9': lambda: sys.exit(0)
        }

        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid option")

    else:
        # Command line mode
        command = sys.argv[1].lower()

        commands = {
            'install': installer.install_service,
            'remove': installer.remove_service,
            'uninstall': installer.remove_service,
            'start': installer.start_service,
            'stop': installer.stop_service,
            'restart': installer.restart_service,
            'status': installer.show_status,
            'configure': installer.configure_service,
            'download-nssm': installer.download_nssm
        }

        if command in commands:
            success = commands[command]()
            sys.exit(0 if success else 1)
        else:
            print(f"Unknown command: {command}")
            print("Available commands: install, remove, start, stop, restart, status, configure")
            sys.exit(1)


if __name__ == "__main__":
    main()