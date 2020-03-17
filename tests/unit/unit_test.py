#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from random import randint
from set_aws_mfa import set_aws_mfa
from set_aws_mfa.set_aws_mfa import ProfileTuple
from set_aws_mfa.set_aws_mfa import IntObject
from botocore.exceptions import ClientError, ParamValidationError
import pytest

########################
# fixtures
########################
@pytest.fixture()
def get_valid_mfa_arn(monkeypatch, valid_aws_account_id, perfect_profile):

    def mock_get_aws_account_id(perfect_profile):
        return valid_aws_account_id

    monkeypatch.setattr(set_aws_mfa, "get_aws_account_id", mock_get_aws_account_id)
    return set_aws_mfa.get_mfa_arn(perfect_profile)


@pytest.fixture()
def get_short_mfa_arn(monkeypatch, short_aws_account_id, perfect_profile):

    def mock_get_aws_account_id(perfect_profile):
        return short_aws_account_id

    monkeypatch.setattr(set_aws_mfa, "get_aws_account_id", mock_get_aws_account_id)
    return set_aws_mfa.get_mfa_arn(perfect_profile)


@pytest.fixture()
def get_string_mfa_arn(monkeypatch, string_aws_account_id, perfect_profile):

    def mock_get_aws_account_id(perfect_profile):
        return string_aws_account_id

    monkeypatch.setattr(set_aws_mfa, "get_aws_account_id", mock_get_aws_account_id)
    return set_aws_mfa.get_mfa_arn(perfect_profile)


@pytest.fixture()
def get_sts_client(perfect_profile):
    return set_aws_mfa.get_sts_client(perfect_profile)


def test_classes_magic_methods():
    temp_name = "Suzuki"
    temp_region = "eu-central-1"
    temp_profile = ProfileTuple(temp_name, temp_region).__repr__()
    assert temp_name in temp_profile
    assert temp_region in temp_profile
    temp_cred = set_aws_mfa.CredentialTuple(temp_name).__repr__()
    assert temp_name in temp_cred
    temp_int = set_aws_mfa.IntObject(9).__repr__()
    assert "9" in temp_int


def test_get_profile_instance_for_user_input(perfect_profile_list):

    # GIVEN: validated input num
    validated_input = randint(1, len(perfect_profile_list))
    # WHEN: get profile instance for the input number
    profile_instance = set_aws_mfa.get_specified_profile(
        perfect_profile_list, validated_input)

    # THEN: 
    assert isinstance(profile_instance, ProfileTuple)


def test_prompt_displays_selected_profile_and_asks_for_mfa_input(capsys, perfect_profile_list):
    # GIVEN: a perfect profile
    perfect_profile = perfect_profile_list[0]

    # WHEN: prompt for asking
    set_aws_mfa.prompt_for_asking_mfa_code(perfect_profile)
    out, err = capsys.readouterr()

    assert perfect_profile.name in out.rstrip()


def test_return_user_input_num(monkeypatch, perfect_profile_list):

    # GIVEN: Mock user input string number
    monkeypatch.setattr('builtins.input', lambda _: "3")

    # WHEN: validate with this function
    user_input = set_aws_mfa.ask_profile_num_input_till_its_validated(IntObject(), perfect_profile_list)
    # THEN: the returned value is int
    assert type(user_input) is int


def test_get_mfa_code(perfect_profile_list, monkeypatch):

    # GIVEN: a profile
    profile = perfect_profile_list[0]
    # GIVEN: Mock user input string number
    monkeypatch.setattr('builtins.input', lambda _: "3334444")
    # WHEN: input mfa code
    mfa_code = set_aws_mfa.get_mfa_code(profile)
    # THEN: the returned value is an int
    assert type(mfa_code) is int


def test_get_sts_client(perfect_profile_list):

    # GIVEN: a ProfileTuple
    profile = perfect_profile_list[0]

    # WHEN: call the function
    sts_client = set_aws_mfa.get_sts_client(profile)

    # THEN:
    assert sts_client is not None


def test_get_mfa_token_with_wrong_length_mfa_code(get_sts_client, get_valid_mfa_arn, capsys):

    # GIVEN: too short mfa code
    mfa_code = "33"
    # "WHEN: Ask for aws token
    set_aws_mfa.get_token_info(get_sts_client, get_valid_mfa_arn, mfa_code)
    out, err = capsys.readouterr()
    # THEN: message is printed
    assert set_aws_mfa.MSG_TOO_SHORT_MFA_CODE == out.rstrip()

    # GIVEN: too long mfa code
    mfa_code = "33333333"
    # "WHEN: Ask for aws token
    set_aws_mfa.get_token_info(get_sts_client, get_valid_mfa_arn, mfa_code)
    out, err = capsys.readouterr()
    # THEN: message is printed
    assert set_aws_mfa.MSG_TOO_LONG_MFA_CODE == out.rstrip()


def test_get_mfa_token_with_wrong_mfa_code(get_sts_client, get_valid_mfa_arn, capsys, monkeypatch):

    # GIVEN: select profile modification
    # "reading from stdin while output is captured!" を回避するために、インプットを Mock
    selected_measure = 1
    # GIVEN: Mock user input string number
    monkeypatch.setattr('builtins.input', lambda _: selected_measure)

    # GIVEN: Wrong mfa code
    mfa_code = "123456"
    # "WHEN: Ask for aws token
    set_aws_mfa.get_token_info(get_sts_client, get_valid_mfa_arn, mfa_code)
    out, err = capsys.readouterr()
    # THEN: message is printed
    assert set_aws_mfa.MFA_FAILURE_MESSAGE.rstrip() == out.rstrip()


def test_input_wrong_mfa_code_and_re_enter_another_mfa_code(get_sts_client, get_valid_mfa_arn, monkeypatch, capsys):
    # GIVEN: select profile modification
    selected_measure = 1
    # GIVEN: Mock user input string number
    monkeypatch.setattr('builtins.input', lambda _: selected_measure)
    validated_selection = set_aws_mfa.ask_for_mfa_failure_inputs(IntObject())

    assert type(validated_selection) is int
