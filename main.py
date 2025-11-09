













#for command line testing for retriving RTSP 


















#!/usr/bin/env python3
"""
Camera RTSP Finder - Python script

Features:
- Discover ONVIF devices on the local network using WS-Discovery.
- For each discovered device, call ONVIF GetStreamUri (if credentials provided).
- Verify RTSP URLs using ffprobe (forces TCP transport).
- If ONVIF doesn't return a usable RTSP URL, try a small list of common RTSP paths
  by sending OPTIONS probe and/or testing with ffprobe.

Requirements:
- pip install wsdiscovery onvif-zeep
- ffprobe (part of ffmpeg) installed and on PATH
"""

import subprocess
import socket
import sys
import time
from urllib.parse import quote, urlparse
from wsdiscovery import WSDiscovery
from onvif import ONVIFCamera

# change these timeout values if your network is slow
WS_DISCOVERY_TIMEOUT = 5
SOCKET_TIMEOUT = 3
FFPROBE_TIMEOUT = 8

COMMON_RTSP_PATHS = [
    "/onvif-media/media.amp",
    "/axis-media/media.amp",
    "/Streaming/Channels/101",
    "/ISAPI/Streaming/Channels/101",
    "/cam/realmonitor?channel=1&subtype=0",
    "/live.sdp",
    "/videoMain",
    "/video1",
    "/h264",
]

def discover_onvif_devices(timeout=WS_DISCOVERY_TIMEOUT):
    w = WSDiscovery()
    w.start()
    services = w.searchServices(timeout=timeout)
    devices = []
    for s in services:
        # s.getXAddrs() returns a list of service endpoints (XAddr)
        xaddrs = s.getXAddrs() or []
        endpoint = xaddrs[0] if xaddrs else None
        epr = s.getEPR()
        devices.append({"epr": epr, "xaddrs": xaddrs, "endpoint": endpoint})
    w.stop()
    return devices

def parse_xaddr(xaddr):
    # example xaddr: http://192.168.1.100:80/onvif/device_service
    if not xaddr:
        return None
    parsed = urlparse(xaddr)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    path = parsed.path or "/"
    return host, port, path

def get_stream_uri_via_onvif(host, port, username, password):
    """
    Connect to camera's ONVIF device service and request GetProfiles -> GetStreamUri for a profile.
    Returns RTSP URI string or None.
    """
    try:
        # ONVIFCamera wants host, port, user, pass
        dev = ONVIFCamera(host, port, username, password, no_cache=True)
        media_service = dev.create_media_service()
        profiles = media_service.GetProfiles()
        if not profiles:
            print(f"  - ONVIF: No profiles found on {host}:{port}")
            return None
        profile_token = profiles[0].token
        # Request stream URI (use "RTSP" as protocol)
        req = media_service.create_type('GetStreamUri')
        req.ProfileToken = profile_token
        req.StreamSetup = {
            'Stream': 'RTP-Unicast',
            'Transport': {'Protocol': 'RTSP'}
        }
        resp = media_service.GetStreamUri(req)
        rtsp_uri = getattr(resp, 'Uri', None) or resp.get('Uri', None)
        return rtsp_uri
    except Exception as e:
        print(f"  - ONVIF error for {host}:{port} -> {e}")
        return None

def url_with_credentials(rtsp, username, password):
    """Insert URL-encoded username:password into RTSP URL if not already present."""
    if not rtsp:
        return None
    parsed = urlparse(rtsp)
    # If credentials already present, return as-is
    if parsed.username:
        return rtsp
    user_enc = quote(username, safe='')
    pass_enc = quote(password, safe='')
    netloc = f"{user_enc}:{pass_enc}@{parsed.hostname}"
    if parsed.port:
        netloc += f":{parsed.port}"
    new = parsed._replace(netloc=netloc)
    return new.geturl()

def ffprobe_check(rtsp_url, timeout=FFPROBE_TIMEOUT):
    """
    Use ffprobe to check whether the RTSP URL is playable.
    Returns (ok:bool, output:str)
    Forces TCP transport for RTSP to avoid UDP firewall issues.
    """
    cmd = ["ffprobe", "-rtsp_transport", "tcp", "-v", "error", "-timeout", str(timeout*1000000), "-i", rtsp_url, "-show_entries", "stream=index", "-print_format", "json"]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        out = p.stdout.decode(errors='ignore') + "\n" + p.stderr.decode(errors='ignore')
        ok = p.returncode == 0
        return ok, out.strip()
    except subprocess.TimeoutExpired:
        return False, "ffprobe timed out"
    except FileNotFoundError:
        print("ffprobe not found - please install ffmpeg and ensure ffprobe is on PATH")
        sys.exit(1)

def rtsp_options_probe(host, port, path="/", timeout=SOCKET_TIMEOUT):
    """
    Send a minimal RTSP OPTIONS request to the device to see response (200 or 401).
    Returns (status_line_or_error, raw_response)
    """
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.settimeout(timeout)
        rtsp_url = f"rtsp://{host}:{port}{path}"
        req = f"OPTIONS {rtsp_url} RTSP/1.0\r\nCSeq: 1\r\nUser-Agent: rtsp-probe\r\n\r\n"
        s.sendall(req.encode())
        data = s.recv(4096)
        s.close()
        return data.decode(errors='ignore').splitlines()[0] if data else "no-response", data.decode(errors='ignore')
    except Exception as e:
        return f"error: {e}", ""

def brute_force_rtsp(host, port, username, password, paths=COMMON_RTSP_PATHS, try_options=True):
    """
    Try common RTSP paths. For each path:
      - send an RTSP OPTIONS probe (socket) to check for 200/401
      - if response promising, build URL with credentials and test with ffprobe
    Returns (list_of_successful_urls, details)
    """
    successes = []
    details = []
    for p in paths:
        try:
            if try_options:
                status, raw = rtsp_options_probe(host, port, p)
                details.append((p, status))
                # If no response, continue but still try ffprobe (some devices don't answer OPTIONS)
                if status.startswith("error") or status == "no-response":
                    # still attempt ffprobe in case
                    pass
                elif "200" in status or "401" in status:
                    # promising, test with ffprobe
                    rtsp = f"rtsp://{host}:{port}{p}"
                    rtsp_with_creds = url_with_credentials(rtsp, username, password)
                    ok, out = ffprobe_check(rtsp_with_creds)
                    if ok:
                        successes.append(rtsp_with_creds)
                        # early exit if you want first working stream
                        # return successes, details
            else:
                rtsp = f"rtsp://{host}:{port}{p}"
                rtsp_with_creds = url_with_credentials(rtsp, username, password)
                ok, out = ffprobe_check(rtsp_with_creds)
                if ok:
                    successes.append(rtsp_with_creds)
        except Exception as e:
            details.append((p, f"exception: {e}"))
    return successes, details

def main():
    print("Discovering ONVIF devices on the network (WS-Discovery)...")
    devices = discover_onvif_devices()
    if not devices:
        print("No ONVIF devices discovered.")
    else:
        print(f"Discovered {len(devices)} services/devices (may include duplicates).")
    # ask user for username/password to attempt ONVIF and RTSP checks
    username = input("Camera username (press Enter to skip credentials): ").strip()
    password = input("Camera password (press Enter to skip credentials): ").strip()

    # normalize devices map by host
    seen_hosts = {}
    for d in devices:
        endpoint = d.get("endpoint")
        if not endpoint and d.get("xaddrs"):
            endpoint = d["xaddrs"][0]
        parsed = parse_xaddr(endpoint)
        if not parsed:
            continue
        host, port, path = parsed
        if host in seen_hosts:
            seen_hosts[host].append((port, path))
        else:
            seen_hosts[host] = [(port, path)]

    results = []
    for host, entries in seen_hosts.items():
        for port, path in entries:
            print("\n---")
            print(f"Device: {host}:{port} (ONVIF endpoint: {path})")
            rtsp_uri = None
            if username and password:
                print("  Trying ONVIF GetStreamUri...")
                rtsp_uri = get_stream_uri_via_onvif(host, port, username, password)
                if rtsp_uri:
                    print(f"  ONVIF returned RTSP URI: {rtsp_uri}")
                    # ensure credentials inserted
                    rtsp_with_creds = url_with_credentials(rtsp_uri, username, password)
                    print("  Verifying with ffprobe (TCP transport)...")
                    ok, out = ffprobe_check(rtsp_with_creds)
                    if ok:
                        print("  => RTSP playable!")
                        results.append({"host": host, "port": port, "rtsp": rtsp_with_creds, "method": "ONVIF"})
                        continue
                    else:
                        print("  ffprobe failed for ONVIF RTSP. ffprobe output:")
                        print(out[:1000])  # print truncated
                else:
                    print("  ONVIF did not provide a usable RTSP URI.")
            else:
                print("  No credentials provided — skipping ONVIF GetStreamUri.")

            # If we reach here, ONVIF failed or not used. Try brute-force common paths:
            print("  Trying common RTSP paths (safe brute force)...")
            successes, details = brute_force_rtsp(host, port, username, password)
            if successes:
                for s in successes:
                    print(f"  Found playable RTSP: {s}")
                    results.append({"host": host, "port": port, "rtsp": s, "method": "BRUTE"})
            else:
                print("  No working RTSP found from common paths. Details:")
                for p, status in details:
                    print(f"    {p} -> {status}")

    print("\n======== Summary ========")
    if results:
        for r in results:
            print(f"{r['host']}:{r['port']}  [{r['method']}] -> {r['rtsp']}")
    else:
        print("No working RTSP streams found. Check network/firewall, credentials, and try again.")
        print("If ODM finds streams, capture a Wireshark pcap of ODM's discovery + RTSP exchange and compare to this tool's logs.")

if __name__ == "__main__":
    main()
