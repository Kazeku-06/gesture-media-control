#!/usr/bin/env python3
"""
Gesture Media Control - Main Entry Point
Enhanced version with modular architecture
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """
    Main entry point for the application
    """
    try:
        from app import main as app_main
        app_main()
    except ImportError as e:
        print(f"Error importing application: {e}")
        print("Please ensure all required modules are installed.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
