#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG, INFO
from logging.handlers import RotatingFileHandler
import collections
import os
import configparser
from typing import NamedTuple
import boto3
from botocore.exceptions import ClientError, ParamValidationError

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

ASKING_INPUT_ROLE_NUM_MESSAGE = "Role No. : "
MSG_ASK_SELECT_PROFILE = "スイッチロール対象の番号を、選択してください"
MSG_DO_NOT_SWITCH = "0) スイッチロールを行わない"


#################################
# Asks for profile number input
################################
def prompt_role_selection(role_list):
    """ターミナルに、プロフィール番号の選択を促すプロンプトを表示する"""
    if len(role_list) != 0:
        print(MSG_ASK_SELECT_PROFILE)
        print(MSG_DO_NOT_SWITCH)
        count = 1
        for profile_obj_for_role in role_list:
            print("{}) {}".format(count, profile_obj_for_role.name))
            count += 1
