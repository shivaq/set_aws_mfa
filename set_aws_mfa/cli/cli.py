#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
from logging.handlers import RotatingFileHandler
from set_aws_mfa.data import data_manager
from set_aws_mfa import validate

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


AWS_TMP_TOKEN = "~/.aws_tmp_token_for_set_mfa"


def access_aws_with_mfa_code(selected_profile):
    # 選択した profile の mfa の arn を用意するために、aws account id を取得
    mfa_arn = data_manager.get_mfa_arn(selected_profile)

    mfa_code = data_manager.get_mfa_code(selected_profile)

    sts_client = data_manager.get_sts_client(selected_profile)

    token_info = data_manager.get_token_info(selected_profile, sts_client, mfa_arn, str(mfa_code))

    data_manager.create_a_file_to_set_env_var(token_info)

    print("Please execute 'source {}'".format(AWS_TMP_TOKEN))


def access_aws_after_reset_aws_account_id(selected_profile):
    data_manager.reset_aws_account_id(selected_profile)
    access_aws_with_mfa_code(selected_profile)


def start_set_aws_mfa():
    # 設定の事前確認
    validate.check_aws_config_existence()
    validate.check_aws_credentials_existence()

    # 設定情報取得
    profile_list = data_manager.get_profile_obj_list()
    role_profile = data_manager.get_role_profile(profile_list)

    # profile 選択のためのユーザー入力要求
    selected_profile = data_manager.get_selected_profile()
    role_for_the_profile_list = data_manager.get_role_list_for_a_profile(selected_profile, profile_list)
    print(role_for_the_profile_list)
    # TODO: profile と関連するロールを取得する
    # TODO: 関連ロールがない場合、入力を促す
    # TODO: role の選択を促す
    # TODO: 選択したロールで、認証をする
    # TODO: 該当ロールでの認証に失敗したら、ロールのデータを更新、削除を促す
    # TODO: 再度認証を試みる

    # access_aws_with_mfa_code(selected_profile)
