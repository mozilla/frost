

def does_firewall_open_all_ports_to_all(firewall):
    """
    Returns True if firewall has a rule to open all ports to all. Excludes ICMP.

    >>> does_firewall_open_all_ports_to_all({})
    False
    >>> does_firewall_open_all_ports_to_all({'sourceRanges': ['1.1.1.1/1']})
    False
    >>> does_firewall_open_all_ports_to_all({'sourceRanges': ['1.1.1.1/1'], 'allowed': [{'ports': '0-65535'}]})
    False
    >>> does_firewall_open_all_ports_to_all({'sourceRanges': ['0.0.0.0/0'], 'allowed': [{'ports': '0-65535'}]})
    True
    """
    if firewall.get("sourceRanges") is None or "0.0.0.0/0" not in firewall['sourceRanges']:
        return False

    for rule in firewall.get('allowed'):
        if rule.get('IPProtocol', '') == 'icmp':
            continue
        if not rule.get('ports'):
            return True
        if rule.get('ports') == '0-65535':
            return True

    return False


def firewall_id(firewall):
    """A getter fn for test ids for Firewalls"""
    return "{} {}".format(firewall['id'], firewall['name'])
