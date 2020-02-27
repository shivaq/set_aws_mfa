#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from random import randint
from set_aws_mfa import set_aws_mfa
from set_aws_mfa.set_aws_mfa import ProfileTuple
from set_aws_mfa.set_aws_mfa import ProfileNumInput


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
    user_input = set_aws_mfa.ask_profile_num_input(ProfileNumInput(), perfect_profile_list)
    # THEN: the returned value is int
    assert type(user_input) is int


def test_get_sts_client(perfect_profile_list):

    # GIVEN: a ProfileTuple
    profile = perfect_profile_list[0]

    # WHEN: call the function
    sts_client = set_aws_mfa.get_sts_client(profile)

    # THEN:
    assert sts_client is not None


# TODO: テスト ~/.aws_accounts_for_set_aws_mfa が存在しない場合、作成を促すプロンプトを表示する

# TODO: テスト ~/.aws_accounts_for_set_aws_mfa はするが、該当ProfileのAWSアカウントIDが存在しない場合にユーザーに入力を求める

# TODO: テスト ユーザー入力の AWSアカウントIDを Validate する


# TODO: テスト ~/.aws_accounts_for_set_aws_mfa から該当ProfileのAWSアカウントIDを取得する
def test_get_aws_account_id_for_the_profile(perfect_profile_list):

    # GIVEN: a ProfileTuple
    profile = perfect_profile_list[0]

    # WHEN: call the function
    aws_account_id = set_aws_mfa.get_aws_account_id(profile)

    # THEN:
    assert type(aws_account_id) == int


# TODO: テスト該当プロファイルのMFA ARN を取得する
def test_get_mfa_arn(perfect_profile_list):

    # GIVEN: a ProfileTuple
    profile = perfect_profile_list[0]

    # WHEN: call the function
    mfa_arn = set_aws_mfa.get_mfa_arn(profile)

    # THEN:
    assert profile.name in mfa_arn


# TODO: 受け取ったトークンで認証を試みる
# TODO: テスト：認証に失敗した場合
# TODO: テスト：認証が成功したことを確認
# TODO: テスト：認証が成功したことを表示
# TODO: テスト：AWS 受け取ったトークンを環境変数に設定できる？
