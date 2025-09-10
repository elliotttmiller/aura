#!/usr/bin/env python3
"""
Aura V25 Hyperrealistic System Startup Script
==============================================

Enhanced startup script for V25 Hyperrealistic AI Jewelry Design System.
Provides unified entry point with proper dependency management for all
hyperrealistic components and professional-grade operation.

Usage:
    python startup.py                    # Interactive menu mode
    python startup.py --full             # Full hyperrealistic system startup
    python startup.py --clean            # Clean restart with process cleanup
    python startup.py --web              # Start and open web control panel
    python startup.py --hyperrealistic   # Start hyperrealistic services only
"""

import os
import sys
import argparse

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(
        description='Aura V25 Hyperrealistic System Startup Script',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--full', 
        action='store_true',
        help='Start all services in proper dependency order'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true', 
        help='Kill existing processes and start fresh'
    )
    
    parser.add_argument(
        '--web',
        action='store_true',
        help='Start services and open web control panel'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Start interactive control menu (default when no args)'
    )
    
    args = parser.parse_args()
    
    # Import the control panel
    try:
        from backend.system_control_panel import SystemControlPanel, interactive_menu, _kill_existing_processes, _open_frontend_browser
    except ImportError as e:
        print(f"❌ Failed to import control panel: {e}")
        print("💡 Make sure you're running this from the Aura project root directory")
        sys.exit(1)
    
    print("🚀 Aura V24 System Startup")
    print("=" * 50)
    
    if args.clean:
        print("🔧 Performing clean startup...")
        _kill_existing_processes()
        print("✅ Process cleanup completed")
        
        # Continue to start services
        args.full = True
    
    if args.full or args.web:
        print("🚀 Starting all services in dependency order...")
        try:
            control_panel = SystemControlPanel()
            success = control_panel.start_all_services()
            
            if success:
                print("\n🎉 All services started successfully!")
                control_panel.print_status_table()
                
                if args.web:
                    print("\n🌐 Opening web control panel...")
                    _open_frontend_browser()
                    
                print("\n💡 System is ready! You can now:")
                print("   - Use the web control panel for visual management")
                print("   - Run 'python backend/system_control_panel.py' for CLI control")
                print("   - Access the API at http://localhost:8001/docs")
                
            else:
                print("\n❌ Some services failed to start")
                print("💡 Run 'python backend/system_control_panel.py status' to see details")
                sys.exit(1)
                
        except Exception as e:
            print(f"\n❌ Startup failed: {e}")
            sys.exit(1)
    
    elif args.interactive or len(sys.argv) == 1:
        # Interactive mode (default)
        print("🎮 Starting interactive control menu...")
        print("💡 You can also use command-line options. Run with --help for details.")
        interactive_menu()
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()