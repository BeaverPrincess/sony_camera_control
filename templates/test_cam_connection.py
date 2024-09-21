import socket

SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900
SSDP_MX = 1
SSDP_ST = "urn:schemas-sony-com:service:ScalarWebAPI:1"
USER_AGENT = "python-requests/2.32.3"

def discover_camera():
    ssdp_request = f'''M-SEARCH * HTTP/1.1
    HOST: {SSDP_ADDR}:{SSDP_PORT}
    MAN: "ssdp:discover"
    MX: {SSDP_MX}
    ST: {SSDP_ST}
    USER-AGENT: {USER_AGENT}\r\n\r\n'''
    
    print("Sending SSDP discovery request...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.settimeout(5)
    sock.sendto(ssdp_request.encode(), (SSDP_ADDR, SSDP_PORT))
    
    try:
        response, addr = sock.recvfrom(1024)
        print(f"Received response from {addr}:\n{response.decode()}")
        return response.decode()
    except socket.timeout:
        print("SSDP discovery timed out.")
        return None

# Function to extract camera endpoint URL from SSDP response
def extract_endpoint(ssdp_response):
    if ssdp_response:
        for line in ssdp_response.splitlines():
            if "LOCATION" in line:
                endpoint = line.split(": ")[1]
                print(f"Extracted endpoint URL: {endpoint}")
                return endpoint
    print("No LOCATION header found in the response.")
    return None

def main():
    ssdp_response = discover_camera()
    
    if not ssdp_response:
        print("Camera not found.")
        return
    
    endpoint_url = extract_endpoint(ssdp_response)
    if endpoint_url:
        print(f"Camera endpoint successfully retrieved: {endpoint_url}")
    else:
        print("Failed to retrieve camera endpoint.")

if __name__ == "__main__":
    main()