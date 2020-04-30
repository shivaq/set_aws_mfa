#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tests.conftest import BUILTIN_INPUTS
from set_aws_mfa.data import data_manager
from set_aws_mfa import validate


def test_switch_role(monkeypatch, profile_which_has_role):
    """ユーザーインプットから、MFA Arn を取得するまでの流れをテスト
    以降の処理は、テンポラリーなコード入力が必要なため、テストを断念
    """
    validate.check_aws_config_existence()
    validate.check_aws_credentials_existence()

    # GIVEN: profile object list
    profile_obj_list = data_manager.get_profile_obj_list()

    # GIVEN: position of a profile which can be switched to a role
    position_in_list = [i for i, x in enumerate(profile_obj_list) if x == profile_which_has_role]

    # GIVEN: Mock input to select a profile which can be switched to a role
    user_input = position_in_list[0] + 1
    monkeypatch.setattr(BUILTIN_INPUTS, lambda _: user_input)
    selected_profile = data_manager.get_selected_profile()
    mfa_arn = data_manager.get_mfa_arn(selected_profile)
    assert profile_which_has_role.name in mfa_arn

