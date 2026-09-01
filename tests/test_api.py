# -*- coding: utf-8 -*-
"""
接口自动化测试（pytest 版）
覆盖注册、登录、用户列表三个接口，含边界值测试。
运行：  venv\\Scripts\\python -m pytest tests/ -v
"""
import pytest


def _register(client, username, password="abc123", email="t@x.com"):
    return client.post("/api/register", json={
        "username": username, "password": password, "email": email
    })


# ---------- 注册 ----------
def test_register_ok(client):
    r = _register(client, "alice")
    assert r.status_code == 201
    assert r.get_json()["code"] == 0


def test_register_missing_password(client):
    r = client.post("/api/register", json={"username": "alice", "email": "t@x.com"})
    assert r.status_code == 400
    assert r.get_json()["code"] == 1


def test_register_duplicate_username(client):
    _register(client, "alice")
    r = _register(client, "alice")
    assert r.status_code == 400
    assert "已存在" in r.get_json()["msg"]


def test_register_weak_password(client):
    # 纯数字，缺少字母，应被拦截
    r = _register(client, "bob", password="123456")
    assert r.status_code == 400


def test_register_invalid_email(client):
    r = _register(client, "carol", email="not-an-email")
    assert r.status_code == 400


# ---------- 边界值：用户名长度 ----------
@pytest.mark.parametrize("username,expect_ok", [
    ("ab", False),        # 2 位，下边界外
    ("abc", True),        # 3 位，下边界
    ("a" * 20, True),     # 20 位，上边界
    ("a" * 21, False),    # 21 位，上边界外
])
def test_username_boundary(client, username, expect_ok):
    r = _register(client, username)
    assert (r.status_code == 201) == expect_ok


# ---------- 登录 ----------
def test_login_ok(client):
    _register(client, "alice")
    r = client.post("/api/login", json={"username": "alice", "password": "abc123"})
    assert r.status_code == 200
    assert r.get_json()["data"]["username"] == "alice"


def test_login_wrong_password(client):
    _register(client, "alice")
    r = client.post("/api/login", json={"username": "alice", "password": "wrong"})
    assert r.status_code == 401
    assert "密码错误" in r.get_json()["msg"]


def test_login_user_not_exist(client):
    r = client.post("/api/login", json={"username": "nobody", "password": "abc123"})
    assert r.status_code == 401
    assert "不存在" in r.get_json()["msg"]


# ---------- 用户列表 ----------
def test_users_list(client):
    _register(client, "alice")
    _register(client, "bob", email="b@x.com")
    r = client.get("/api/users")
    assert r.status_code == 200
    assert len(r.get_json()["data"]) == 2
