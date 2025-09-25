#!/usr/bin/env python3
"""
Encrypted Linear Algebra over UDP - Main Launcher
Run this script to start the complete system with server, client, and moderator
"""

import sys
import argparse
import subprocess
import threading
import time

def run_server():
    """Run the UDP matrix server"""
    print("Starting Matrix Server...")
    subprocess.run([sys.executable, "server.py"])

def run_client():
    """Run the client GUI"""
    print("Starting Matrix Client GUI...")
    subprocess.run([sys.executable, "client.py"])

def run_moderator():
    """Run the packet moderator"""
    print("Starting Packet Moderator...")
    subprocess.run([sys.executable, "moderator.py"])

def main():
    parser = argparse.ArgumentParser(description="Encrypted Linear Algebra over UDP")
    parser.add_argument("component", nargs="?", choices=["server", "client", "moderator", "all"],
                       default="all", help="Component to run (default: all)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ENCRYPTED LINEAR ALGEBRA OVER UDP")
    print("=" * 60)
    print("Components:")
    print("  • Server: Processes matrix operations")
    print("  • Client: GUI for sending operations") 
    print("  • Moderator: Observes network traffic")
    print("=" * 60)
    
    if args.component == "server":
        run_server()
    elif args.component == "client":
        run_client()
    elif args.component == "moderator":
        run_moderator()
    elif args.component == "all":
        print("Starting all components...")
        
        # Start server in background
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Start moderator in background
        moderator_thread = threading.Thread(target=run_moderator, daemon=True)
        moderator_thread.start()
        
        # Give server and moderator time to start
        time.sleep(2)
        
        print("All background components started.")
        print("Starting client GUI (close GUI to exit all components)...")
        
        # Run client in main thread (GUI needs main thread)
        run_client()

if __name__ == "__main__":
    main()