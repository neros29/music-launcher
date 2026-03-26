import socket, sys, json

# Usage: python mpv_client.py '/tmp/mpvsocket' '{"command":["get_property","playback-time"]}'

sock_path = sys.argv[1]
cmd = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read().strip()

# Ensure command ends with newline (required by mpv)
if not cmd.endswith('\n'):
    cmd += '\n'

# Create and connect socket
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(sock_path)
client.send(cmd.encode())

# Read response until newline
response = b''
while True:
    chunk = client.recv(1024)
    if not chunk:
        break
    response += chunk
    if b'\n' in chunk:
        break

client.close()

# Parse and print JSON response
try:
    result = json.loads(response.decode().strip())
    print(json.dumps(result, indent=2))
except:
    print(response.decode())
