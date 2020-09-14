import pytest

from helpers import get_param_id

from gsuite.admin.resources import list_groups_and_members
from gsuite.admin.helpers import owners_of_a_group


@pytest.fixture
def min_number_of_owners(pytestconfig):
    return pytestconfig.custom_config.gsuite.min_number_of_owners


@pytest.mark.gsuite_admin
@pytest.mark.parametrize(
    "group", list_groups_and_members(), ids=lambda g: get_param_id(g, "email"),
)
def test_groups_have_enough_owners(group, min_number_of_owners):
    assert len(owners_of_a_group(group["members"])) >= min_number_of_owners
