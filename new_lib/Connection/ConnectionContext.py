"""
The connection_context is a singleton to wrap everything needed to build ssh
connections.
"""
import paramiko
from Common.ConfigurationManagement import get_configuration


connection_context = None


def create_singleton():
    global connection_context

    config = get_configuration()
    connection_context = ConnectionContext(config["slice_name"],
                                           config["rsa_file"],
                                           config["known_hosts_file"])


class ConnectionContext:

    def __init__(self, default_username,
                 default_private_key,
                 known_hosts=None):
        self.username = default_username
        self.private_key = default_private_key
        self.known_hosts = known_hosts

    def get_ssh_connection(self, ip,
                           username=None,
                           private_key=None,
                           timeout=None):
        ssh = paramiko.SSHClient()
        # paramiko.util.log_to_file("paramiko.log")

        if self.known_hosts is None:
            ssh.load_host_keys(self.known_hosts)
            ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
        else:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if username is None:
            username = self.username
        if private_key is None:
            private_key = self.private_key

        ssh.connect(ip, username=username, key_filename=private_key,
                    timeout=timeout)
        return ssh

    # def getConnectionSafe(self, target, username=None, timeout=5):
    #     info = {}
    #     info["ip"] = target
    #     info["dns"] = target
    #     info["error"] = None
    #     info["errorTrace"] = None
    #
    #     if not is_valid_ip(target):
    #         info["ip"] = getIP_fromDNS(target)
    #         if info["ip"] == None:
    #             info["online"] = False
    #             info["error"] = "AddressError"
    #             info["errorTrace"] = "not valid ip address or DNS name"
    #             return info, None
    #
    #     info["online"] = ping(info["ip"])
    #     if info["online"]:
    #         try:
    #             con = self.getConnection(info["ip"], username, timeout)
    #             return info, con
    #         except paramiko.AuthenticationException:
    #             info["errorTrace"] = traceback.format_exc()
    #             info["error"] = "AuthenticationError"
    #             return info, None
    #         except paramiko.BadHostKeyException:
    #             info["errorTrace"] = traceback.format_exc()
    #             info["error"] = "BadHostKeyError"
    #             return info, None
    #         except:
    #             info["errorTrace"] = traceback.format_exc()
    #             info["error"] = "ConnectionError"
    #             return info, None
    #
    #     info["errorTrace"] = "Offline"
    #     info["error"] = "Offline"
    #     return info, None


if connection_context is None:
    create_singleton()
