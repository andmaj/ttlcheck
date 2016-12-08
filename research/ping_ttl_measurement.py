"""
This measurement tests if on the internet some party modifies the ttl field
of packets.

Scenarion:
On the destination host all the incoming ping requests are logged, with the
ttl fields.
From all the avaiable machines we send  ping requests to the destination with
the maximum allowed TTL feild, 250.

If the received pakcet's TTL is less then 200 we can be sure that though the
route of the packet some middlebox manipulated the packet.
"""
from lib import RemoteScripting as rs
from Common import ConfigurationManagement
from Common import LoggingManagement
import re

logger = None
config = None


def main():
    logger.info("Starting measurement: Checking ping ttl modification")

    logger.info("Initializing ConnectionBuilder")
    conn_builder = rs.ConnectionBuilder(config["slice_name"],
                                        config["rsa_file"],
                                        config["known_hosts_file"])

    destination_info = config["ping_destination"]
    logger.info("Creating connection to ping destination: %s",
                destination_info["ip"])
    dest_conn = rs.Connection(destination_info["ip"],
                              destination_info["username"],
                              conn_builder)

    if not dest_conn.connect():
        logger.error("Connection to ping destination (%s) failed: %s",
                     destination_info["ip"],
                     dest_conn.error)
        # return

    start_listening(dest_conn)

    logger.info("Measurement ended")


def start_listening(connection):
    logger.info("Start listening for incoming ping requests.")
    # sudo tcpdump -vnn -i p21p1 icmp[icmptype] == 8 and dst host 152.66.247.138
    interface = get_interface_for_ip(connection)

    if interface is None:
        logger.error("Measurement failed, no public interface found for ping "
                     "destination!")
        exit(-1)

    cmd = "sudo tcpdump -vnn -i {interface} " \
          "icmp[icmptype] == 8 and dst host {ip}"\
        .format(interface=interface, ip=connection.ip)
    connection.startCommand(cmd)


def get_interface_for_ip(connection):
    logger.info("Get interface for machine: %s", connection.ip)
    ip = connection.ip
    # Regexp for ifconfig output to find interface and port pairs
    find_interface_ip_pairs = r"^([\w\d]+):[^\n]+\n\s+inet\s+(\d+.\d+.\d+.\d+)"
    cmd = "ifconfig"
    stdout, stderr = connection.runCommand(cmd)
    logger.debug("Response for command '%s': \n%s",
                 cmd, stdout)
    matcher = re.compile(find_interface_ip_pairs, re.MULTILINE)
    found_pairs = matcher.findall(stdout)
    for found_pair in found_pairs:
        if found_pair[1] == ip:
            logger.info("Interface found: %s", found_pair[0])
            return found_pair[0]

    logger.error("No public interface found for host: %s", connection.ip)
    return None


if __name__ == '__main__':
    config = ConfigurationManagement.get_configuration()
    logger = LoggingManagement.get_logger(__name__)
    main()
