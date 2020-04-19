#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

# 入力し直しプロンプト
PROMPT_USER_INPUT_BEFORE = "\nあなたが入力したのは"
PROMPT_USER_INPUT_AFTER = "です"
PROMPT_ENTER_AN_INT = "数値を入力してください"

class IntObject:
    def __init__(self, prompt_num: int = 0):
        self.prompt_num = prompt_num

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}('
                f'{self.prompt_num!r})')


def is_this_file_exists_in_local(local_file_path: str) -> bool:
    """ローカルファイルが存在しているか否かを返す"""
    filename = os.path.expanduser(local_file_path)
    return os.path.exists(filename)


def create_a_file_in_local(local_file_path_str: str):
    """ローカルにファイルを作成する"""
    filename = os.path.expanduser(local_file_path_str)
    open(filename, 'w+')


def delete_a_file_if_it_exists(local_file_path_str: str):
    """該当ローカルファイルが存在していた場合、削除する"""
    filename = os.path.expanduser(local_file_path_str)
    if is_this_file_exists_in_local(local_file_path_str):
        os.remove(filename)


def get_input(message: str) -> str:
    """ユーザーインプットを受け付けて返す"""
    return input(message)


# Validate STEP 1/2
def ask_int_input_till_its_validated(int_obj: IntObject, message: str) -> int:
    """ユーザーのインプットが validate されるまでインプットを求めるのをやめない"""
    while not is_input_int_loop(int_obj, message):
        None
    # is_input_int_loop() で validate されたインプットを返す
    return int(int_obj.prompt_num)


# Validate STEP 2/2
def is_input_int_loop(int_obj: IntObject, message: str) -> bool:
    """aws account id 用のユーザーインプットが integer であるかどうかを validate"""

    user_input = get_input(message)

    try:
        # ask_int_input_till_its_validated() に値を引き継ぐために、
        # IntObject インスタンスを使用
        int_obj.prompt_num = user_input
        # int に変換してエラーとなるかどうかをチェック
        int(int_obj.prompt_num)
        # int 変換でエラーにならなかった場合、今度は下記で、値が範囲内かどうか✅
        return True
    except ValueError:
        # 誤りを指摘し、再入力を促すプロンプトを表示
        print(PROMPT_USER_INPUT_BEFORE + str(user_input) + PROMPT_USER_INPUT_AFTER)
        print(PROMPT_ENTER_AN_INT + "\n")
        return False
