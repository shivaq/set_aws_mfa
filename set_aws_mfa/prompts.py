#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG, INFO
from logging.handlers import RotatingFileHandler
from set_aws_mfa.data.model import ProfileTuple
from typing import List

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


# ロール番号入力要求プロンプト
MSG_ASK_SELECT_ROLE = "スイッチロール対象の番号を、選択してください"
MSG_DO_NOT_SWITCH = "0) スイッチロールを行わない"
# 番号入力要求プロンプト
MSG_ASK_SELECT_PROFILE = "Input a number for an aws login user."
# AWS Account Id 入力要求プロンプト
PROMPT_ASK_AWS_ACCOUNT_ID_FOR_PROFILE_BEFORE = "\n"
PROMPT_ASK_AWS_ACCOUNT_ID_FOR_PROFILE_AFTER = " 用の aws account id が記録されていません。入力してください。"
PROMPT_ASK_UPDATE_AWS_ACCOUNT_ID_FOR_PROFILE_AFTER = " 用の aws account id を更新します。入力してください。"
# MFAコード入力要求プロンプト
PROMPT_ASK_MFA_TOKEN_FOR_PROFILE_BEFORE = "\n"
PROMPT_ASK_MFA_TOKEN_FOR_PROFILE_AFTER = " 用のMFAコードを入力してください。"
# ロール関係プロンプト
MSG_SUGGEST_REGISTER_ROLE = "がスイッチできるロールがセットされていません。セットしますか？"
MSG_SUGGEST_SELECT_ROLE = "がスイッチするロールを選んでください"


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


def prompt_for_asking_aws_account_id(perfect_profile: ProfileTuple):
    """該当プロフィールのアカウントID入力を促すプロンプトを表示する"""
    print(PROMPT_ASK_AWS_ACCOUNT_ID_FOR_PROFILE_BEFORE + perfect_profile.name +
          PROMPT_ASK_AWS_ACCOUNT_ID_FOR_PROFILE_AFTER)


def prompt_for_update_aws_account_id(perfect_profile: ProfileTuple):
    """該当プロフィールのアカウントID入力を促すプロンプトを表示する"""
    print(PROMPT_ASK_AWS_ACCOUNT_ID_FOR_PROFILE_BEFORE + perfect_profile.name +
          PROMPT_ASK_UPDATE_AWS_ACCOUNT_ID_FOR_PROFILE_AFTER)


def prompt_for_asking_mfa_code(perfect_profile: ProfileTuple):
    """該当プロフィールのMFAトークン入力を促すプロンプトを表示する"""
    print(PROMPT_ASK_MFA_TOKEN_FOR_PROFILE_BEFORE + perfect_profile.name + PROMPT_ASK_MFA_TOKEN_FOR_PROFILE_AFTER)


def prompt_msg_for_the_profile_roles(profile: ProfileTuple, role_for_the_profile_list: List[ProfileTuple]):
    """選択したプロファイルでスイッチロールをするかどうか等のメッセージを表示する"""
    if len(role_for_the_profile_list) == 0:
        print("\n" + profile.name + " " + MSG_SUGGEST_REGISTER_ROLE)
    else:
        print("\n" + profile.name + " " + MSG_SUGGEST_SELECT_ROLE)


def prompt_role_selection(role_list):
    """ターミナルに、プロフィール番号の選択を促すプロンプトを表示する"""
    if len(role_list) != 0:
        print(MSG_DO_NOT_SWITCH)
        count = 1
        for profile_obj_for_role in role_list:
            print("{}) {}".format(count, profile_obj_for_role.name))
            count += 1
