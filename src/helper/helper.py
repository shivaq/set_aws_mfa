#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os


def is_this_file_exists_in_local(local_file_path: str) -> bool:
    """ローカルファイルが存在しているか否かを返す"""
    filename = os.path.expanduser(local_file_path)
    return os.path.exists(filename)