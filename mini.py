import psutil
import time
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import socket

# Threshold in Mbps
THRESHOLD = 10  # Alert threshold

# Lists to store data for plotting
time_stamps = []
download_speeds = []
upload_speeds = []
network_info = {}

# Function to fetch active network interfaces and their IP addresses
def get_network_interfaces():
    interfaces = psutil.net_if_addrs()
    active_interfaces = {}
    for iface, addrs in interfaces.items():
        for addr in addrs:
            if addr.family == socket.AF_INET:  # IPv4 address
                active_interfaces[iface] = addr.address
    return active_interfaces

# Function to fetch network stats
def get_network_usage(interval=1):
    prev_net_io = psutil.net_io_counters()
    time.sleep(interval)
    curr_net_io = psutil.net_io_counters()
    
    # Calculate bytes sent and received
    bytes_sent = curr_net_io.bytes_sent - prev_net_io.bytes_sent
    bytes_recv = curr_net_io.bytes_recv - prev_net_io.bytes_recv
    
    # Convert to Mbps
    download_speed = (bytes_recv * 8) / (1024 * 1024) / interval  # Mbps
    upload_speed = (bytes_sent * 8) / (1024 * 1024) / interval  # Mbps
    
    return download_speed, upload_speed

# Background function to monitor bandwidth and fetch network details
def monitor_bandwidth():
    global time_stamps, download_speeds, upload_speeds, network_info
    start_time = time.time()
    
    # Fetch active interfaces and IPs once
    network_info = get_network_interfaces()
    print(f"Active Network Interfaces and IPs: {network_info}\n")
    
    while True:
        try:
            download, upload = get_network_usage()
        except Exception as e:
            print(f"Error in fetching network usage: {e}")
            continue
        
        # Add data to lists
        current_time = time.time() - start_time
        time_stamps.append(current_time)
        download_speeds.append(download)
        upload_speeds.append(upload)
        
        # Alert if threshold exceeded
        if download > THRESHOLD or upload > THRESHOLD:
            print(f"⚠ Alert! Bandwidth usage exceeded: Download = {download:.2f} Mbps, Upload = {upload:.2f} Mbps")
        
        # Debug information
        print(f"Time: {current_time:.2f}s | Download: {download:.2f} Mbps | Upload: {upload:.2f} Mbps")
        
        # Keep lists limited to the last 100 points for efficient plotting
        if len(time_stamps) > 100:
            time_stamps.pop(0)
            download_speeds.pop(0)
            upload_speeds.pop(0)
        
        time.sleep(1)

# Function to update the graph
def update_graph(frame):
    plt.cla()
    
    if time_stamps:
        # Plot the bandwidth usage
        plt.plot(time_stamps, download_speeds, label='Download (Mbps)', color='blue')
        plt.plot(time_stamps, upload_speeds, label='Upload (Mbps)', color='green')
        plt.xlabel('Time (s)')
        plt.ylabel('Speed (Mbps)')
        plt.title('Real-Time Bandwidth Monitoring with Network Info')
        plt.legend()
        plt.grid()
    
    # Display active network interfaces
    network_text = "\n".join([f"{iface}: {ip}" for iface, ip in network_info.items()])
    plt.text(0.02, 0.85, f"Active Network Interfaces:\n{network_text}", 
             transform=plt.gcf().transFigure, fontsize=10, color='black', bbox=dict(facecolor='white', alpha=0.8))

# Start monitoring in a separate thread
threading.Thread(target=monitor_bandwidth, daemon=True).start()

# Initialize live graph
fig = plt.figure()
ani = FuncAnimation(fig, update_graph, interval=1000, cache_frame_data=False, blit=False)
plt.show()