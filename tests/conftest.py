from set_aws_mfa import set_aws_mfa
import pytest
FAKE_AWS_ACCOUNT_FOR_SET_AWS_MFA = "~/fake_aws_accounts_for_set_aws_mfa"
CORRECT_AWS_ACCOUNT_FOR_SET_AWS_MFA = "~/.aws_accounts_for_set_aws_mfa"


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
##########################
# aws account id
##########################
@pytest.fixture
def set_fake_aws_account_files():
    set_aws_mfa.AWS_ACCOUNT_FOR_SET_AWS_MFA = FAKE_AWS_ACCOUNT_FOR_SET_AWS_MFA
    yield
    set_aws_mfa.AWS_ACCOUNT_FOR_SET_AWS_MFA = CORRECT_AWS_ACCOUNT_FOR_SET_AWS_MFA


@pytest.fixture()
def delete_fake_aws_account_files():
    yield
    helper.delete_a_file_if_it_exists(FAKE_AWS_ACCOUNT_FOR_SET_AWS_MFA)


@pytest.fixture()
def create_fake_aws_account_files():
    set_aws_mfa.create_aws_account_id_file()
