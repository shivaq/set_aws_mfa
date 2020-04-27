import pytest
import os
import configparser
from set_aws_mfa.helper import helper
from set_aws_mfa.data import data_manager
from set_aws_mfa import validate

FAKE_AWS_ACCOUNT_FOR_SET_AWS_MFA = "~/fake_aws_accounts_for_set_aws_mfa"
CORRECT_AWS_ACCOUNT_FOR_SET_AWS_MFA = "~/.aws_accounts_for_set_aws_mfa"
BUILTIN_INPUTS = 'builtins.input'

# Get ini config parser
Config = configparser.ConfigParser()
Config._interpolation = configparser.ExtendedInterpolation()


@pytest.fixture()
def profile_obj_list():
    return data_manager.get_profile_obj_list()


@pytest.fixture()
def credentials_lists():
    return data_manager.get_credentials_obj_list()


@pytest.fixture
def perfect_profile_list(profile_obj_list, credentials_lists):
    return data_manager.get_perfect_profile_list(
        profile_obj_list, credentials_lists)


@pytest.fixture()
def perfect_profile(perfect_profile_list):
    return perfect_profile_list[0]


@pytest.fixture()
def profile_which_has_role(profile_obj_list):
    """スイッチできるロールがある プロファイルを返す"""
    role_list_for_a_profile = []
    for profile in profile_obj_list:
        role_list_for_a_profile = data_manager.get_role_list_for_a_profile(profile, profile_obj_list)
        if len(role_list_for_a_profile) != 0:
            return profile


@pytest.fixture()
def role_for_the_profile_list(profile_which_has_role, profile_obj_list):
    """IAMユーザーと紐付いたロールのリストを返す"""
    return data_manager.get_role_list_for_a_profile(profile_which_has_role, profile_obj_list)


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


@pytest.fixture()
def get_sts_client(perfect_profile):
    return data_manager.get_sts_client(perfect_profile)


@pytest.fixture()
def get_valid_mfa_arn(monkeypatch, valid_aws_account_id, perfect_profile):

    # Mock does not use profile, but original function need it.
    def mock_get_aws_account_id(perfect_profile):
        return valid_aws_account_id

    monkeypatch.setattr(data_manager, "get_aws_account_id", mock_get_aws_account_id)
    return data_manager.get_mfa_arn(perfect_profile)
