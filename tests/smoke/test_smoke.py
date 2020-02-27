#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from set_aws_mfa import set_aws_mfa
import unittest.mock as mock
import pytest


@pytest.fixture
def set_fake_files():
    set_aws_mfa.AWS_CONFIG = "~/.fake/fake"
    set_aws_mfa.AWS_CREDENTIALS = "~/.fake/fake"
    yield
    set_aws_mfa.AWS_CONFIG = "~/.aws/config"
    set_aws_mfa.AWS_CREDENTIALS = "~/.aws/credentials"


# 1. ~/.aws/config が存在していること
def test_aws_config_exists():

    # GIVEN: the path of target file
    config_file = set_aws_mfa.AWS_CONFIG
    # WHEN: get the path in local pc
    filename = os.path.expanduser(config_file)
    # THEN: the file exists
    assert os.path.exists(filename)


# 1. ~/.aws/credentials が存在していること
def test_aws_credentials_exists():

    # GIVEN: the path of target file
    config_file = set_aws_mfa.AWS_CREDENTIALS
    # WHEN: get the path in local pc
    filename = os.path.expanduser(config_file)
    # THEN: the file exists
    assert os.path.exists(filename)


# 1.  ~/.aws/config の内容を取得する
def test_get_aws_config_section_dict():
    """~/.aws/config の内容を取得できている"""

    # role_arn を取得
    config_dict = set_aws_mfa.get_aws_config_section_dict()
    assert len(config_dict) != 0


# 1. Profile クラスを取得できる
def test_get_aws_profile_object_list():
    """Profile クラスを取得できる"""
    profile_list = set_aws_mfa.get_profile_obj_list()

    if len(profile_list) != 0:
        for i in profile_list:
            assert isinstance(i, set_aws_mfa.ProfileTuple)


# 1.  ~/.aws/credentials の内容を取得する
def test_get_aws_credentials_section_dict():
    """~/.aws/credentials の内容を取得できている"""

    # role_arn を取得
    credentials_dict = set_aws_mfa.get_aws_credentials_section_dict()
    assert len(credentials_dict) != 0


# 1. Credentials クラスを取得できる
def test_get_aws_credentials_object_list():
    """Credentials クラスを取得できる"""
    credentials_list = set_aws_mfa.get_credentials_obj_list()

    if len(credentials_list) != 0:
        for i in credentials_list:
            assert isinstance(i, set_aws_mfa.CredentialTuple)


# 1. ~/.aws/config が存在していない場合、その旨標準出力されること
def test_no_aws_config_prompts_message(set_fake_files):

    # GIVEN: a fake path of target file
    # WHEN: Check if the file exists
    with pytest.raises(FileNotFoundError) as exeption_info:
        set_aws_mfa.check_aws_config_existence()

    # THEN: Raises FileNotFoundError
    exception_msg = exeption_info.value.args[0]
    assert exception_msg == set_aws_mfa.NO_AWS_CONFIG_ERROR


# 1. ~/.aws/credentials が存在していない場合、その旨標準出力されること
def test_no_aws_credentials_prompts_message(set_fake_files):

    # GIVEN: a fake path of target file
    # WHEN: Check if the file exists
    with pytest.raises(FileNotFoundError) as exception_info:
        set_aws_mfa.check_aws_credentials_existence()

    # THEN: Raises FileNotFoundError
    exception_msg = exception_info.value.args[0]
    assert exception_msg == set_aws_mfa.NO_AWS_CREDENTIALS_ERROR
