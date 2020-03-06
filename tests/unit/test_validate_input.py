#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from random import randint
from random import choice
from set_aws_mfa import set_aws_mfa
from set_aws_mfa.set_aws_mfa import IntObject
import string


def test_user_input_num_ok_validation(perfect_profile_list, monkeypatch):
    # GIVEN: User inputs random integer within perfect_profile_list range
    user_input_int = randint(1, len(perfect_profile_list))
    # GIVEN: Mock user input integer
    monkeypatch.setattr('builtins.input', lambda _: user_input_int)

    # WHEN: Validate the number
    is_that_int = set_aws_mfa.is_input_int_and_in_range(
        IntObject(), perfect_profile_list)

    # THEN: the returned value is True
    assert is_that_int


def test_user_input_num_not_ok_validation(perfect_profile_list, monkeypatch):

    # GIVEN: User inputs random strings
    letters = string.ascii_letters
    user_input_str = ''.join(choice(letters) for i in range(10))
    # GIVEN: Mock user input string
    monkeypatch.setattr('builtins.input', lambda _: user_input_str)

    # WHEN: Validate the input
    is_int = set_aws_mfa.is_input_int_and_in_range(
        IntObject(), perfect_profile_list)
    # THEN: It's not an int
    assert not is_int


def test_input_in_list_range():

    # GIVEN: a static length of list
    _list = [1, 2, 3]
    # GIVEN: a num
    profile_num_input = IntObject(prompt_num=2)
    # WHEN: check if a num is in range of the list
    # THEN: True
    is_in_range = set_aws_mfa.is_input_in_profile_list_range(
        profile_num_input, _list)
    assert is_in_range


def test_input_is_not_in_list_range():

    # GIVEN: a static length of list
    _list = [1, 2, 3]
    # GIVEN: a num
    profile_num_input = IntObject(prompt_num=0)
    # WHEN: check if a num is in range of the list
    # THEN: True
    is_in_range = set_aws_mfa.is_input_in_profile_list_range(
        profile_num_input, _list)
    assert not is_in_range
