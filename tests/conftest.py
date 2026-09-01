# -*- coding: utf-8 -*-
"""pytest 公共夹具：让测试能导入 app，并为每个测试准备独立的临时数据库。"""
import os
import sys

import pytest

# 把 src 目录加入导入路径，这样测试里可以直接 import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import app as app_module


@pytest.fixture()
def client(tmp_path):
    """每个测试用一个独立的临时 SQLite 库，互不干扰。"""
    app_module.DB_PATH = str(tmp_path / "test.db")  # 指向临时库
    app_module.app.config["TESTING"] = True
    app_module.init_db()
    with app_module.app.test_client() as c:
        yield c
