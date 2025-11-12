#!/usr/bin/env python3
"""
Fixed Camera Discovery GUI - Works properly when compiled to .exe
Handles wsdiscovery issues and includes all dependencies
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import socket
import os
import sys
import time
import logging
from urllib.parse import quote, urlparse

# Suppress the probe handler warning
logging.getLogger('daemon').setLevel(logging.ERROR)

# Fix for PyInstaller bundling
if hasattr(sys, '_MEIPASS'):
    # Running as bundled exe
    bundle_dir = sys._MEIPASS
else:
    # Running as script
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Import with error handling for better exe compatibility
try:
    from wsdiscovery import WSDiscovery
    from wsdiscovery.actions import *
    WSDISCOVERY_AVAILABLE = True
    print("✅ WS-Discovery library loaded successfully")
except ImportError as e:
    WSDISCOVERY_AVAILABLE = False
    print(f"⚠️ WS-Discovery not available: {e}")
    print("Will use direct IP scanning instead")

try:
    from onvif import ONVIFCamera
    ONVIF_AVAILABLE = True
    print("✅ ONVIF library loaded successfully")
    
    # Verify WSDL files are accessible (critical for exe)
    import onvif
    onvif_path = os.path.dirname(onvif.__file__)
    wsdl_path = os.path.join(onvif_path, 'wsdl')
    if os.path.exists(wsdl_path):
        wsdl_files = [f for f in os.listdir(wsdl_path) if f.endswith('.wsdl')]
        print(f"✅ Found {len(wsdl_files)} ONVIF WSDL files")
    else:
        print(f"⚠️ ONVIF WSDL folder not found at: {wsdl_path}")
        print("Camera discovery via ONVIF may not work!")
except ImportError as e:
    ONVIF_AVAILABLE = False
    print(f"⚠️ ONVIF not available: {e}")
    print("Will use common RTSP paths only")
except Exception as e:
    print(f"⚠️ ONVIF loaded but WSDL check failed: {e}")


class CameraFinderApp:
    """Simple camera finder that works as portable exe"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("AlgoOrange Camera Finder - Portable")
        self.window.geometry("850x650")
        self.window.configure(bg='#f0f0f0')
        
        # Store credentials
        self.username = ""
        self.password = ""
        
        # Create GUI
        self.create_widgets()
        
        # Get ffprobe path
        self.ffprobe_path = self.get_ffprobe_path()
        
    def get_ffprobe_path(self):
        """Find ffprobe - check bundled location first"""
        # For exe bundle
        if hasattr(sys, '_MEIPASS'):
            bundled_ffprobe = os.path.join(sys._MEIPASS, "ffprobe.exe")
            print(f"Checking bundled ffprobe: {bundled_ffprobe}")
            if os.path.exists(bundled_ffprobe):
                print("✅ Found bundled ffprobe")
                return bundled_ffprobe
            else:
                print("⚠️ Bundled ffprobe not found")
        
        # Check local folder (current directory)
        local_ffprobe = "ffprobe.exe"
        if os.path.exists(local_ffprobe):
            print(f"✅ Found local ffprobe: {os.path.abspath(local_ffprobe)}")
            return os.path.abspath(local_ffprobe)
        
        # Check script directory
        script_dir_ffprobe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffprobe.exe")
        if os.path.exists(script_dir_ffprobe):
            print(f"✅ Found script dir ffprobe: {script_dir_ffprobe}")
            return script_dir_ffprobe
            
        # Fall back to system PATH
        print("⚠️ Using system PATH ffprobe")
        return "ffprobe"

    # def resource_path(relative_path):
    #     """Return absolute path to resource, works for dev and PyInstaller onefile."""
    #     if getattr(sys, "frozen", False):
    #         # PyInstaller bundles files in _MEIPASS
    #         base_path = sys._MEIPASS
    #     else:
    #         base_path = os.path.abspath(os.path.dirname(__file__))
    #     return os.path.join(base_path, relative_path)    
        
    def create_widgets(self):
        """Create the GUI elements"""
        
        # Title
        title_label = tk.Label(
            self.window,
            text="📷 AlgoOrange Camera Finder",
            font=("Arial", 22, "bold"),
            bg='#f0f0f0'
        )
        title_label.pack(pady=15)
        
        # Instructions
        instruction_label = tk.Label(
            self.window,
            text="Discover IP cameras on your network - No installation required!",
            font=("Arial", 12),
            bg='#f0f0f0'
        )
        instruction_label.pack(pady=5)
        
        # Status label
        self.status_label = tk.Label(
            self.window,
            text="Ready to scan",
            font=("Arial", 10, "italic"),
            bg='#f0f0f0',
            fg='#666'
        )
        self.status_label.pack(pady=5)
        
        # Button frame
        button_frame = tk.Frame(self.window, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        # WiFi Cameras button
        self.wifi_button = tk.Button(
            button_frame,
            text="🔍 Scan for WiFi Cameras",
            font=("Arial", 14, "bold"),
            bg='#4CAF50',
            fg='white',
            width=20,
            height=2,
            command=self.find_wifi_cameras
        )
        self.wifi_button.pack(side=tk.LEFT, padx=10)
        
        # Quick Scan button (alternative method)
        self.quick_button = tk.Button(
            button_frame,
            text="⚡ Quick IP Scan",
            font=("Arial", 14, "bold"),
            bg='#FF9800',
            fg='white',
            width=20,
            height=2,
            command=self.quick_ip_scan
        )
        self.quick_button.pack(side=tk.LEFT, padx=10)
        
        # Results label
        results_label = tk.Label(
            self.window,
            text="Discovered Cameras:",
            font=("Arial", 12, "bold"),
            bg='#f0f0f0'
        )
        results_label.pack(pady=(15, 5))
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(
            self.window,
            width=95,
            height=22,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.results_text.pack(padx=20, pady=10)
        
        # Button frame for actions
        action_frame = tk.Frame(self.window, bg='#f0f0f0')
        action_frame.pack(pady=5)
        
        # Export button
        self.export_button = tk.Button(
            action_frame,
            text="💾 Export Results",
            font=("Arial", 11),
            bg='#2196F3',
            fg='white',
            width=15,
            command=self.export_results
        )
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_button = tk.Button(
            action_frame,
            text="🗑️ Clear",
            font=("Arial", 11),
            bg='#9E9E9E',
            fg='white',
            width=10,
            command=lambda: self.results_text.delete(1.0, tk.END)
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
    def find_wifi_cameras(self):
        """Main camera discovery using ONVIF/WS-Discovery"""
        self.get_credentials()
        if not self.username:
            return
            
        self.start_search("ONVIF Discovery")
        
    def quick_ip_scan(self):
        """Alternative quick scan method - scans common camera ports"""
        self.get_credentials()
        if not self.username:
            return
            
        self.start_search("Quick IP Scan")
        
    def start_search(self, method):
        """Start the search in a background thread"""
        self.results_text.delete(1.0, tk.END)
        self.update_status("🔍 Scanning network...")
        
        # Disable buttons during search
        self.wifi_button.config(state='disabled')
        self.quick_button.config(state='disabled')
        
        # Start search thread
        thread = threading.Thread(target=self.search_thread, args=(method,))
        thread.daemon = True
        thread.start()
        
    def search_thread(self, method):
        """Background search thread"""
        try:
            if method == "ONVIF Discovery":
                self.onvif_discovery_search()
            else:
                self.quick_scan_search()
        except Exception as e:
            self.update_results(f"❌ Error: {str(e)}\n")
        finally:
            self.update_status("Ready to scan")
            self.window.after(0, lambda: self.wifi_button.config(state='normal'))
            self.window.after(0, lambda: self.quick_button.config(state='normal'))
            
    def onvif_discovery_search(self):
        """ONVIF/WS-Discovery search method"""
        self.update_results("📡 Starting ONVIF discovery...\n")
        self.update_results("This may take 10-20 seconds...\n\n")
        
        devices = []
        
        # Try WS-Discovery if available
        if WSDISCOVERY_AVAILABLE:
            try:
                devices = self.discover_with_wsdiscovery()
            except Exception as e:
                self.update_results(f"⚠️ WS-Discovery failed: {e}\n")
                self.update_results("Falling back to IP scanning...\n\n")
        
        # If no devices found, try IP scanning
        if not devices:
            devices = self.scan_network_ips()
            
        if not devices:
            self.update_results("❌ No cameras found.\n")
            self.update_results("\nTroubleshooting:\n")
            self.update_results("• Ensure cameras are powered on\n")
            self.update_results("• Check you're on the same network\n")
            self.update_results("• Try the Quick IP Scan method\n")
            self.update_results("• Check firewall settings\n")
            return
            
        self.update_results(f"✅ Found {len(devices)} potential camera(s)\n\n")
        self.process_devices(devices)
        
    def discover_with_wsdiscovery(self):
        """Use WS-Discovery to find devices"""
        devices = []
        try:
            # Create discovery instance
            wsd = WSDiscovery()
            wsd.start()
            
            # Search for services
            services = wsd.searchServices(timeout=5)
            
            for service in services:
                xaddrs = service.getXAddrs()
                if xaddrs:
                    for xaddr in xaddrs:
                        parsed = urlparse(xaddr)
                        if parsed.hostname:
                            devices.append({
                                'host': parsed.hostname,
                                'port': parsed.port or 80,
                                'endpoint': xaddr
                            })
            
            wsd.stop()
        except Exception as e:
            print(f"WS-Discovery error: {e}")
            
        return devices
        
    def scan_network_ips(self):
        """Scan local network for cameras on common ports"""
        devices = []
        self.update_results("🔍 Scanning local network IPs...\n")
        
#=======================================================================
# dynamically gets your local IP and scans that subnet
#=======================================================================
        # Get local IP to determine subnet
        local_ip = self.get_local_ip()
        if not local_ip:
            return devices
            
        # Extract subnet (e.g., 192.168.1)
        parts = local_ip.split('.')
        subnet = '.'.join(parts[:3])
        
        self.update_results(f"Scanning subnet {subnet}.x\n")
        
        # Common camera ports
        ports = [80, 8080, 554, 8000, 8899]
        
        # Scan range (adjust as needed)
        for i in range(1, 255):
            ip = f"{subnet}.{i}"
            for port in ports:
                if self.check_port(ip, port):
                    devices.append({
                        'host': ip,
                        'port': port,
                        'endpoint': f"http://{ip}:{port}"
                    })
                    self.update_results(f"  Found device at {ip}:{port}\n")
                    
        return devices
        
    def quick_scan_search(self):
        """Quick scan method - faster but less thorough"""
        self.update_results("⚡ Quick IP scan starting...\n")
        self.update_results("Scanning common camera ports...\n\n")
        
        devices = self.scan_network_ips()
        
        if devices:
            self.update_results(f"\n✅ Found {len(devices)} device(s)\n\n")
            self.process_devices(devices)
        else:
            self.update_results("❌ No devices found on common ports.\n")
            
    def process_devices(self, devices):
        """Process found devices and get RTSP URLs"""
        working_streams = []
        
        for device in devices:
            host = device['host']
            port = device.get('port', 80)
            
            self.update_results(f"🎥 Checking camera at {host}:{port}...\n")
            
            # Get RTSP URLs
            rtsp_urls = self.get_rtsp_urls(host, port)
            
            # Test each URL
            for url in rtsp_urls:
                self.update_results(f"  Testing: {url[:50]}...\n")
                if self.test_rtsp_stream(url):
                    working_streams.append(url)
                    self.update_results(f"  ✅ Working stream found!\n")
                    break
                    
        # Show summary
        self.update_results("\n" + "="*60 + "\n")
        self.update_results("📊 SCAN COMPLETE\n")
        if working_streams:
            self.update_results(f"Found {len(working_streams)} working stream(s):\n\n")
            for url in working_streams:
                self.update_results(f"• {url}\n")
            self.update_results("\n✅ Copy these URLs to use in VLC or other players!\n")
        else:
            self.update_results("❌ No working streams found.\n")
            self.update_results("Try different credentials or check camera settings.\n")
            
    def get_rtsp_urls(self, host, port):
        """Generate possible RTSP URLs for a camera"""
        urls = []
        
        # Try ONVIF if available
        if ONVIF_AVAILABLE:
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
                    urls.append(self.add_credentials_to_url(rtsp_url))
            except:
                pass
        
        # Common RTSP URL patterns - try multiple ports and paths
        # Based on successful discoveries
        # Order matters! More specific/unique paths first
        common_ports = [554, 5543, 8554]  # Common RTSP ports
        common_paths_list = [
            # Most specific paths first (your working cameras)
            "/ch0_0.264",
            "/live/channel0",
            "/ch0_0.h264",
            "/ch0_1.264",
            # Hikvision/Dahua specific
            "/Streaming/Channels/101",
            "/Streaming/Channels/102",
            "/cam/realmonitor?channel=1&subtype=0",
            # Common generic paths
            "/stream1",
            "/stream2",
            "/h264",
            "/h265",
            "/onvif1",
            "/onvif2",
            "/live.sdp",
            "/video.mjpg",
            "/video.h264",
            "/1",
            "/",  # Root path last (least specific)
        ]
        
        # Try different port and path combinations
        for rtsp_port in common_ports:
            for path in common_paths_list:
                url = f"rtsp://{self.username}:{self.password}@{host}:{rtsp_port}{path}"
                urls.append(url)
        
        return urls
        
    def add_credentials_to_url(self, url):
        """Add credentials to RTSP URL"""
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
        """Test if RTSP stream works using ffprobe"""
        try:
            # Check if ffprobe exists
            if not os.path.exists(self.ffprobe_path):
                self.update_results(f"  ⚠️ ffprobe not found at: {self.ffprobe_path}\n")
                return False
                
            cmd = [
                self.ffprobe_path,
                "-rtsp_transport", "tcp",
                "-v", "quiet",
                "-timeout", "3000000",
                "-i", url,
                "-show_entries", "stream=codec_type",
                "-print_format", "json"
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=5)  # Increased timeout
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            # Log error for debugging
            self.update_results(f"  ⚠️ ffprobe error: {str(e)}\n")
            return False
            
    def check_port(self, host, port, timeout=0.5):
        """Check if a port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
            
    def get_local_ip(self):
        """Get the local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return None
            
    def get_credentials(self):
        """Get username and password from user"""
        popup = tk.Toplevel(self.window)
        popup.title("Camera Login")
        popup.geometry("350x200")
        popup.configure(bg='white')
        popup.transient(self.window)
        popup.grab_set()
        
        tk.Label(
            popup,
            text="Enter Camera Credentials",
            font=("Arial", 14, "bold"),
            bg='white'
        ).pack(pady=10)
        
        tk.Label(popup, text="Username:", font=("Arial", 11), bg='white').pack()
        username_entry = tk.Entry(popup, width=30, font=("Arial", 11))
        username_entry.pack(pady=5)
        username_entry.insert(0, "admin")
        
        tk.Label(popup, text="Password:", font=("Arial", 11), bg='white').pack()
        password_entry = tk.Entry(popup, width=30, show="*", font=("Arial", 11))
        password_entry.pack(pady=5)
        
        def save_and_close():
            self.username = username_entry.get()
            self.password = password_entry.get()
            popup.destroy()
            
        tk.Button(
            popup,
            text="Start Scan",
            command=save_and_close,
            bg='#4CAF50',
            fg='white',
            font=("Arial", 11),
            width=12
        ).pack(pady=15)
        
        popup.wait_window()
        
    def update_results(self, text):
        """Thread-safe update of results"""
        self.window.after(0, lambda: self.results_text.insert(tk.END, text))
        self.window.after(0, lambda: self.results_text.see(tk.END))
        
    def update_status(self, text):
        """Update status label"""
        self.window.after(0, lambda: self.status_label.config(text=text))
        
    def export_results(self):
        """Export results to file"""
        results = self.results_text.get(1.0, tk.END)
        if not results.strip():
            messagebox.showwarning("No Results", "No results to export!")
            return
            
        filename = f"camera_scan_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(results)
            
        messagebox.showinfo("Export Successful", f"Results saved to {filename}")
        
    def run(self):
        """Start the application"""
        self.window.mainloop()


if __name__ == "__main__":
    app = CameraFinderApp()
    app.run()
