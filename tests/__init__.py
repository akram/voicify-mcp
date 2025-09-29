# Add the parent directory to the Python path so tests can import voicify_server
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
