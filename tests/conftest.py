import pytest
import os
import configparser
from set_aws_mfa.helper import helper
from set_aws_mfa.data import data_manager
from set_aws_mfa import validate

FAKE_AWS_ACCOUNT_FOR_SET_AWS_MFA = "~/fake_aws_accounts_for_set_aws_mfa"
CORRECT_AWS_ACCOUNT_FOR_SET_AWS_MFA = "~/.aws_accounts_for_set_aws_mfa"

# Get ini config parser
Config = configparser.ConfigParser()
Config._interpolation = configparser.ExtendedInterpolation()


@pytest.fixture()
def profile_lists():
    return data_manager.get_profile_obj_list()


@pytest.fixture()
def credentials_lists():
    return data_manager.get_credentials_obj_list()


@pytest.fixture
def perfect_profile_list(profile_lists, credentials_lists):
    return data_manager.get_perfect_profile_list(
        profile_lists, credentials_lists)


@pytest.fixture()
def perfect_profile(perfect_profile_list):
    return perfect_profile_list[0]


##########################
# aws account id
##########################
@pytest.fixture
def set_fake_aws_account_files():
    validate.AWS_ACCOUNT_FOR_SET_AWS_MFA = FAKE_AWS_ACCOUNT_FOR_SET_AWS_MFA
    data_manager.AWS_ACCOUNT_FOR_SET_AWS_MFA = FAKE_AWS_ACCOUNT_FOR_SET_AWS_MFA
    yield
    validate.AWS_ACCOUNT_FOR_SET_AWS_MFA = CORRECT_AWS_ACCOUNT_FOR_SET_AWS_MFA
    data_manager.AWS_ACCOUNT_FOR_SET_AWS_MFA = CORRECT_AWS_ACCOUNT_FOR_SET_AWS_MFA


@pytest.fixture()
def delete_fake_aws_account_files():
    yield
    helper.delete_a_file_if_it_exists(FAKE_AWS_ACCOUNT_FOR_SET_AWS_MFA)


@pytest.fixture()
def create_fake_aws_account_files():
    data_manager.create_aws_account_id_file()


@pytest.fixture()
def valid_aws_account_id():
    abs_file_path = "~/.values_to_use_in_test"
    section = "set_aws_mfa"
    key = "aws_account_id_for_test"
    filename = os.path.expanduser(abs_file_path)
    with open(filename) as cfg:
        Config.clear()
        Config.read_file(cfg)
    return Config._sections.get(section).get(key)


@pytest.fixture()
def short_aws_account_id():
    return 33


@pytest.fixture()
def string_aws_account_id():
    return "aiueo"


@pytest.fixture()
def create_fake_valid_aws_account_id_setting(perfect_profile, valid_aws_account_id):
    abs_file_path = "~/.values_to_use_in_test"
    filename = os.path.expanduser(abs_file_path)
    with open(filename) as cfg:
        Config.clear()
        Config.read_file(cfg)

    data_manager.writing_aws_account_to_the_file(perfect_profile, valid_aws_account_id)
