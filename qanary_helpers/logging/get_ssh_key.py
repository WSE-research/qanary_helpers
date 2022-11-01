import socket
import paramiko
from pathlib import Path
import os


def load_ssh_host_key(host, ssh_port):
    """
    Load the SSH host key of a remote server and stores it as a known host
    """
    with socket.socket() as sock:
        # init connection
        sock.connect((host, int(ssh_port)))

        # establish connection
        trans = paramiko.transport.Transport(sock)
        trans.start_client()

        # load host key
        key = trans.get_remote_server_key().get_base64()

        trans.close()

    # home directory of executing user
    home_dir = Path.home()

    # SSH host key entry
    host_key = f'{host} ssh-ed25519 {key}'

    # no SSH config for current user
    if not os.path.exists(f'{home_dir}/.ssh'):
        os.mkdir(f'{home_dir}/.ssh')

        # create new known hosts file and store key
        with open(f'{home_dir}/.ssh/known_hosts', 'w') as f:
            f.write(host_key)
    # SSH config exists
    else:
        # loading existing config
        with open(f'{home_dir}/.ssh/known_hosts') as f:
            hosts = f.read()

            if not hosts.endswith('\n'):
                hosts += '\n'

        # SSH host key not known
        if host_key not in hosts:
            # add key to config file
            with open(f'{home_dir}/.ssh/known_hosts', 'w') as f:
                f.write(hosts)
                f.write(host_key)


if __name__ == '__main__':
    load_ssh_host_key()
