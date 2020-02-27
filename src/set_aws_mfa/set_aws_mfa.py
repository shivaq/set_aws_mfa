#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG, INFO
from logging.handlers import RotatingFileHandler
import collections
import os
import configparser
from typing import NamedTuple
import boto3

LOG_FILE_NAME = "set_aws_mfa.log"

##################
# configure logging
##################
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


##################
# Constants
##################
AWS_CONFIG = "~/.aws/config"
NO_AWS_CONFIG_ERROR = "There is no '~/.aws/config'. You need to set with `aws configure` command."
AWS_CREDENTIALS = "~/.aws/credentials"
NO_AWS_CREDENTIALS_ERROR = "There is no '~/.aws/credentials'. You need to set with `aws configure` command."
MSG_ASK_SELECT_PROFILE = "Input a number for an aws login user."
ASKING_USER_INPUT_MESSAGE = "Profile No. : "
PROMPT_USER_INPUT_BEFORE = "\nあなたが入力したのは"
PROMPT_USER_INPUT_AFTER = "です"
PROMPT_ENTER_AN_INT = "数値を入力してください"
PROMPT_NOT_AN_VALID_INT_BEFORE = "0から"
PROMPT_NOT_AN_VALID_INT_AFTER = "の数値を入力してください"
PROMPT_ASK_MFA_TOKEN_FOR_PROFILE_BEFORE = "\n"
PROMPT_ASK_MFA_TOKEN_FOR_PROFILE_AFTER = " 用のMFAトークンを入力してください。"

# Get ini config parser
Config = configparser.ConfigParser()
Config._interpolation = configparser.ExtendedInterpolation()


class ProfileTuple(NamedTuple):
    name: str
    region: str
    role_arn: str = None
    source_profile: str = None
    is_default: bool = False
    aws_access_key_id: str = None
    aws_secret_access_key: str = None

    def __repr__(self) -> str:

        return (f'{self.__class__.__name__}('
                f'{self.name!r}, {self.region!r}, {self.role_arn!r}, {self.source_profile!r}, {self.is_default!r}, {self.aws_access_key_id!r}, {self.aws_secret_access_key!r})')


class CredentialTuple(NamedTuple):
    name: str
    aws_access_key_id: str = None
    aws_secret_access_key: str = None

    def __repr__(self) -> str:

        return (f'{self.__class__.__name__}('
                f'{self.name!r}, {self.aws_access_key_id!r}, {self.aws_secret_access_key!r})')


class ProfileNumInput:
    def __init__(self, prompt_num: int = 0):
        self.prompt_num = prompt_num

    def __repr__(self) -> str:

        return (f'{self.__class__.__name__}('
                f'{self.prompt_num!r})')

#################################
# Retrieve Settings
################################


def is_this_file_exists_in_local(local_file_path: str) -> bool:
    """ローカルファイルが存在しているか否かを返す"""
    filename = os.path.expanduser(local_file_path)
    return os.path.exists(filename)


def check_aws_config_existence():
    """
    Check if ~/.aws/config exists
    """
    if not is_this_file_exists_in_local(AWS_CONFIG):
        raise FileNotFoundError(NO_AWS_CONFIG_ERROR)


def check_aws_credentials_existence():
    """
    Check if ~/.aws/credentials exists
    """
    if not is_this_file_exists_in_local(AWS_CREDENTIALS):
        raise FileNotFoundError(NO_AWS_CREDENTIALS_ERROR)


def prepare_aws_config():
    """~/.aws/config を読み込む"""
    config_file = AWS_CONFIG
    filename = os.path.expanduser(config_file)
    with open(filename) as cfg:
        Config.clear()
        # 該当 ini ファイルを Config に読み込む
        Config.read_file(cfg)


def get_aws_config_section_dict() -> collections.OrderedDict:
    """~/.aws/config から Section 情報を取得する"""
    prepare_aws_config()
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


def prepare_aws_credentials():
    """~/.aws/credentials を読み込む"""
    config_file = AWS_CREDENTIALS
    filename = os.path.expanduser(config_file)
    with open(filename) as cfg:
        Config.clear()
        # 該当 ini ファイルを Config に読み込む
        Config.read_file(cfg)


def get_aws_credentials_section_dict() -> collections.OrderedDict:
    """~/.aws/credentials から Section 情報を取得する"""
    prepare_aws_credentials()
    # 該当 ini ファイルのセクション dictionary を取得
    return Config._sections


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


def get_role_profile(profile_obj_list) -> list:
    """IAM ロールの Profile のリストを取得する"""
    role_obj_list = []
    for i in profile_obj_list:
        if i.role_arn is not None:
            role_obj_list.append(i)

    return role_obj_list


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


#################################
# Provide Prompts
################################
def prompt_user_selection(perfect_profile_list):
    """ターミナルに、プロフィール番号の選択を促すプロンプトを表示する"""
    if len(perfect_profile_list) != 0:
        print(MSG_ASK_SELECT_PROFILE)
        count = 1
        for p in perfect_profile_list:
            # リストの要素のうち、credential にも存在していた要素だけがプロンプトに出力される
            if p.aws_access_key_id != None:
                print("{}) {}".format(count, p.name))
                count += 1


def ask_user_input() -> str:
    """プロフィール番号を受け付けるため、ユーザーのインプットを待ち受ける"""

    return input(ASKING_USER_INPUT_MESSAGE)


def ask_input_integer(profile_num_input, perfect_profile_list: list) -> bool:
    """
    While loop をテストするために、ProfileNumInput クラスを介して
    Validation と ProfileNumInput インスタンスの更新を行う
    """
    # メニューを表示
    prompt_user_selection(perfect_profile_list)
    # インプットを促す
    user_input = ask_user_input()
    try:
        profile_num_input.prompt_num = user_input
        # int に変換してエラーとなるかどうかをチェック
        int(profile_num_input.prompt_num)
        return ask_input_in_list_range(profile_num_input, perfect_profile_list)
    except ValueError:
        # 誤りを指摘し、再入力を促す
        print(PROMPT_USER_INPUT_BEFORE + str(user_input) + PROMPT_USER_INPUT_AFTER)
        print(PROMPT_ENTER_AN_INT + "\n")
        return False


def ask_input_in_list_range(profile_num_input, perfect_profile_list) -> bool:
    """
    While loop をテストするために、ProfileNumInput クラスを介して
    Validation と ProfileNumInput インスタンスの更新を行う
    """

    if 0 < int(profile_num_input.prompt_num) <= len(perfect_profile_list):
        return True
    else:
        print(PROMPT_USER_INPUT_BEFORE + str(profile_num_input.prompt_num) + PROMPT_USER_INPUT_AFTER)
        print(PROMPT_NOT_AN_VALID_INT_BEFORE + str(len(perfect_profile_list)) + PROMPT_NOT_AN_VALID_INT_AFTER + "\n")
        return False

    
def ask_profile_num_input(profile_num_input: ProfileNumInput, perfect_profile_list) -> int:
    """ユーザーのインプットが validate されるまでインプットを求めるのをやめない"""
    while not ask_input_integer(profile_num_input, perfect_profile_list):
        None
    return int(profile_num_input.prompt_num)


def get_specified_profile(perfect_profile_list, validated_input) -> ProfileTuple:
    """int に応じた """
    return perfect_profile_list[validated_input - 1]


def prompt_for_asking_mfa_code(perfect_profile):
    """該当プロフィールのMFAトークン入力を促すプロンプトを表示する"""
    print(PROMPT_ASK_MFA_TOKEN_FOR_PROFILE_BEFORE + perfect_profile.name + PROMPT_ASK_MFA_TOKEN_FOR_PROFILE_AFTER)


def get_aws_account_id(perfect_profile: ProfileTuple):
    # TODO:
    return 33333333


#################################
# Access AWS
################################
def get_mfa_arn(perfect_profile: ProfileTuple):
    # TODO:
    return perfect_profile.name


def get_sts_client(perfect_profile: ProfileTuple) -> boto3.session.Session:
    session = boto3.session.Session(profile_name=perfect_profile.name)
    return session.client('sts')


#################################
# Orchestrate functions
################################
def main():

    # 設定の事前確認
    check_aws_config_existence()
    check_aws_credentials_existence()
    # 設定情報取得
    profile_list = get_profile_obj_list()
    perfect_profile_list = get_perfect_profile_list(
        profile_list,
        get_credentials_obj_list())
    role_profile = get_role_profile(profile_list)
    # ユーザー入力要求
    validated_input = ask_profile_num_input(ProfileNumInput(), perfect_profile_list)
    selected_profile = get_specified_profile(perfect_profile_list, validated_input)
    prompt_for_asking_mfa_code(selected_profile)

    get_sts_client(selected_profile)


if __name__ == "__main__":
    main()

