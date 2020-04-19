#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from set_aws_mfa.data.data_manager import ProfileTuple
from set_aws_mfa.data.data_manager import CredentialTuple
from set_aws_mfa.helper.helper import IntObject


def test_classes_magic_methods():
    temp_name = "Suzuki"
    temp_region = "eu-central-1"
    temp_profile = ProfileTuple(temp_name, temp_region).__repr__()
    assert temp_name in temp_profile
    assert temp_region in temp_profile
    temp_cred = CredentialTuple(temp_name).__repr__()
    assert temp_name in temp_cred
    temp_int = IntObject(9).__repr__()
    assert "9" in temp_int
