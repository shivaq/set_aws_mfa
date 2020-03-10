#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from random import randint
from set_aws_mfa import set_aws_mfa
from set_aws_mfa.set_aws_mfa import ProfileTuple
from set_aws_mfa.set_aws_mfa import IntObject


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




# TODO: 受け取ったトークンで認証を試みる
# TODO: テスト：認証に失敗した場合
# TODO: テスト：認証が成功したことを確認
# TODO: テスト：認証が成功したことを表示
# TODO: テスト：AWS 受け取ったトークンを環境変数に設定できる？
