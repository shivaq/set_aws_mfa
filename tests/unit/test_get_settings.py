#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from set_aws_mfa import set_aws_mfa
from set_aws_mfa.set_aws_mfa import ProfileTuple
import pytest


@pytest.fixture
def set_fake_files():
    set_aws_mfa.AWS_ACCOUNT_FOR_SET_AWS_MFA = "~/.fake/aws_accounts_for_set_aws_mfa"
    yield
    set_aws_mfa.AWS_ACCOUNT_FOR_SET_AWS_MFA = "~/.aws_accounts_for_set_aws_mfa"


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


# TODO: テスト ~/.aws_accounts_for_set_aws_mfa が存在しない場合、作成を促すプロンプトを表示する
def test_no_aws_accounts_for_set_aws_mfa_prompts_permission_to_create_the_file(set_fake_files):
    # GIVEN: the path of AWS_ACCOUNT_FOR_SET_AWS_MFA replaced with fake path
    # WHEN: Check the existence of AWS_ACCOUNT_FOR_SET_AWS_MFA
    # THEN: Ask input to permit creating ~/.aws_accounts_for_set_aws_mfa
    assert "a" is "a"


# TODO: ~/.aws_accounts_for_set_aws_mfa の作成に成功する
def test_new_file_is_created_in_local_path():
    # GIVEN: Check the existence of AWS_ACCOUNT_FOR_SET_AWS_MFA is failed
    # WHEN: Create fake AWS_ACCOUNT_FOR_SET_AWS_MFA
    # THEN: fake AWS_ACCOUNT_FOR_SET_AWS_MFA existence is confirmed
    # THEN: remove fake AWS_ACCOUNT_FOR_SET_AWS_MFA with fixture
    assert "a" is "a"


# TODO: テスト ユーザー入力の AWSアカウントIDを Validate する
def test_user_input_is_int():
    # GIVEN: Create fake AWS_ACCOUNT_FOR_SET_AWS_MFA
    # GIVEN: No info for profile exists in fake AWS_ACCOUNT_FOR_SET_AWS_MFA
    # WHEN: check the existence of info for the given profile
    # THEN: Prompt message to ask for input aws account id for the profile
    assert "a" is "a"


# TODO: ~/.aws_accounts_for_set_aws_mfa に テスト ユーザー入力の AWSアカウントIDを 記入する
def test_writing_aws_account_to_the_file():
    # GIVEN: Create fake AWS_ACCOUNT_FOR_SET_AWS_MFA
    # GIVEN: No info for profile exists in fake AWS_ACCOUNT_FOR_SET_AWS_MFA
    # WHEN: check the existence of info for the given profile
    # THEN: Prompt message to ask for input aws account id for the profile
    assert "a" is "a"


# TODO: テスト ~/.aws_accounts_for_set_aws_mfa から該当ProfileのAWSアカウントIDを取得する
def test_get_aws_account_id_for_the_profile(perfect_profile_list):

    # GIVEN: a ProfileTuple
    profile = perfect_profile_list[0]

    # WHEN: call the function
    aws_account_id = set_aws_mfa.get_aws_account_id(profile)

    # THEN:
    assert type(aws_account_id) == int


# TODO: テスト ~/.aws_accounts_for_set_aws_mfa はするが、該当ProfileのAWSアカウントIDが存在しない場合にユーザーに入力を求める
def test_no_aws_account_id_for_given_profile_prompts_msg():
    # GIVEN: Create fake AWS_ACCOUNT_FOR_SET_AWS_MFA
    # GIVEN: No info for profile exists in fake AWS_ACCOUNT_FOR_SET_AWS_MFA
    # WHEN: check the existence of info for the given profile
    # THEN: Prompt message to ask for input aws account id for the profile
    assert "a" is "a"


# TODO: テスト該当プロファイルのMFA ARN を取得する
def test_get_mfa_arn(perfect_profile_list):

    # GIVEN: a ProfileTuple
    profile = perfect_profile_list[0]

    # WHEN: call the function
    mfa_arn = set_aws_mfa.get_mfa_arn(profile)

    # THEN:
    assert profile.name in mfa_arn