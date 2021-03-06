#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from set_aws_mfa import prompts
from set_aws_mfa.data import data_manager
from tests.conftest import BUILTIN_INPUTS
from set_aws_mfa.data.data_manager import ProfileTuple


def test_prompt_displays_selected_profile_and_asks_for_mfa_input(capsys, perfect_profile_list):
    # GIVEN: a perfect profile
    perfect_profile = perfect_profile_list[0]

    # WHEN: prompt for asking
    prompts.prompt_for_asking_mfa_code(perfect_profile)
    out, err = capsys.readouterr()

    assert perfect_profile.name in out.rstrip()


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


def test_prompt_msg_for_no_role_profile(capsys):
    """テスト: ロールリストの要素数が ゼロ だったときのメッセージ表示"""
    # GIVEN: 0 length list
    zero_list_for_roles = []

    # WHEN: Check the list
    prompts.prompt_msg_for_the_profile_roles(ProfileTuple("Nobunaga", "Owari"), zero_list_for_roles)
    out, err = capsys.readouterr()
    assert prompts.MSG_SUGGEST_REGISTER_ROLE in out.rstrip()


def test_prompt_msg_for_with_role_profile(capsys, profile_which_has_role, profile_obj_list):
    """テスト: 選択したプロファイルにスイッチ可能なロールがあるときのメッセージ表示"""
    # GIVEN: list for roles for a profile
    role_list = data_manager.get_role_list_for_a_profile(profile_which_has_role, profile_obj_list)
    # WHEN: Check the list
    prompts.prompt_msg_for_the_profile_roles(profile_which_has_role, role_list)
    out, err = capsys.readouterr()
    # THEN: prompt message to select a role
    assert prompts.MSG_SUGGEST_SELECT_ROLE in out.rstrip()