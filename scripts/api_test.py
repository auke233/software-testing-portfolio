# -*- coding: utf-8 -*-
"""
接口测试脚本（requests 版）
对应《测试用例.md》中的 API_001 ~ API_008

用法：
  1. 先启动被测系统：  cd src && ..\\venv\\Scripts\\python app.py
  2. 另开终端运行：    venv\\Scripts\\python scripts/api_test.py
"""
import uuid
import requests

BASE = "http://127.0.0.1:5000"

results = []


def check(name, cond, detail=""):
    results.append(cond)
    print(("✅ PASS" if cond else "❌ FAIL"), "|", name, "|", detail)


def post(path, data=None, raw=None):
    if raw is not None:
        return requests.post(BASE + path, data=raw,
                             headers={"Content-Type": "text/plain"}, timeout=5)
    return requests.post(BASE + path, json=data, timeout=5)


# 随机用户名，避免和数据库已有数据冲突
name = "user_" + uuid.uuid4().hex[:6]

# API_001 正常注册
r = post("/api/register", {"username": name, "password": "abc123", "email": "t@x.com"})
check("API_001 正常注册", r.status_code == 201 and r.json().get("code") == 0,
      f"status={r.status_code} body={r.json()}")

# API_002 缺密码字段
r = post("/api/register", {"username": name, "email": "t@x.com"})
check("API_002 缺密码字段", r.status_code == 400 and r.json().get("code") == 1,
      f"status={r.status_code}")

# API_003 重复用户名
r = post("/api/register", {"username": name, "password": "abc123", "email": "t2@x.com"})
check("API_003 重复用户名", r.status_code == 400 and "已存在" in r.json().get("msg", ""),
      f"status={r.status_code}")

# API_004 正常登录
r = post("/api/login", {"username": name, "password": "abc123"})
check("API_004 正常登录", r.status_code == 200 and r.json().get("code") == 0,
      f"status={r.status_code} data={r.json().get('data')}")

# API_005 密码错误
r = post("/api/login", {"username": name, "password": "wrong"})
check("API_005 密码错误", r.status_code == 401 and r.json().get("code") == 1,
      f"status={r.status_code}")

# API_006 用户名不存在
r = post("/api/login", {"username": "no_such_user_xx", "password": "abc123"})
check("API_006 用户名不存在", r.status_code == 401 and "不存在" in r.json().get("msg", ""),
      f"status={r.status_code}")

# API_007 请求体非 JSON
r = post("/api/login", raw="this is not json")
check("API_007 非JSON请求体", r.status_code == 400,
      f"status={r.status_code} body={r.json()}")

# API_008 用户列表
r = requests.get(BASE + "/api/users", timeout=5)
check("API_008 用户列表", r.status_code == 200 and r.json().get("code") == 0,
      f"status={r.status_code} 用户数={len(r.json().get('data', []))}")

print()
print(f"共 {len(results)} 条，通过 {sum(results)} 条，失败 {len(results) - sum(results)} 条")
