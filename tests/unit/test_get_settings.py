#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from set_aws_mfa import set_aws_mfa
from set_aws_mfa.set_aws_mfa import ProfileTuple
import pytest
import os
from helper import helper
from set_aws_mfa.set_aws_mfa import IntObject

FAKE_AWS_ACCOUNT_FOR_SET_AWS_MFA = "~/fake_aws_accounts_for_set_aws_mfa"
CORRECT_AWS_ACCOUNT_FOR_SET_AWS_MFA = "~/.aws_accounts_for_set_aws_mfa"

########################
# fixtures
########################
@pytest.fixture
def set_fake_aws_account_files():
    set_aws_mfa.AWS_ACCOUNT_FOR_SET_AWS_MFA = FAKE_AWS_ACCOUNT_FOR_SET_AWS_MFA
    yield
    set_aws_mfa.AWS_ACCOUNT_FOR_SET_AWS_MFA = CORRECT_AWS_ACCOUNT_FOR_SET_AWS_MFA


@pytest.fixture()
def delete_fake_aws_account_files():
    yield
    helper.delete_a_file_if_it_exists(FAKE_AWS_ACCOUNT_FOR_SET_AWS_MFA)


@pytest.fixture()
def create_fake_aws_account_files():
    set_aws_mfa.create_aws_account_id_file()


########################
# Get profiles
########################
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


########################
# Get aws account info
########################
# テスト ~/.aws_accounts_for_set_aws_mfa が存在しない場合、False を返す
def test_no_aws_accounts_for_set_aws_mfa_returns_false(set_fake_aws_account_files):
    # GIVEN: the path of AWS_ACCOUNT_FOR_SET_AWS_MFA replaced with fake path
    # WHEN: Check the existence of AWS_ACCOUNT_FOR_SET_AWS_MFA
    is_the_file_exists = set_aws_mfa.check_aws_accounts_for_set_aws_mfa_existence()

    # THEN: The file is not exist
    assert not is_the_file_exists


# テスト ~/.aws_accounts_for_set_aws_mfa が存在しない場合、作成する
def test_create_aws_accounts_for_set_aws_mfa(set_fake_aws_account_files, delete_fake_aws_account_files):
    # GIVEN: the path of AWS_ACCOUNT_FOR_SET_AWS_MFA replaced with fake path
    # WHEN: Try to create AWS_ACCOUNT_FOR_SET_AWS_MFA
    set_aws_mfa.create_aws_account_id_file()

    # WHEN: Check the existence of AWS_ACCOUNT_FOR_SET_AWS_MFA
    is_the_file_exists = set_aws_mfa.check_aws_accounts_for_set_aws_mfa_existence()

    # THEN: The file is exist
    assert is_the_file_exists


# テスト ~/.aws_accounts_for_set_aws_mfa 作成後、ユーザーに 該当ProfileのAWSアカウントID の入力を求める
def test_when_no_aws_account_file_asks_for_user_input(set_fake_aws_account_files, delete_fake_aws_account_files,
                                                     perfect_profile_list, capsys):
    # GIVEN a Profile
    profile = perfect_profile_list[0]
    # WHEN create a new aws account file
    if not set_aws_mfa.check_aws_accounts_for_set_aws_mfa_existence():
        set_aws_mfa.create_aws_account_id_file()
    else:
        # そのファイルが既に存在していた場合、書き込みをせずに raise
        raise
    # THEN: ask to input aws account id for the profile
    set_aws_mfa.prompt_for_asking_aws_account_id(profile)
    out, err = capsys.readouterr()

    assert profile.name in out.rstrip()
    assert set_aws_mfa.PROMPT_ASK_AWS_ACCOUNT_ID_FOR_PROFILE_BEFORE in out.rstrip()
    assert set_aws_mfa.PROMPT_ASK_AWS_ACCOUNT_ID_FOR_PROFILE_AFTER in out.rstrip()


# ~/.aws_accounts_for_set_aws_mfa から該当ProfileのAWSアカウントIDを取得する
def test_get_aws_account_id_for_the_profile(perfect_profile_list):

    # GIVEN: a ProfileTuple
    profile = perfect_profile_list[0]

    # WHEN: call the function
    aws_account_id = set_aws_mfa.get_aws_account_id(profile)

    # THEN:
    assert type(aws_account_id) == int


# テスト ユーザー入力の AWSアカウントID が int じゃない場合、False が返される
def test_user_input_is_not_int(monkeypatch):
    # GIVEN: ユーザーインプットが integer ではない場合、を Mock
    user_input_not_int = "hogehoge"
    # GIVEN: Mock user input string
    monkeypatch.setattr('builtins.input', lambda _: user_input_not_int)
    # WHEN: Validate the input
    is_int = helper.is_input_int_loop(IntObject(), set_aws_mfa.ASKING_AWS_ACCOUNT_ID_INPUT_MESSAGE)
    # THEN: It's not an int
    assert not is_int


# テスト ユーザー入力の AWSアカウントID が int の場合、True が返される
def test_user_input_is_int(monkeypatch):
    # GIVEN: ユーザーインプットが integer ではない場合、を Mock
    user_input_not_int = "12345"
    # GIVEN: Mock user input string
    monkeypatch.setattr('builtins.input', lambda _: user_input_not_int)
    # WHEN: Validate the input
    is_int = helper.is_input_int_loop(IntObject(), set_aws_mfa.ASKING_AWS_ACCOUNT_ID_INPUT_MESSAGE)
    # THEN: It's not an int
    assert is_int


# ~/.aws_accounts_for_set_aws_mfa に ユーザー入力の AWSアカウントIDを 記入する
def test_writing_aws_account_to_the_file(set_fake_aws_account_files, delete_fake_aws_account_files, perfect_profile_list):
    # GIVEN: AWS_ACCOUNT_FOR_SET_AWS_MFA is changed to fake path
    # GIVEN: Create fake AWS_ACCOUNT_FOR_SET_AWS_MFA
    set_aws_mfa.create_aws_account_id_file()
    # GIVEN: 対象 profile を指定する
    profile = perfect_profile_list[0]
    # GIVEN: 下記aws account id を取得したとする
    aws_account_id = 12345
    set_aws_mfa.create_aws_account_id_file()
    # WHEN: check the existence of info for the given profile
    set_aws_mfa.writing_aws_account_to_the_file(profile, aws_account_id)
    # WHEN: AWS_ACCOUNT_FOR_SET_AWS_MFA から該当 profile の aws account id を検索した場合
    retrieved_aws_account_id = set_aws_mfa.get_aws_account_id(profile)
    # THEN: int の aws account id が取得できている
    assert type(retrieved_aws_account_id) is int


# テスト ~/.aws_accounts_for_set_aws_mfa はするが、該当ProfileのAWSアカウントIDが存在しない場合にユーザーに入力を求める
def test_no_aws_account_id_for_given_profile_prompts_msg(set_fake_aws_account_files,
                                                         perfect_profile_list, create_fake_aws_account_files,
                                                         delete_fake_aws_account_files,
                                                         capsys, monkeypatch):
    # GIVEN: Create fake AWS_ACCOUNT_FOR_SET_AWS_MFA
    # GIVEN: No info for profile exists in fake AWS_ACCOUNT_FOR_SET_AWS_MFA
    # GIVEN: 対象 profile を指定する
    profile = perfect_profile_list[0]
    # GIVEN: ユーザーインプットが integer ではない場合、を Mock
    aws_account_id_int = "12345"
    # GIVEN: Mock user input string
    monkeypatch.setattr('builtins.input', lambda _: aws_account_id_int)

    # WHEN: check the existence of info for the given profile
    set_aws_mfa.get_aws_account_id(profile)
    # THEN: Prompt message to ask for input aws account id for the profile
    out, err = capsys.readouterr()

    print(out.rstrip())

    assert profile.name in out.rstrip()
    assert set_aws_mfa.PROMPT_ASK_AWS_ACCOUNT_ID_FOR_PROFILE_BEFORE in out.rstrip()
    assert set_aws_mfa.PROMPT_ASK_AWS_ACCOUNT_ID_FOR_PROFILE_AFTER in out.rstrip()


# テスト該当プロファイルのMFA ARN を取得する
def test_get_mfa_arn(perfect_profile_list):

    # GIVEN: a ProfileTuple
    profile = perfect_profile_list[0]

    # WHEN: call the function
    mfa_arn = set_aws_mfa.get_mfa_arn(profile)

    # THEN:
    assert set_aws_mfa.AWS_IAM_ARN_HEAD_PART
    assert set_aws_mfa.AWS_IAM_ARN_MFA_PART
    assert profile.name in mfa_arn
