def does_firewall_open_all_ports_to_any(firewall):
    """
    Returns True if firewall has a rule to open all ports to any source. Excludes ICMP.

    >>> does_firewall_open_all_ports_to_any({})
    False
    >>> does_firewall_open_all_ports_to_any({'sourceRanges': ['1.1.1.1/1'], 'allowed': [{'ports': ['1', '2', '300']}]})
    False
    >>> does_firewall_open_all_ports_to_any({'sourceRanges': ['1.1.1.1/1'], 'allowed': [{'ports': ['0-65535']}]})
    True
    >>> does_firewall_open_all_ports_to_any({'sourceRanges': ['0.0.0.0/0'], 'allowed': [{'ports': ['0-65535']}]})
    True
    >>> does_firewall_open_all_ports_to_any({'sourceRanges': ['10.0.0.5/32'], 'allowed': [{'ports': ['0-65535']}]})
    True
    """
    if does_firewall_open_all_ports_to_all(firewall):
        return True

    if firewall.get("sourceRanges") is None:
        return False

    for rule in firewall.get("allowed"):
        if rule.get("IPProtocol", "") == "icmp":
            continue
        if not rule.get("ports"):
            return True
        for port_rule in rule.get("ports"):
            if port_rule == "0-65535":
                return True

    return False


def does_firewall_open_all_ports_to_all(firewall):
    """
    Returns True if firewall has a rule to open all ports to all. Excludes ICMP.

    >>> does_firewall_open_all_ports_to_all({})
    False
    >>> does_firewall_open_all_ports_to_all({'sourceRanges': ['1.1.1.1/1']})
    False
    >>> does_firewall_open_all_ports_to_all({'sourceRanges': ['1.1.1.1/1'], 'allowed': [{'ports': ['0-65535']}]})
    False
    >>> does_firewall_open_all_ports_to_all({'sourceRanges': ['0.0.0.0/0'], 'allowed': [{'ports': ['0-65535']}]})
    True
    """
    if (
        firewall.get("sourceRanges") is None
        or "0.0.0.0/0" not in firewall["sourceRanges"]
    ):
        return False

    for rule in firewall.get("allowed"):
        if rule.get("IPProtocol", "") == "icmp":
            continue
        if not rule.get("ports"):
            return True
        for port_rule in rule.get("ports"):
            if port_rule == "0-65535":
                return True

    return False


def does_firewall_open_any_ports_to_all(firewall, allowed_ports=None):
    """
    Returns True if firewall has a rule to open any ports (except 80/443) to all. Excludes ICMP.

    >>> does_firewall_open_any_ports_to_all({})
    False
    >>> does_firewall_open_any_ports_to_all({'sourceRanges': ['1.1.1.1/1']})
    False
    >>> does_firewall_open_any_ports_to_all({'sourceRanges': ['1.1.1.1/1'], 'allowed': [{'ports': ['0-65535']}]})
    False
    >>> does_firewall_open_any_ports_to_all({'sourceRanges': ['0.0.0.0/0'], 'allowed': [{'ports': ['0-65535']}]})
    True
    >>> does_firewall_open_any_ports_to_all({'sourceRanges': ['1.1.1.1/1'], 'allowed': [{'ports': ['123']}]})
    False
    >>> does_firewall_open_any_ports_to_all({'sourceRanges': ['0.0.0.0/0'], 'allowed': [{'ports': ['123']}]})
    True
    >>> does_firewall_open_any_ports_to_all({'sourceRanges': ['0.0.0.0/0'], 'allowed': [{'ports': ['80']}]})
    False
    >>> does_firewall_open_any_ports_to_all({'sourceRanges': ['0.0.0.0/0'], 'allowed': [{'ports': ['443']}]})
    False
    >>> does_firewall_open_any_ports_to_all({'sourceRanges': ['0.0.0.0/0'], 'allowed': [{'ports': ['22', '80', '443']}]})
    True
    """
    if allowed_ports is None:
        allowed_ports = []

    if does_firewall_open_all_ports_to_all(firewall):
        return True

    if (
        firewall.get("sourceRanges") is None
        or "0.0.0.0/0" not in firewall["sourceRanges"]
    ):
        return False

    for rule in firewall.get("allowed"):
        if rule.get("IPProtocol", "") == "icmp":
            continue
        for port_rule in rule.get("ports"):
            try:
                port_rule = int(port_rule)
            except ValueError:
                return True

            if port_rule in allowed_ports:
                continue

            if port_rule not in [80, 443]:
                return True

    return False


def firewall_id(firewall):
    """A getter fn for test ids for Firewalls"""
    return (
        "{}-{}".format(firewall["id"], firewall["name"])
        if hasattr(firewall, "__getitem__")
        else None
    )
