#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os


def is_this_file_exists_in_local(local_file_path: str) -> bool:
    """ローカルファイルが存在しているか否かを返す"""
    filename = os.path.expanduser(local_file_path)
    return os.path.exists(filename)


def create_a_file_in_local(local_file_path_str: str):
    """ローカルにファイルを作成する"""
    filename = os.path.expanduser(local_file_path_str)
    open(filename, 'w+')


def delete_a_file_if_it_exists(local_file_path_str:str):
    """該当ローカルファイルが存在していた場合、削除する"""
    filename = os.path.expanduser(local_file_path_str)
    if is_this_file_exists_in_local(local_file_path_str):
        os.remove(filename)
