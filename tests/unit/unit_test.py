#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from set_aws_mfa.helper.helper import IntObject
from set_aws_mfa.helper import helper
from set_aws_mfa.data import data_manager
from set_aws_mfa import prompts
from set_aws_mfa import validate
from tests.conftest import BUILTIN_INPUTS


########################
# fixtures
########################
@pytest.fixture()
def get_valid_mfa_arn(monkeypatch, valid_aws_account_id, perfect_profile):

    # Mock does not use profile, but original function need it.
    def mock_get_aws_account_id(perfect_profile):
        return valid_aws_account_id

    monkeypatch.setattr(data_manager, "get_aws_account_id", mock_get_aws_account_id)
    return data_manager.get_mfa_arn(perfect_profile)


@pytest.fixture()
def get_short_mfa_arn(monkeypatch, short_aws_account_id, perfect_profile):

    # Mock does not use profile, but original function need it.
    def mock_get_aws_account_id(perfect_profile):
        return short_aws_account_id

    monkeypatch.setattr(data_manager, "get_aws_account_id", mock_get_aws_account_id)
    return data_manager.get_mfa_arn(perfect_profile)


@pytest.fixture()
def get_string_mfa_arn(monkeypatch, string_aws_account_id, perfect_profile):

    # Mock does not use profile, but original function need it.
    def mock_get_aws_account_id(perfect_profile):
        return string_aws_account_id

    monkeypatch.setattr(data_manager, "get_aws_account_id", mock_get_aws_account_id)
    return data_manager.get_mfa_arn(perfect_profile)


@pytest.fixture()
def get_sts_client(perfect_profile):
    return data_manager.get_sts_client(perfect_profile)


























