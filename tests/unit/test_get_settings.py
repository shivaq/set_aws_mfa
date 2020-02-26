#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from set_aws_mfa import set_aws_mfa
from set_aws_mfa.set_aws_mfa import ProfileTuple


# 1. role の profile を取得する
def test_role_profiles_item_is_profile_instance(profile_lists):
    # WHEN: role のリスト を取得
    role_profile_list = set_aws_mfa.get_role_profile(profile_lists)
    # THEN: role のリストのアイテムは ProfileTuple クラスのインスタンスである
    for i in role_profile_list:
        assert isinstance(i, ProfileTuple)
        assert i.role_arn is not None


# 1. config, credentials 両方にいる profile に、credentials の値を合体させたリストを取得する
def test_get_perfect_profile_list(profile_lists, credentials_lists, perfect_profile_list):
    # GIVEN: Profile に Credentials の値も合わせた ProfileTuple のリストを取得する
    profile_name_list = []
    credentials_name_list = []

    for i in profile_lists:
        # Given: ProfileTuple の name だけを抽出する
        profile_name_list.append(i.name)
    for k in credentials_lists:
        # GIVEN: CredentialsTuple の name だけを抽出する
        credentials_name_list.append(k.name)

    for in_both in perfect_profile_list:
        assert isinstance(in_both, ProfileTuple)
        # WHEN: ProfileTuple に aws_secret_access_key がセットされているならば
        if in_both.aws_secret_access_key is not None:
            # THEN: credentials にも config にも、その profile が存在している
            assert in_both.name in credentials_name_list
            assert in_both.name in profile_name_list


def test_prompt_displays_profile_name(capsys, perfect_profile_list):
    # GIVEN: get perfect_profile_list

    # WHEN: execute prompt_user_selection()
    set_aws_mfa.prompt_user_selection(perfect_profile_list)
    out, err = capsys.readouterr()

    # THEN: prompt usable profile name
    for p in perfect_profile_list:
        if p.aws_secret_access_key is not None:
            # ") profile_name" is included in stdout
            assert ") " + p.name in out.strip()
