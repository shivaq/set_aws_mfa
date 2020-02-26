#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from set_aws_mfa import set_aws_mfa
import subprocess
import re
import pytest
from test.support import captured_stdout

# 1. ジーザスはターミナルを開く
# 1. ジーザスが set_aws_mfa コマンドを叩くと、有効なユーザーリストが表示される


def test_prompt_iam_user_list(perfect_profile_list):
    """
    コマンドを叩くと、Iam ユーザーを選択する画面が表示される
    """

    # WHEN: コンソールでコマンドを実行
    result = subprocess.run(
        ['python', 'src/set_aws_mfa/set_aws_mfa.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    lines = result.stdout.decode('utf-8').rstrip().splitlines()

    # GIVEN: 有効なプロフィールがあった場合(プロンプトが標準出力に表示された場合)
    if len(lines) > 1:
        # THEN: プロンプトの文字列が出力される
        assert lines[0] == set_aws_mfa.MSG_ASK_SELECT_PROFILE
        for i, line in enumerate(lines):
            # GIVEN: プロンプトの1行目及び最後以外の行の出力を確認したとき
            if i != 0 and i != len(lines) -1:
                # THEN: 数値) で始まる出力がなされる
                assert re.compile(r"^[0-99]+\)\s").match(line)

            


# 1. リストに表示された番号を入力すると、MFA の入力を求められる

# 1. MFA を入力すると認証が実行される

# 1. 選択したユーザーの前回のログイン日情報が表示される(IAM へのアクセスができたことがわかる)
