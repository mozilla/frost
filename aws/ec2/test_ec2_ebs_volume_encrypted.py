import pytest

from aws.ec2.resources import ec2_ebs_volumes

def is_ebs_volume_encrypted(ebs):
    """
    Checks the EBS volume 'Encrypted' value.

    >>> is_ebs_volume_encrypted({'Encrypted': True})
    True
    >>> is_ebs_volume_encrypted({'Encrypted': False})
    False
    >>> is_ebs_volume_encrypted({})
    Traceback (most recent call last):
    ...
    KeyError: 'Encrypted'
    >>> is_ebs_volume_encrypted(0)
    Traceback (most recent call last):
    ...
    TypeError: 'int' object is not subscriptable
    >>> is_ebs_volume_encrypted(None)
    Traceback (most recent call last):
    ...
    TypeError: 'NoneType' object is not subscriptable
    """
    return ebs['Encrypted']

@pytest.mark.ec2
@pytest.mark.parametrize(
    'ec2_ebs_volume',
    ec2_ebs_volumes(),
    ids=lambda ebs: ebs['VolumeId'],
)
def test_ec2_ebs_volume_encrypted(ec2_ebs_volume):
    assert is_ebs_volume_encrypted(ec2_ebs_volume)
