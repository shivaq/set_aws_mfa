#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
from logging.handlers import RotatingFileHandler
import os
import configparser
import collections
import boto3
from botocore.exceptions import ClientError, ParamValidationError
from set_aws_mfa import validate
from set_aws_mfa.helper import helper
from set_aws_mfa.helper.helper import IntObject
from set_aws_mfa import prompts
from set_aws_mfa.cli import cli
from set_aws_mfa.data.model import ProfileTuple
from set_aws_mfa.data.model import CredentialTuple


##################
# configure logging
##################
LOG_FILE_NAME = "set_aws_mfa.log"
logger = getLogger(__name__)
logger.setLevel(INFO)
# create console handler
ch = StreamHandler()
ch.setLevel(INFO)
# create file handler
rfh = RotatingFileHandler(
    LOG_FILE_NAME, maxBytes=10485760, backupCount=1)
rfh.setLevel(DEBUG)
# create formatter and add it to the handlers
formatter = Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rfh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(rfh)
logger.propagate = False

# File Path
AWS_CONFIG = "~/.aws/config"
AWS_ACCOUNT_FOR_SET_AWS_MFA = "~/.aws_accounts_for_set_aws_mfa"
AWS_CREDENTIALS = "~/.aws/credentials"
AWS_TMP_TOKEN = "~/.aws_tmp_token_for_set_mfa"
# AWS ACCOUNT ID
ASKING_AWS_ACCOUNT_ID_INPUT_MESSAGE = "Aws account Id : "
# MFA
ASKING_MFA_CODE_BEFORE = "MFA code for "
ASKING_MFA_CODE_AFTER = ": "
MSG_TOO_LONG_MFA_CODE = "MFA Code が長すぎます。"
MSG_TOO_SHORT_MFA_CODE = "MFA Code が短すぎます。"
# 認証失敗プロンプト
MFA_FAILURE_MESSAGE = "\nおっと.....!\n\n認証に失敗しました.\nユーザー名、AWS アカウント ID、MFA CODE のいずれかが" \
                      "間違っているかもしれません。\n修正対象を選んでください\n\n1) ユーザー名\n2) AWS アカウント ID\n3) MFA コード\n4) 修正せずに終了する\n\n"
MSG_EDIT_AWS_FILES = "~/.aws/config, ~/.aws/credentials に有効な profile を記載し、" + AWS_ACCOUNT_FOR_SET_AWS_MFA + \
                     "の profile も更新してください"
# ARN の部品
AWS_IAM_ARN_HEAD_PART = "arn:aws:iam::"
AWS_IAM_ARN_MFA_PART = ":mfa/"

#################################
# config parser operation
################################
# Get ini config parser
Config = configparser.ConfigParser()
Config._interpolation = configparser.ExtendedInterpolation()


#################################
# Create
################################
def create_aws_account_id_file():
    """
    Create ~/.aws_accounts_for_set_aws_mfa if it is not exists
    """
    helper.create_a_file_in_local(AWS_ACCOUNT_FOR_SET_AWS_MFA)


def create_a_file_to_set_env_var(token_info: dict, profile: ProfileTuple, role_profile: ProfileTuple):
    filename = os.path.expanduser(AWS_TMP_TOKEN)
    profile_to_set = profile
    if profile != role_profile:
        profile_to_set = role_profile
    with open(filename, "w") as tk:
        # 下記環境変数が設定されていると、AWS_PROFILE が機能しないため、コメントアウト
        # tk.write("export AWS_ACCESS_KEY_ID=" + token_info['Credentials']['AccessKeyId'] + "\n")
        # tk.write("export AWS_SECRET_ACCESS_KEY=" + token_info['Credentials']['SecretAccessKey'] + "\n")
        tk.write("export AWS_SESSION_TOKEN=" + token_info['Credentials']['SessionToken'] + "\n")
        tk.write("export AWS_ROLE_SESSION_NAME=" + profile.name + "\n")
        tk.write("export AWS_SDK_LOAD_CONFIG=true\n")
        tk.write("export AWS_DEFAULT_REGION=" + profile.region + "\n")
        tk.write("export AWS_PROFILE=" + profile_to_set.name + "\n")


#################################
# Read
################################
def prepare_to_read_local_ini_file(abs_file_path):
    """
    Read an ini file to read data from it with configparser
    """
    filename = os.path.expanduser(abs_file_path)
    with open(filename) as cfg:
        Config.clear()
        # 該当 ini ファイルを Config に読み込む
        Config.read_file(cfg)


def prepare_aws_account_id_file():
    """
    ~/.aws_accounts_for_set_aws_mfa の存在を確認し、なければ作成する
    """
    if not validate.check_aws_accounts_for_set_aws_mfa_existence():
        create_aws_account_id_file()
    prepare_to_read_local_ini_file(AWS_ACCOUNT_FOR_SET_AWS_MFA)


def get_aws_config_section_dict() -> collections.OrderedDict:
    """~/.aws/config から Section 情報を取得する"""
    prepare_to_read_local_ini_file(AWS_CONFIG)
    # 該当 ini ファイルのセクション dictionary を取得
    return Config._sections


def get_aws_credentials_section_dict() -> collections.OrderedDict:
    """~/.aws/credentials から Section 情報を取得する"""
    prepare_to_read_local_ini_file(AWS_CREDENTIALS)
    # 該当 ini ファイルのセクション dictionary を取得
    return Config._sections


def get_profile_obj_list() -> list:
    """ProfileTuple オブジェクトのリストを生成する"""
    profile_list = []
    profile_str = "profile"

    for section_key, section_value in get_aws_config_section_dict().items():
        # デフォルト値を設定
        region = ""
        role_arn = None
        source_profile = None
        is_default = False

        # ~/.aws/config のセクション名が profile から始まっていたら
        if section_key.startswith(profile_str):
            name = section_key[len(profile_str):].lstrip().rstrip()
        # セクション名が default だったら
        elif section_key == "default":
            name = "default"
            is_default = True
        # それ以外のセクション名は想定していないので、出力させる
        else:
            name = "unknown"
            print("unknown key" + section_key)

        # Get other attributes for a profile
        for key, value in section_value.items():
            if key == "region":
                region = value
            elif key == "role_arn":
                role_arn = value
            elif key == "source_profile":
                source_profile = value
            elif key == "output":
                output = value
            # それ以外のセクション名は想定していないので、出力させる
            else:
                print("unknown_key: " + key)
                print("value: " + value)
        profile_list.append(ProfileTuple(name, region, role_arn, source_profile, is_default))

    return profile_list


def get_credentials_obj_list() -> list:
    """CredentialTuple オブジェクトのリストを生成する"""
    credentials_list = []

    for profile, values in get_aws_credentials_section_dict().items():
        credential = CredentialTuple(profile)
        for key, value in values.items():
            if key == "aws_access_key_id":
                credential = credential._replace(aws_access_key_id=value)
            elif key == "aws_secret_access_key":
                credential = credential._replace(aws_secret_access_key=value)
        credentials_list.append(credential)
    return credentials_list


def get_perfect_profile_list(profile_list, credentials_list) -> list:
    """ IAM ユーザーと Credentials の情報を合わせた ProfileTuple のリストを取得 """

    perfect_profile_list = []
    for n, p in enumerate(profile_list):
        for c in credentials_list:
            # profile の name と一致する credential の name があった場合
            if p.name == c.name:
                # credentials のキーを、ProfileTuple の属性に割り当てて、更新する
                p = p._replace(aws_access_key_id=c.aws_access_key_id,
                               aws_secret_access_key=c.aws_secret_access_key)
                perfect_profile_list.append(p)
    return perfect_profile_list


def get_role_list_for_a_profile(profile: ProfileTuple, profile_obj_list: list):
    """該当プロフィールと紐づくロールを返す"""
    role_for_the_profile_list = []
    for profile_obj in profile_obj_list:
        if profile_obj.source_profile == profile.name:
            role_for_the_profile_list.append(profile_obj)
    return role_for_the_profile_list


def get_specified_profile(perfect_profile_list: list, validated_input: int) -> ProfileTuple:
    """int に応じた profile を取得"""
    return perfect_profile_list[validated_input - 1]


def get_selected_profile():
    profile_list = get_profile_obj_list()
    perfect_profile_list = get_perfect_profile_list(profile_list, get_credentials_obj_list())
    validated_input = validate.ask_profile_num_input_till_its_validated(IntObject(), perfect_profile_list)
    return get_specified_profile(perfect_profile_list, validated_input)


def get_aws_account_id_file_section_dict() -> collections.OrderedDict:
    """~/.aws_accounts_for_set_aws_mfa から Section 情報を取得する"""
    # ~/.aws_accounts_for_set_aws_mfa の有無を確認し、なければ生成する
    prepare_aws_account_id_file()
    # 該当 ini ファイルのセクション dictionary を取得
    return Config._sections


def get_aws_account_id(perfect_profile: ProfileTuple) -> int:
    """該当 profile の AWS account id を取得する"""
    account_id_section_dict = get_aws_account_id_file_section_dict()
    aws_account_id = 0
    # 該当ファイルのセクションに、該当 profile が存在している場合
    if perfect_profile.name in account_id_section_dict.keys():
        for profile, values in account_id_section_dict.items():
            if profile == perfect_profile.name:
                # 該当profile の aws_account_id の値を取得する
                aws_account_id = values.get("aws_account_id")
    else:  # 該当ファイルのセクションに、該当 profile が存在しない場合
        # aws account id の入力を要求し、
        prompts.prompt_for_asking_aws_account_id(perfect_profile)
        aws_account_id = helper.ask_int_input_till_its_validated(IntObject(), ASKING_AWS_ACCOUNT_ID_INPUT_MESSAGE)
        # 該当ファイルに書き込む
        writing_aws_account_to_the_file(perfect_profile, aws_account_id)
        # 再帰的に本関数を呼び出して、書き込み済みの aws account id を取得する
        get_aws_account_id(perfect_profile)

    return int(aws_account_id)


def get_mfa_code(perfect_profile: ProfileTuple):

    prompts.prompt_for_asking_mfa_code(perfect_profile)
    return helper.ask_int_input_till_its_validated(
        IntObject(), ASKING_MFA_CODE_BEFORE + perfect_profile.name + ASKING_MFA_CODE_AFTER
    )


def get_sts_client(perfect_profile: ProfileTuple) -> boto3.session.Session:
    """sts の client を取得する"""
    session = None
    try:
        session = boto3.session.Session(profile_name=perfect_profile.name)
    except ClientError:
        logger.exception("Failed to get session.")

    return session.client('sts')


def get_token_info(selected_profile: ProfileTuple, sts_client: boto3.session.Session, mfa_arn: str, mfa_code: str):
    """session token を取得する"""
    token_info = None
    try:
        token_info = sts_client.get_session_token(
            DurationSeconds=43200,  # 12 hours
            SerialNumber=mfa_arn,
            TokenCode=mfa_code
        )
    except ClientError as e:
        if "less than or equal to 6" in str(e):
            print(MSG_TOO_LONG_MFA_CODE)
            cli.access_aws_with_mfa_code(selected_profile)

        elif "MultiFactorAuthentication" in str(e):
            selected_measure = validate.ask_for_mfa_failure_inputs(IntObject())
            switcher = {
                1: lambda: print(MSG_EDIT_AWS_FILES),  # update profile
                2: lambda: cli.access_aws_after_reset_aws_account_id(selected_profile),  # update aws account id
                3: lambda: cli.access_aws_with_mfa_code(selected_profile),  # update mfa code
                4: lambda: exit(1)
            }
            return switcher[int(selected_measure)]()

    except ParamValidationError as e:
        if "Invalid length" in str(e):
            print(MSG_TOO_SHORT_MFA_CODE)
            cli.access_aws_with_mfa_code(selected_profile)

    return token_info


def get_mfa_arn(perfect_profile: ProfileTuple) -> str:
    """mfa arn を返す"""

    return AWS_IAM_ARN_HEAD_PART + str(
        get_aws_account_id(perfect_profile)) + AWS_IAM_ARN_MFA_PART + perfect_profile.name


def switch_actions_for_role(profile, selected_num: int, role_for_the_profile_list):
    """ユーザー入力に応じた、ロール関連のアクションを実行する"""
    if selected_num == 0:
        return profile
    elif selected_num == 1:
        # 追加登録するロール名を取得
        new_role_name = helper.get_input("ロールの名前 :")
        # ロールを新規登録
        writing_new_role_to_aws_config(profile, new_role_name)
        switch_actions_again(profile)
    elif selected_num == 2:
        prompts.prompt_roles_to_delete(role_for_the_profile_list)
        selected_num = int(validate.validate_input_for_delete_role(role_for_the_profile_list))
        delete_role_from_settings(role_for_the_profile_list[selected_num - 1])
        switch_actions_again(profile)
    else:
        return role_for_the_profile_list[selected_num - 3]


def get_role_action(profile, role_for_the_profile_list) -> int:
    """スイッチロール関連のアクションと紐づく番号を取得する"""
    prompts.prompt_msg_for_the_profile_roles(profile, role_for_the_profile_list)
    return validate.validate_input_actions_for_role(role_for_the_profile_list)


def switch_actions_again(profile: ProfileTuple):
    # 新規 Profile リスト、ロールリストを取得
    profile_obj_list = get_profile_obj_list()
    new_role_list = get_role_list_for_a_profile(profile, profile_obj_list)
    # 再度ロールのアクションを選択
    role_action_num = int(get_role_action(profile, new_role_list))
    # 再帰的に switch_actions_for_role() を呼び出す
    switch_actions_for_role(profile, role_action_num, new_role_list)


#################################
# Update
################################
def update_config_parser(file_path: str, section: str, key: str, value):
    prepare_to_read_local_ini_file(file_path)

    # 当該セクションがなければ作成する
    if not Config.has_section(section):
        Config.add_section(section)

    Config.set(section, key, value)

    filename = os.path.expanduser(file_path)
    # ConfigParser への変更を実ファイルに反映する
    with open(filename, "w") as configfile:
        Config.write(configfile)


def writing_aws_account_to_the_file(profile: ProfileTuple, aws_account_id):
    """該当 profile の aws account id を AWS_ACCOUNT_FOR_SET_AWS_MFA に書き込む"""
    aws_account_id = str(aws_account_id)
    update_config_parser(AWS_ACCOUNT_FOR_SET_AWS_MFA, profile.name, "aws_account_id", aws_account_id)


def reset_aws_account_id(perfect_profile: ProfileTuple):
    # aws account id の入力を要求し、
    prompts.prompt_for_update_aws_account_id(perfect_profile)
    aws_account_id = helper.ask_int_input_till_its_validated(IntObject(), ASKING_AWS_ACCOUNT_ID_INPUT_MESSAGE)
    # 該当ファイルに書き込む
    writing_aws_account_to_the_file(perfect_profile, aws_account_id)
    # 再帰的に本関数を呼び出して、書き込み済みの aws account id を取得する
    get_aws_account_id(perfect_profile)


def writing_new_role_to_aws_config(profile: ProfileTuple, new_role_name: str):
    """新規ロールを ~/.aws/config に登録する"""

    section = "profile " + new_role_name
    aws_account_id = str(get_aws_account_id(profile))
    role_arn = "arn:aws:iam::" + aws_account_id + ":role/" + new_role_name

    update_config_parser(AWS_CONFIG, section, "region", profile.region)
    update_config_parser(AWS_CONFIG, section, "role_arn", role_arn)
    update_config_parser(AWS_CONFIG, section, "source_profile", profile.name)


#################################
# Delete
################################
def delete_section(file_path: str, section: str):
    """指定したセクションを削除する"""
    prepare_to_read_local_ini_file(file_path)

    # 当該セクションがなければ作成する
    if not Config.has_section(section):
        Config.add_section(section)

    Config.remove_section(section)

    filename = os.path.expanduser(file_path)
    # ConfigParser への変更を実ファイルに反映する
    with open(filename, "w") as configfile:
        Config.write(configfile)


def delete_role_from_settings(role_profile: ProfileTuple):
    """設定ファイルから当該ロールを削除する"""
    section = "profile " + role_profile.name

    delete_section(AWS_CONFIG, section)
