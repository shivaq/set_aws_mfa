from set_aws_mfa import set_aws_mfa
import pytest

@pytest.fixture()
def profile_lists():
    return set_aws_mfa.get_profile_obj_list()


@pytest.fixture()
def credentials_lists():
    return set_aws_mfa.get_credentials_obj_list()


@pytest.fixture
def perfect_profile_list(profile_lists, credentials_lists):
    return set_aws_mfa.get_perfect_profile_list(
        profile_lists, credentials_lists)
