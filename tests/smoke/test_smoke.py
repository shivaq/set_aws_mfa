#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from set_aws_mfa.helper import helper
import pytest
from set_aws_mfa.data.data_manager import ProfileTuple
from set_aws_mfa.data.data_manager import CredentialTuple
from set_aws_mfa.data import data_manager
from set_aws_mfa import validate


@pytest.fixture
def set_fake_files():
    validate.AWS_CONFIG = "~/.fake/fake"
    validate.AWS_CREDENTIALS = "~/.fake/fake"
    yield
    validate.AWS_CONFIG = "~/.aws/config"
    validate.AWS_CREDENTIALS = "~/.aws/credentials"


# 1. ~/.aws/config が存在していること
def test_aws_config_exists():
    # GIVEN: the path of target file
    # WHEN: get the path in local pc
    # THEN: the file exists
    assert helper.is_this_file_exists_in_local(data_manager.AWS_CONFIG)


# 1. ~/.aws/credentials が存在していること
def test_aws_credentials_exists():
    # GIVEN: the path of target file
    # WHEN: get the path in local pc
    # THEN: the file exists
    assert helper.is_this_file_exists_in_local(data_manager.AWS_CREDENTIALS)


# 1.  ~/.aws/config の内容を取得する
def test_get_aws_config_section_dict():
    """~/.aws/config の内容を取得できている"""

    # role_arn を取得
    config_dict = data_manager.get_aws_config_section_dict()
    assert len(config_dict) != 0


# 1. Profile クラスを取得できる
def test_get_aws_profile_object_list():
    """Profile クラスを取得できる"""
    profile_list = data_manager.get_profile_obj_list()

    if len(profile_list) != 0:
        for i in profile_list:
            assert isinstance(i, ProfileTuple)


# 1.  ~/.aws/credentials の内容を取得する
def test_get_aws_credentials_section_dict():
    """~/.aws/credentials の内容を取得できている"""

    # role_arn を取得
    credentials_dict = data_manager.get_aws_credentials_section_dict()
    assert len(credentials_dict) != 0


# 1. Credentials クラスを取得できる
def test_get_aws_credentials_object_list():
    """Credentials クラスを取得できる"""
    credentials_list = data_manager.get_credentials_obj_list()

    if len(credentials_list) != 0:
        for i in credentials_list:
            assert isinstance(i, CredentialTuple)


# 1. ~/.aws/config が存在していない場合、その旨標準出力されること
def test_no_aws_config_prompts_message(set_fake_files):
    # GIVEN: a fake path of target file
    # WHEN: Check if the file exists
    with pytest.raises(FileNotFoundError) as exception_info:
        validate.check_aws_config_existence()

    # THEN: Raises FileNotFoundError
    exception_msg = exception_info.value.args[0]
    assert exception_msg == validate.NO_AWS_CONFIG_ERROR


# 1. ~/.aws/credentials が存在していない場合、その旨標準出力されること
def test_no_aws_credentials_prompts_message(set_fake_files):
    # GIVEN: a fake path of target file
    # WHEN: Check if the file exists
    with pytest.raises(FileNotFoundError) as exception_info:
        validate.check_aws_credentials_existence()

    # THEN: Raises FileNotFoundError
    exception_msg = exception_info.value.args[0]
    assert exception_msg == validate.NO_AWS_CREDENTIALS_ERROR
