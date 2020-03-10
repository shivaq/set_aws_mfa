#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG, INFO
from logging.handlers import RotatingFileHandler
import collections
import os
import configparser
from typing import NamedTuple
import boto3
from botocore.client import ClientError

from helper import helper
from helper.helper import IntObject

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
PROMPT_NOT_AN_VALID_INT_BEFORE = "0から"
PROMPT_NOT_AN_VALID_INT_AFTER = "の数値を入力してください"
PROMPT_ASK_MFA_TOKEN_FOR_PROFILE_BEFORE = "\n"
PROMPT_ASK_MFA_TOKEN_FOR_PROFILE_AFTER = " 用のMFAコードを入力してください。"
AWS_ACCOUNT_FOR_SET_AWS_MFA = "~/.aws_accounts_for_set_aws_mfa"
PROMPT_ASK_AWS_ACCOUNT_ID_FOR_PROFILE_BEFORE = "\n"
PROMPT_ASK_AWS_ACCOUNT_ID_FOR_PROFILE_AFTER = " 用の aws account id が記録されていません。入力してください。"
ASKING_AWS_ACCOUNT_ID_INPUT_MESSAGE = "Aws account Id : "
AWS_IAM_ARN_HEAD_PART = "arn:aws:iam::"
AWS_IAM_ARN_MFA_PART = ":mfa/"
ASKING_MFA_CODE_BEFORE = "MFA code for "
ASKING_MFA_CODE_AFTER = ": "

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


#################################
# Retrieve Settings
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


def check_aws_config_existence():
    """
    Check if ~/.aws/config exists
    """
    if not helper.is_this_file_exists_in_local(AWS_CONFIG):
        raise FileNotFoundError(NO_AWS_CONFIG_ERROR)


def check_aws_credentials_existence():
    """
    Check if ~/.aws/credentials exists
    """
    if not helper.is_this_file_exists_in_local(AWS_CREDENTIALS):
        raise FileNotFoundError(NO_AWS_CREDENTIALS_ERROR)


def get_aws_config_section_dict() -> collections.OrderedDict:
    """~/.aws/config から Section 情報を取得する"""
    prepare_to_read_local_ini_file(AWS_CONFIG)
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


def get_aws_credentials_section_dict() -> collections.OrderedDict:
    """~/.aws/credentials から Section 情報を取得する"""
    prepare_to_read_local_ini_file(AWS_CREDENTIALS)
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
# Asks for profile number input
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


# Validate STEP 1/3
def ask_profile_num_input_till_its_validated(int_obj: IntObject, perfect_profile_list) -> int:
    """ユーザーのインプットが validate されるまでインプットを求めるのをやめない"""
    while not is_input_int_and_in_range(int_obj, perfect_profile_list, ASKING_USER_INPUT_MESSAGE):
        None
    # validate_is_input_int_and_in_range() で validate されたインプットを返す
    return int(int_obj.prompt_num)


# Validate STEP 2/3
def is_input_int_and_in_range(int_obj: IntObject, _list: list, message: str) -> bool:
    """
    While loop をテストするために、NumInputForWhileLoop クラスを介して
    Validation と NumInputForWhileLoop インスタンスの更新を行う
    """
    # メニューを表示
    prompt_user_selection(_list)
    # インプットを促す
    user_input = helper.get_input(message)

    try:
        # validate_is_input_int_and_in_range() に値を引き継ぐために、
        # NumInputForWhileLoop インスタンスを使用
        int_obj.prompt_num = user_input
        # int に変換してエラーとなるかどうかをチェック
        int(int_obj.prompt_num)
        # int 変換でエラーにならなかった場合、今度は下記で、値が範囲内かどうか✅
        return is_input_in_profile_list_range(int_obj, _list)
    except ValueError:
        # 誤りを指摘し、再入力を促すプロンプトを表示
        print(helper.PROMPT_USER_INPUT_BEFORE + str(user_input) + helper.PROMPT_USER_INPUT_AFTER)
        print(helper.PROMPT_ENTER_AN_INT + "\n")
        return False


# Validate STEP 3/3
def is_input_in_profile_list_range(int_obj: IntObject, perfect_profile_list: list) -> bool:
    """
    While loop をテストするために、ProfileNumInput クラスを介して
    Validation と ProfileNumInput インスタンスの更新を行う
    """

    # input で受け取った値が リストの範囲内かどうかチェック
    if 0 < int(int_obj.prompt_num) <= len(perfect_profile_list):
        return True
    else:
        print(helper.PROMPT_USER_INPUT_BEFORE + str(int_obj.prompt_num) + helper.PROMPT_USER_INPUT_AFTER)
        print(PROMPT_NOT_AN_VALID_INT_BEFORE + str(len(perfect_profile_list)) + PROMPT_NOT_AN_VALID_INT_AFTER + "\n")
        return False


def get_specified_profile(perfect_profile_list: list, validated_input: int) -> ProfileTuple:
    """int に応じた profile を取得"""
    return perfect_profile_list[validated_input - 1]


def get_selected_profile():
    profile_list = get_profile_obj_list()
    perfect_profile_list = get_perfect_profile_list(profile_list, get_credentials_obj_list())
    validated_input = ask_profile_num_input_till_its_validated(IntObject(), perfect_profile_list)
    return get_specified_profile(perfect_profile_list, validated_input)


#################################
# Get an aws account id for a profile
################################
def check_aws_accounts_for_set_aws_mfa_existence() -> bool:
    """
    Check if ~/.aws_accounts_for_set_aws_mfa exists
    """
    return helper.is_this_file_exists_in_local(AWS_ACCOUNT_FOR_SET_AWS_MFA)


def create_aws_account_id_file():
    """
    Create ~/.aws_accounts_for_set_aws_mfa if it is not exists
    """
    helper.create_a_file_in_local(AWS_ACCOUNT_FOR_SET_AWS_MFA)


def prepare_aws_account_id_file():
    """
    ~/.aws_accounts_for_set_aws_mfa の存在を確認し、なければ作成する
    """
    if not check_aws_accounts_for_set_aws_mfa_existence():
        create_aws_account_id_file()
    prepare_to_read_local_ini_file(AWS_ACCOUNT_FOR_SET_AWS_MFA)


def prompt_for_asking_aws_account_id(perfect_profile):
    """該当プロフィールのアカウントID入力を促すプロンプトを表示する"""
    print(PROMPT_ASK_AWS_ACCOUNT_ID_FOR_PROFILE_BEFORE + perfect_profile.name +
          PROMPT_ASK_AWS_ACCOUNT_ID_FOR_PROFILE_AFTER)


def writing_aws_account_to_the_file(profile: ProfileTuple, aws_account_id: int):
    """該当 profile の aws account id を AWS_ACCOUNT_FOR_SET_AWS_MFA に書き込む"""

    prepare_to_read_local_ini_file(AWS_ACCOUNT_FOR_SET_AWS_MFA)

    Config[profile.name] = {"aws_account_id": aws_account_id}
    filename = os.path.expanduser(AWS_ACCOUNT_FOR_SET_AWS_MFA)
    with open(filename, "w") as configfile:
        Config.write(configfile)


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
        prompt_for_asking_aws_account_id(perfect_profile)
        aws_account_id = helper.ask_int_input_till_its_validated(IntObject(), ASKING_AWS_ACCOUNT_ID_INPUT_MESSAGE)
        # 該当ファイルに書き込む
        writing_aws_account_to_the_file(perfect_profile, aws_account_id)
        # 再帰的に本関数を呼び出して、書き込み済みの aws account id を取得する
        get_aws_account_id(perfect_profile)

    return int(aws_account_id)


#################################
# Ask MFA code
################################
def prompt_for_asking_mfa_code(perfect_profile: ProfileTuple):
    """該当プロフィールのMFAトークン入力を促すプロンプトを表示する"""
    print(PROMPT_ASK_MFA_TOKEN_FOR_PROFILE_BEFORE + perfect_profile.name + PROMPT_ASK_MFA_TOKEN_FOR_PROFILE_AFTER)


def get_mfa_code(perfect_profile: ProfileTuple):

    prompt_for_asking_mfa_code(perfect_profile)
    return helper.ask_int_input_till_its_validated(
        IntObject(), ASKING_MFA_CODE_BEFORE + perfect_profile.name + ASKING_MFA_CODE_AFTER
    )


#################################
# Access AWS
################################
def get_mfa_arn(perfect_profile: ProfileTuple) -> str:
    """mfa arn を返す"""

    return AWS_IAM_ARN_HEAD_PART + str(
        get_aws_account_id(perfect_profile)) + AWS_IAM_ARN_MFA_PART + perfect_profile.name


def get_sts_client(perfect_profile: ProfileTuple) -> boto3.session.Session:
    session = None
    try:
        session = boto3.session.Session(profile_name=perfect_profile.name)
    except ClientError:
        logger.exception("Failed to get session.")

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
    role_profile = get_role_profile(profile_list)

    # profile 選択のためのユーザー入力要求
    selected_profile = get_selected_profile()

    # 選択した profile の mfa の arn を用意するために、aws account id を取得
    mfa_arn = get_mfa_arn(selected_profile)

    mfa_code = get_mfa_code(selected_profile)

    get_sts_client(selected_profile)


if __name__ == "__main__":
    main()
