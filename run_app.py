"""
Entry point for running the Streamlit app.
Works with both normal Python execution and PyInstaller bundled executables.
"""
import sys
import os
from streamlit.web import cli as stcli


def main(argv=None):
    """Main entry point that works with PyInstaller."""
    # Get the directory where the script is located
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        application_path = sys._MEIPASS
    else:
        # Running in normal Python
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Path to app.py
    app_path = os.path.join(application_path, 'app.py')
    
    # Ensure app.py exists
    if not os.path.exists(app_path):
        print(f"Error: app.py not found at {app_path}")
        return 1
    
    # Set up sys.argv for streamlit
    # Disable development mode to avoid conflicts with server.port
    sys.argv = [
        "streamlit", 
        "run", 
        app_path,
        "--global.developmentMode=false",
        "--server.port=35540",
        "--server.address=localhost",
        "--server.headless=true"
    ]
    
    # Add any additional arguments
    if argv:
        sys.argv.extend(argv)
    
    # Run streamlit
    try:
        sys.exit(stcli.main())
    except SystemExit as e:
        return e.code


if __name__ == '__main__':
    sys.exit(main())
