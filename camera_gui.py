#!/usr/bin/env python3
"""
Simple Camera Discovery GUI Application
This is a beginner-friendly GUI for finding cameras on your network

Author: Created for learning purposes
Date: 2024
"""

# Import required libraries
import tkinter as tk  # This is Python's built-in GUI library
from tkinter import ttk, scrolledtext, messagebox
import threading  # To run camera discovery without freezing the GUI
import subprocess
import socket
import json
import os
import sys
from urllib.parse import quote, urlparse

# Import libraries for camera discovery
try:
    from wsdiscovery import WSDiscovery
    from onvif import ONVIFCamera
except ImportError:
    print("Please install required packages: pip install wsdiscovery onvif-zeep")
    sys.exit(1)


class CameraFinderApp:
    """
    This is our main application class.
    Think of a class like a blueprint for creating our app.
    """
    
    def __init__(self):
        """This function runs when we create our app"""
        
        # Create the main window
        self.window = tk.Tk()
        self.window.title("Camera Finder - Simple & Easy")
        self.window.geometry("800x600")  # Width x Height in pixels
        
        # Set colors to make it look nice
        self.window.configure(bg='#f0f0f0')
        
        # Variables to store username and password
        self.username = ""
        self.password = ""
        
        # Create the GUI elements
        self.create_widgets()
        
        # Path to ffprobe.exe (we'll include this with our app)
        self.ffprobe_path = self.get_ffprobe_path()
        
    def get_ffprobe_path(self):
        """Find ffprobe.exe - first check local folder, then system PATH"""
        # Check if ffprobe.exe is in the same folder as our app
        local_ffprobe = os.path.join(os.path.dirname(__file__), "ffprobe.exe")
        if os.path.exists(local_ffprobe):
            return local_ffprobe
        # Otherwise, assume it's in system PATH
        return "ffprobe"
        
    def create_widgets(self):
        """Create all the buttons, text boxes, etc."""
        
        # Title at the top
        title_label = tk.Label(
            self.window, 
            text="📷 AlgoOrange Camera Finder Tool",
            font=("Arial", 20, "bold"),
            bg='#f0f0f0'
        )
        title_label.pack(pady=20)  # pady adds space above and below
        
        # Instructions
        instruction_label = tk.Label(
            self.window,
            text="Click a button below to start finding cameras on your network",
            font=("Arial", 12),
            bg='#f0f0f0'
        )
        instruction_label.pack(pady=5)
        
        # Frame to hold the two main buttons
        button_frame = tk.Frame(self.window, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        # WiFi Cameras button (this one works!)
        self.wifi_button = tk.Button(
            button_frame,
            text="🔍 WiFi Cameras",
            font=("Arial", 14, "bold"),
            bg='#4CAF50',  # Green color
            fg='white',
            width=15,
            height=2,
            command=self.find_wifi_cameras  # This function runs when clicked
        )
        self.wifi_button.pack(side=tk.LEFT, padx=10)
        
        # DVR Cameras button (placeholder for now)
        self.dvr_button = tk.Button(
            button_frame,
            text="📹 DVR Cameras",
            font=("Arial", 14, "bold"),
            bg='#2196F3',  # Blue color
            fg='white',
            width=15,
            height=2,
            command=self.dvr_placeholder  # This shows "coming soon" message
        )
        self.dvr_button.pack(side=tk.LEFT, padx=10)
        
        # Results area (where we show the found cameras)
        results_label = tk.Label(
            self.window,
            text="Results will appear here:",
            font=("Arial", 12, "bold"),
            bg='#f0f0f0'
        )
        results_label.pack(pady=(20, 5))
        
        # Text area with scrollbar for results
        self.results_text = scrolledtext.ScrolledText(
            self.window,
            width=90,
            height=20,
            font=("Consolas", 10),  # Monospace font for URLs
            wrap=tk.WORD
        )
        self.results_text.pack(padx=20, pady=10)
        
        # Export button (to save results to a file)
        self.export_button = tk.Button(
            self.window,
            text="💾 Export Results",
            font=("Arial", 11),
            bg='#FF9800',
            fg='white',
            width=15,
            command=self.export_results
        )
        self.export_button.pack(pady=5)
        
    def find_wifi_cameras(self):
        """This runs when user clicks WiFi Cameras button"""
        
        # First, ask for username and password
        self.get_credentials()
        
        # Only continue if user provided credentials
        if not self.username:
            return
            
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "🔍 Starting camera search...\n")
        self.results_text.insert(tk.END, "This may take 10-30 seconds...\n\n")
        
        # Disable buttons while searching
        self.wifi_button.config(state='disabled')
        self.dvr_button.config(state='disabled')
        
        # Run the search in a separate thread so GUI doesn't freeze
        search_thread = threading.Thread(target=self.search_cameras_thread)
        search_thread.daemon = True  # This ensures thread closes when app closes
        search_thread.start()
        
    def get_credentials(self):
        """Create a popup window to ask for username and password"""
        
        # Create a new popup window
        popup = tk.Toplevel(self.window)
        popup.title("Camera Login")
        popup.geometry("350x200")
        popup.configure(bg='white')
        
        # Center the popup
        popup.transient(self.window)
        popup.grab_set()
        
        # Title in popup
        tk.Label(
            popup,
            text="Enter Camera Credentials",
            font=("Arial", 14, "bold"),
            bg='white'
        ).pack(pady=10)
        
        # Username input
        tk.Label(popup, text="Username:", font=("Arial", 11), bg='white').pack()
        username_entry = tk.Entry(popup, width=30, font=("Arial", 11))
        username_entry.pack(pady=5)
        username_entry.insert(0, "admin")  # Default username
        
        # Password input
        tk.Label(popup, text="Password:", font=("Arial", 11), bg='white').pack()
        password_entry = tk.Entry(popup, width=30, show="*", font=("Arial", 11))
        password_entry.pack(pady=5)
        
        # Function to save credentials and close popup
        def save_and_close():
            self.username = username_entry.get()
            self.password = password_entry.get()
            popup.destroy()
            
        # OK button
        tk.Button(
            popup,
            text="OK",
            command=save_and_close,
            bg='#4CAF50',
            fg='white',
            font=("Arial", 11),
            width=10
        ).pack(pady=15)
        
        # Wait for popup to close
        popup.wait_window()
        
    def search_cameras_thread(self):
        """This is the actual camera search code (runs in background)"""
        
        try:
            # Step 1: Discover ONVIF devices
            self.update_results("📡 Discovering ONVIF cameras on your network...\n")
            devices = self.discover_onvif_devices()
            
            if not devices:
                self.update_results("❌ No cameras found on the network.\n")
                self.update_results("Make sure:\n")
                self.update_results("  • You're connected to WiFi\n")
                self.update_results("  • Cameras are powered on\n")
                self.update_results("  • Cameras are on the same network\n")
                return
                
            self.update_results(f"✅ Found {len(devices)} potential camera(s)\n\n")
            
            # Step 2: Check each device
            working_streams = []
            for device in devices:
                # Get device info
                host, port = self.parse_device(device)
                if not host:
                    continue
                    
                self.update_results(f"🔍 Checking camera at {host}:{port}...\n")
                
                # Try to get RTSP URL
                rtsp_urls = self.get_rtsp_urls(host, port)
                
                # Test each URL
                for url in rtsp_urls:
                    if self.test_rtsp_stream(url):
                        working_streams.append(url)
                        self.update_results(f"  ✅ Working stream: {url}\n")
                        
            # Step 3: Show summary
            self.update_results("\n" + "="*50 + "\n")
            self.update_results("📊 SUMMARY:\n")
            if working_streams:
                self.update_results(f"Found {len(working_streams)} working stream(s):\n\n")
                for url in working_streams:
                    self.update_results(f"  • {url}\n")
                self.update_results("\n✅ You can copy these URLs and use them in VLC or other players!\n")
            else:
                self.update_results("❌ No working streams found.\n")
                self.update_results("Try checking your camera settings or credentials.\n")
                
        except Exception as e:
            self.update_results(f"\n❌ Error: {str(e)}\n")
            
        finally:
            # Re-enable buttons
            self.window.after(0, lambda: self.wifi_button.config(state='normal'))
            self.window.after(0, lambda: self.dvr_button.config(state='normal'))
            
    def discover_onvif_devices(self, timeout=5):
        """Find ONVIF cameras on the network"""
        try:
            wsd = WSDiscovery()
            wsd.start()
            services = wsd.searchServices(timeout=timeout)
            wsd.stop()
            
            devices = []
            for service in services:
                xaddrs = service.getXAddrs()
                if xaddrs:
                    devices.append({'endpoint': xaddrs[0]})
            return devices
        except:
            return []
            
    def parse_device(self, device):
        """Extract IP and port from device info"""
        try:
            endpoint = device.get('endpoint', '')
            parsed = urlparse(endpoint)
            host = parsed.hostname
            port = parsed.port or 80
            return host, port
        except:
            return None, None
            
    def get_rtsp_urls(self, host, port):
        """Get RTSP URLs for a camera"""
        urls = []
        
        # Try ONVIF method first
        try:
            camera = ONVIFCamera(host, port, self.username, self.password)
            media = camera.create_media_service()
            profiles = media.GetProfiles()
            
            if profiles:
                profile_token = profiles[0].token
                req = media.create_type('GetStreamUri')
                req.ProfileToken = profile_token
                req.StreamSetup = {
                    'Stream': 'RTP-Unicast',
                    'Transport': {'Protocol': 'RTSP'}
                }
                resp = media.GetStreamUri(req)
                rtsp_url = resp.Uri
                
                # Add credentials to URL
                rtsp_with_auth = self.add_credentials_to_url(rtsp_url)
                urls.append(rtsp_with_auth)
        except:
            pass
            
        # Also try common RTSP paths
        common_paths = [
            f"rtsp://{self.username}:{self.password}@{host}:554/onvif1",
            f"rtsp://{self.username}:{self.password}@{host}:554/stream1",
            f"rtsp://{self.username}:{self.password}@{host}:554/h264",
        ]
        urls.extend(common_paths)
        
        return urls
        
    def add_credentials_to_url(self, url):
        """Add username and password to RTSP URL"""
        try:
            parsed = urlparse(url)
            if parsed.username:
                return url
            netloc = f"{self.username}:{self.password}@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            new_url = parsed._replace(netloc=netloc)
            return new_url.geturl()
        except:
            return url
            
    def test_rtsp_stream(self, url):
        """Test if RTSP stream is working using ffprobe"""
        try:
            cmd = [
                self.ffprobe_path,
                "-rtsp_transport", "tcp",
                "-v", "error",
                "-timeout", "5000000",
                "-i", url,
                "-show_entries", "stream=index",
                "-print_format", "json"
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
            
    def update_results(self, text):
        """Update the results text area (thread-safe)"""
        self.window.after(0, lambda: self.results_text.insert(tk.END, text))
        self.window.after(0, lambda: self.results_text.see(tk.END))
        
    def dvr_placeholder(self):
        """Show message for DVR button (not implemented yet)"""
        messagebox.showinfo(
            "Coming Soon",
            "DVR camera discovery will be available in a future update!"
        )
        
    def export_results(self):
        """Save results to a text file"""
        results = self.results_text.get(1.0, tk.END)
        if not results.strip():
            messagebox.showwarning("No Results", "No results to export!")
            return
            
        # Save to file
        filename = "camera_results.txt"
        with open(filename, 'w') as f:
            f.write(results)
            
        messagebox.showinfo(
            "Export Successful",
            f"Results saved to {filename}"
        )
        
    def run(self):
        """Start the application"""
        self.window.mainloop()


# This is where the program starts
if __name__ == "__main__":
    # Create and run the app
    app = CameraFinderApp()
    app.run()
