#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from set_aws_mfa import prompts
from set_aws_mfa.data import data_manager
from tests.conftest import BUILTIN_INPUTS


def test_prompt_displays_selected_profile_and_asks_for_mfa_input(capsys, perfect_profile_list):
    # GIVEN: a perfect profile
    perfect_profile = perfect_profile_list[0]

    # WHEN: prompt for asking
    prompts.prompt_for_asking_mfa_code(perfect_profile)
    out, err = capsys.readouterr()

    assert perfect_profile.name in out.rstrip()


def test_get_mfa_token_with_wrong_length_mfa_code(perfect_profile, get_sts_client, get_valid_mfa_arn, capsys):

    # GIVEN: too short mfa code
    mfa_code = "33"
    # "WHEN: Ask for aws token
    data_manager.get_token_info(perfect_profile, get_sts_client, get_valid_mfa_arn, mfa_code)
    out, err = capsys.readouterr()
    # THEN: message is printed
    assert data_manager.MSG_TOO_SHORT_MFA_CODE == out.rstrip()

    # GIVEN: too long mfa code
    mfa_code = "33333333"
    # "WHEN: Ask for aws token
    data_manager.get_token_info(perfect_profile, get_sts_client, get_valid_mfa_arn, mfa_code)
    out, err = capsys.readouterr()
    # THEN: message is printed
    assert data_manager.MSG_TOO_LONG_MFA_CODE == out.rstrip()


def test_get_mfa_token_with_wrong_mfa_code(perfect_profile, get_sts_client, get_valid_mfa_arn, capsys, monkeypatch):

    # GIVEN: select profile modification
    # "reading from stdin while output is captured!" を回避するために、インプットを Mock
    selected_measure = 1
    # GIVEN: Mock user input string number
    monkeypatch.setattr(BUILTIN_INPUTS, lambda _: selected_measure)

    # GIVEN: Wrong mfa code
    mfa_code = "123456"
    # "WHEN: Ask for aws token
    data_manager.get_token_info(perfect_profile, get_sts_client, get_valid_mfa_arn, mfa_code)
    out, err = capsys.readouterr()
    # THEN: message is printed
    assert data_manager.MFA_FAILURE_MESSAGE.rstrip() in out.rstrip()


def test_prompt_to_select_role(capsys, profile_which_has_role, profile_obj_list):
    """ロールリストから、スイッチ対象のロールを促すプロンプトを表示する"""
    # Given: A selected profile
    # Given: A role for the profile
    role_list = data_manager.get_role_list_for_a_profile(profile_which_has_role, profile_obj_list)
    # When: call this
    prompts.prompt_role_selection(role_list)
    out, err = capsys.readouterr()

    assert prompts.MSG_DO_NOT_SWITCH in out.rstrip()
    assert role_list[0].name in out.rstrip()
