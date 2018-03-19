

def does_firewall_open_all_ports_to_all(firewall):
    """
    TODO
    """
    if firewall.get("sourceRanges") is None or "0.0.0.0/0" not in firewall['sourceRanges']:
        return False

    if not firewall.get('allowed', [])[0].get('ports'):
        if firewall.get('allowed', [])[0].get('IPProtocol', '') != 'icmp':
            return True

    for rule in firewall.get('allowed'):
        if rule.get('ports') == '0-65535' and rule.get('IPProtocol', '') != 'icmp':
            return True

    return False


def firewall_id(firewall):
    """
    TODO
    """
    return "{} {}".format(firewall['id'], firewall['name'])
