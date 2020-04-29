#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG, INFO
from logging.handlers import RotatingFileHandler
from set_aws_mfa.helper import helper
from set_aws_mfa.helper.helper import IntObject
from set_aws_mfa.prompts import prompt_user_selection
from set_aws_mfa.helper.helper import get_input

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


# ファイルパス
AWS_CONFIG = "~/.aws/config"
AWS_ACCOUNT_FOR_SET_AWS_MFA = "~/.aws_accounts_for_set_aws_mfa"
AWS_CREDENTIALS = "~/.aws/credentials"
# ファイルがないですよプロンプト
NO_AWS_CONFIG_ERROR = "There is no '~/.aws/config'. You need to set with `aws configure` command."
NO_AWS_CREDENTIALS_ERROR = "There is no '~/.aws/credentials'. You need to set with `aws configure` command."
# 入力し直しプロンプト
PROMPT_USER_INPUT_BEFORE = "\nあなたが入力したのは"
PROMPT_USER_INPUT_AFTER = "です"
PROMPT_ENTER_AN_INT = "数値を入力してください"
# 番号入力要求プロンプト
ASKING_USER_INPUT_MESSAGE = "Profile No. : "
PROMPT_NOT_AN_VALID_INT_BEFORE = "0から"
PROMPT_NOT_AN_VALID_INT_AFTER = "の数値を入力してください"
INPUT_No = "No: "
# 認証失敗プロンプト
MFA_FAILURE_MESSAGE = "\nおっと.....!\n\n認証に失敗しました.\nユーザー名、AWS アカウント ID、MFA CODE のいずれかが" \
                      "間違っているかもしれません。\n修正対象を選んでください\n\n1) ユーザー名\n2) AWS アカウント ID\n3) MFA コード\n4) 修正せずに終了する\n\n"


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


def check_aws_accounts_for_set_aws_mfa_existence() -> bool:
    """
    Check if ~/.aws_accounts_for_set_aws_mfa exists
    """
    return helper.is_this_file_exists_in_local(AWS_ACCOUNT_FOR_SET_AWS_MFA)


# Validate STEP 1/3
def ask_profile_num_input_till_its_validated(int_obj: IntObject, perfect_profile_list) -> int:
    """ユーザーのインプットが validate されるまでインプットを求めるのをやめない"""
    while not is_input_int_and_in_range_for_profile_selection(int_obj, perfect_profile_list, ASKING_USER_INPUT_MESSAGE):
        None
    # validate_is_input_int_and_in_range() で validate されたインプットを返す
    return int(int_obj.prompt_num)


# Validate STEP 2/3
def is_input_int_and_in_range_for_profile_selection(int_obj: IntObject, _list: list, message: str) -> bool:
    """
    While loop をテストするために、IntObject クラスを介して
    Validation と IntObject インスタンスの更新を行う
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
        print(PROMPT_USER_INPUT_BEFORE + str(user_input) + PROMPT_USER_INPUT_AFTER)
        print(PROMPT_ENTER_AN_INT + "\n")
        return False


# Validate STEP 3/3
def is_input_in_profile_list_range(int_obj: IntObject, perfect_profile_list: list) -> bool:
    """
    While loop をテストするために、IntObject クラスを介して
    Validation と IntObject インスタンスの更新を行う
    """

    # input で受け取った値が リストの範囲内かどうかチェック
    if 0 < int(int_obj.prompt_num) <= len(perfect_profile_list):
        return True
    else:
        print(PROMPT_USER_INPUT_BEFORE + str(int_obj.prompt_num) + PROMPT_USER_INPUT_AFTER)
        print(PROMPT_NOT_AN_VALID_INT_BEFORE + str(len(perfect_profile_list)) +
              PROMPT_NOT_AN_VALID_INT_AFTER + "\n")
        return False


# Validate STEP 1/2
def ask_for_mfa_failure_inputs(int_obj: IntObject) -> int:
    """番号入力 input() が validate するまでループさせる"""
    while not is_input_int_and_in_range_for_mfa_failure(int_obj, INPUT_No):
        pass
    return int_obj.prompt_num


# Validate STEP 2/2
def is_input_int_and_in_range_for_mfa_failure(int_obj: IntObject, message: str) -> bool:
    """
    While loop をテストするために、IntObject クラスを介して
    Validation と IntObject インスタンスの更新を行う
    """
    menu_num = 4
    # メニューを表示
    print(MFA_FAILURE_MESSAGE)
    # インプットを促す
    user_input = get_input(message)

    try:
        # 値を引き継ぐために、IntObject インスタンスを使用
        int_obj.prompt_num = user_input
        # int に変換してエラーとなるかどうかをチェック
        int(int_obj.prompt_num)
        # int 変換でエラーにならなかった場合、今度は下記で、値が範囲内かどうかcheck
        if int(int_obj.prompt_num) <= menu_num:
            return True
        else:
            print("1 から {0} の値を入力してください".format(menu_num))
            return False
    except ValueError:
        # 誤りを指摘し、再入力を促すプロンプトを表示
        print(PROMPT_USER_INPUT_BEFORE + str(user_input) + PROMPT_USER_INPUT_AFTER)
        print(PROMPT_ENTER_AN_INT + "\n")
        return False


def ask_for_selection(prompt_msg: str, min_menu_num: int, max_menu_num: int) -> int:
    """番号入力 input() が validate するまでループさせる"""
    int_obj = IntObject()

    while not is_input_int_and_in_range(int_obj, prompt_msg, min_menu_num, max_menu_num):
        pass
    return int_obj.prompt_num


def is_input_int_and_in_range(int_obj: IntObject, prompt_str: str, min_menu_num: int, max_menu_num: int) -> bool:
    user_input = get_input(prompt_str)
    try:
        # 値を引き継ぐために、IntObject インスタンスを使用
        int_obj.prompt_num = user_input
        # int に変換してエラーとなるかどうかをチェック
        int(int_obj.prompt_num)
        # int 変換でエラーにならなかった場合、今度は下記で、値が範囲内かどうかcheck
        if (int(int_obj.prompt_num) <= max_menu_num) and (int(int_obj.prompt_num) >= min_menu_num):
            return True
        else:
            print("{} から {} の値を入力してください".format(min_menu_num, max_menu_num))
            return False
    except ValueError:
        # 誤りを指摘し、再入力を促すプロンプトを表示
        print(PROMPT_USER_INPUT_BEFORE + str(user_input) + PROMPT_USER_INPUT_AFTER)
        print(PROMPT_ENTER_AN_INT + "\n")
        return False


def validate_input_actions_for_role(role_for_the_profile_list) -> int:
    prompt_str = INPUT_No
    min_menu_num = 0
    max_menu_num = len(role_for_the_profile_list) + 1
    return ask_for_selection(prompt_str, min_menu_num, max_menu_num)
