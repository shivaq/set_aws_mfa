#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from random import randint
from random import choice
import string
from set_aws_mfa import validate
from set_aws_mfa.data import data_manager
from set_aws_mfa.helper.helper import IntObject
from set_aws_mfa.helper.helper import PROMPT_USER_INPUT_BEFORE
from tests.conftest import BUILTIN_INPUTS


def test_user_input_num_ok_validation(perfect_profile_list, monkeypatch):
    # GIVEN: User inputs random integer within perfect_profile_list range
    user_input_int = randint(1, len(perfect_profile_list))
    # GIVEN: Mock user input integer
    monkeypatch.setattr('builtins.input', lambda _: user_input_int)

    # WHEN: Validate the number
    is_that_int = validate.is_input_int_and_in_range(
        IntObject(), perfect_profile_list, validate.ASKING_USER_INPUT_MESSAGE)

    # THEN: the returned value is True
    assert is_that_int


def test_user_input_num_not_ok_validation(perfect_profile_list, monkeypatch):

    # GIVEN: User inputs random strings
    letters = string.ascii_letters
    user_input_str = ''.join(choice(letters))
    # GIVEN: Mock user input string
    monkeypatch.setattr('builtins.input', lambda _: user_input_str)

    # WHEN: Validate the input
    is_int = validate.is_input_int_and_in_range(
        IntObject(), perfect_profile_list, validate.ASKING_USER_INPUT_MESSAGE)
    # THEN: It's not an int
    assert not is_int


def test_input_in_list_range():

    # GIVEN: a static length of list
    _list = [1, 2, 3]
    # GIVEN: a num
    profile_num_input = IntObject(prompt_num=2)
    # WHEN: check if a num is in range of the list
    # THEN: True
    is_in_range = validate.is_input_in_profile_list_range(
        profile_num_input, _list)
    assert is_in_range


def test_input_is_not_in_list_range():

    # GIVEN: a static length of list
    _list = [1, 2, 3]
    # GIVEN: a num
    profile_num_input = IntObject(prompt_num=0)
    # WHEN: check if a num is in range of the list
    # THEN: True
    is_in_range = validate.is_input_in_profile_list_range(
        profile_num_input, _list)
    assert not is_in_range


def test_return_user_input_num(monkeypatch, perfect_profile_list):

    # GIVEN: Mock user input string number
    monkeypatch.setattr(BUILTIN_INPUTS, lambda _: "3")

    # WHEN: validate with this function
    user_input = validate.ask_profile_num_input_till_its_validated(IntObject(), perfect_profile_list)
    # THEN: the returned value is int
    assert type(user_input) is int


def test_get_mfa_code(perfect_profile_list, monkeypatch):

    # GIVEN: a profile
    profile = perfect_profile_list[0]
    # GIVEN: Mock user input string number
    monkeypatch.setattr(BUILTIN_INPUTS, lambda _: "3334444")
    # WHEN: input mfa code
    mfa_code = data_manager.get_mfa_code(profile)
    # THEN: the returned value is an int
    assert type(mfa_code) is int


def test_input_range_failure(capsys, monkeypatch):
    """input が範囲外の数値だった場合に、プロンプトが表示され、かつ False が返ってくる"""
    # GIVEN: some message
    msg = "nothing"
    menu_num = 4
    # GIVEN: out of range input
    int_input = 33333
    monkeypatch.setattr(BUILTIN_INPUTS, lambda _: int_input)
    # WHEN: check if the input is in range
    result = validate.is_input_int_and_in_range_for_mfa_failure(IntObject(), msg)
    out, err = capsys.readouterr()
    assert not result
    assert "1 から {0} の値を入力してください".format(menu_num) in out.rstrip()


def test_input_for_mfa_with_string_error(capsys, monkeypatch):
    """input が範囲外の数値だった場合に、プロンプトが表示され、かつ False が返ってくる"""
    # GIVEN: some message
    msg = "nothing"
    # GIVEN: out of range input
    int_input = "aiueo"
    monkeypatch.setattr(BUILTIN_INPUTS, lambda _: int_input)
    # WHEN: check if the input is in range
    result = validate.is_input_int_and_in_range_for_mfa_failure(IntObject(), msg)
    out, err = capsys.readouterr()
    assert not result
    assert PROMPT_USER_INPUT_BEFORE in out.rstrip()


def test_input_wrong_mfa_code_and_re_enter_another_mfa_code(get_sts_client, get_valid_mfa_arn, monkeypatch, capsys):
    # GIVEN: select profile modification
    selected_measure = 1
    # GIVEN: Mock user input string number
    monkeypatch.setattr(BUILTIN_INPUTS, lambda _: selected_measure)
    validated_selection = validate.ask_for_mfa_failure_inputs(IntObject())

    assert type(validated_selection) is int

