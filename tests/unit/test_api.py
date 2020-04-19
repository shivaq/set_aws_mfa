#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from set_aws_mfa.data import data_manager


def test_get_sts_client(perfect_profile_list):

    # GIVEN: a ProfileTuple
    profile = perfect_profile_list[0]

    # WHEN: call the function
    sts_client = data_manager.get_sts_client(profile)

    # THEN:
    assert sts_client is not None
