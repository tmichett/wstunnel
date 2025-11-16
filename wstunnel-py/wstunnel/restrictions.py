import yaml
import re
import ipaddress

class Restrictions:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def is_allowed(self, remote_host, remote_port, path_prefix, authorization):
        for restriction in self.config.get('restrictions', []):
            if self._matches(restriction, path_prefix, authorization):
                return self._is_allowed(restriction, remote_host, remote_port)
        return False

    def _matches(self, restriction, path_prefix, authorization):
        for match in restriction.get('match', []):
            if 'Any' in match:
                return True
            if 'PathPrefix' in match and re.match(match['PathPrefix'], path_prefix):
                return True
            if 'Authorization' in match and authorization and re.match(match['Authorization'], authorization):
                return True
        return False

    def _is_allowed(self, restriction, remote_host, remote_port):
        for allow in restriction.get('allow', []):
            if 'Tunnel' in allow:
                tunnel_config = allow['Tunnel']
                if self._is_host_allowed(tunnel_config, remote_host) and \
                   self._is_port_allowed(tunnel_config, remote_port):
                    return True
        return False
    
    def _is_host_allowed(self, config, remote_host):
        if 'host' in config and not re.match(config['host'], remote_host):
            return False
        if 'cidr' in config:
            remote_ip = ipaddress.ip_address(remote_host)
            for cidr in config['cidr']:
                if remote_ip in ipaddress.ip_network(cidr):
                    return True
            return False
        return True

    def _is_port_allowed(self, config, remote_port):
        if 'port' in config:
            for port_range in config['port']:
                if '..' in port_range:
                    start, end = port_range.split('..')
                    if int(start) <= remote_port <= int(end):
                        return True
                elif int(port_range) == remote_port:
                    return True
            return False
        return True
