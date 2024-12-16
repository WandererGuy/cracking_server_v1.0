import socket
import configparser

# Function to get the local IP address
def get_local_ip():
    # Get the local machine's hostname
    hostname = socket.gethostname()
    # Resolve the IP address of the local machine
    local_ip = socket.gethostbyname(hostname)
    return local_ip

# Define the path to your config.ini file
config_file = 'config.ini'

# Get the local IP address dynamically
new_ip = get_local_ip()

# Initialize the configparser
config = configparser.ConfigParser()

# Read the current configuration file
config.read(config_file)

# Modify the 'host' value in the appropriate section
config.set('DEFAULT', 'host', new_ip)

# Write the updated configuration back to the file
with open(config_file, 'w') as configfile:
    config.write(configfile)

print(f"Host IP address dynamically updated to: {new_ip}")
