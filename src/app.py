# -*- coding: utf-8 -*-
"""
用户管理系统 —— 测试实习生作品项目的「被测系统」

功能：
  - 注册 / 登录 / 退出 / 查看用户列表（页面）
  - 对应的 JSON 接口（/api/*），供接口测试和自动化测试使用

技术栈：Flask + SQLite + session（密码用哈希存储）

注意：这是一个「被测对象」，故意做得简单直接，方便你理解每一行。
"""
import os
import re
import sqlite3
from flask import (Flask, request, session, redirect, url_for,
                   render_template, jsonify, flash)
from werkzeug.security import generate_password_hash, check_password_hash

# 数据库文件路径：默认放在 src/ 目录下，也可用环境变量覆盖（测试时指向临时库）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("USERS_DB_PATH", os.path.join(BASE_DIR, "users.db"))

app = Flask(__name__)
app.secret_key = "test-intern-demo-secret"  # 生产环境应使用随机密钥


# ---------------- 数据库 ----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 让查询结果可以按列名取值，如 row["username"]
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ---------------- 校验规则（这是测试用例的重要依据） ----------------
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")           # 3-20位，字母/数字/下划线
PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[\S]{6,20}$")  # 6-20位，至少一个字母+一个数字
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")        # 简单邮箱格式


def validate_register(username, password, email):
    """校验注册信息，合法返回 None，否则返回错误提示文案。"""
    if not username:
        return "用户名不能为空"
    if not USERNAME_RE.match(username):
        return "用户名需为 3-20 位，只能包含字母、数字、下划线"
    if not password:
        return "密码不能为空"
    if not PASSWORD_RE.match(password):
        return "密码需为 6-20 位，且必须同时包含字母和数字"
    if not email:
        return "邮箱不能为空"
    if not EMAIL_RE.match(email):
        return "邮箱格式不正确"
    return None


# ---------------- 页面路由 ----------------
@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("user_list"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        email = request.form.get("email", "").strip()

        err = validate_register(username, password, email)
        if err is None and password != confirm:
            err = "两次输入的密码不一致"

        if err:
            flash(err, "error")
            return render_template("register.html", username=username, email=email)

        db = get_db()
        exists = db.execute(
            "SELECT 1 FROM users WHERE username = ?", (username,)
        ).fetchone()
        if exists:
            db.close()
            flash("用户名已存在", "error")
            return render_template("register.html", username=username, email=email)

        db.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), email),
        )
        db.commit()
        db.close()
        flash("注册成功，请登录", "success")
        return redirect(url_for("login"))

    return render_template("register.html", username="", email="")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("用户名和密码不能为空", "error")
            return render_template("login.html", username=username)

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        db.close()

        if user is None:
            flash("用户名不存在", "error")
        elif not check_password_hash(user["password_hash"], password):
            flash("密码错误", "error")
        else:
            session["user"] = user["username"]
            return redirect(url_for("user_list"))

    return render_template("login.html", username="")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/users")
def user_list():
    if "user" not in session:
        return redirect(url_for("login"))
    db = get_db()
    users = db.execute(
        "SELECT id, username, email, created_at FROM users ORDER BY id"
    ).fetchall()
    db.close()
    return render_template("users.html", users=users, current_user=session["user"])


# ---------------- JSON 接口（供接口测试 / 自动化测试使用） ----------------
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    email = (data.get("email") or "").strip()

    err = validate_register(username, password, email)
    if err:
        return jsonify({"code": 1, "msg": err}), 400

    db = get_db()
    exists = db.execute(
        "SELECT 1 FROM users WHERE username = ?", (username,)
    ).fetchone()
    if exists:
        db.close()
        return jsonify({"code": 1, "msg": "用户名已存在"}), 400

    db.execute(
        "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
        (username, generate_password_hash(password), email),
    )
    db.commit()
    db.close()
    return jsonify({"code": 0, "msg": "注册成功"}), 201


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"code": 1, "msg": "用户名和密码不能为空"}), 400

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    db.close()

    if user is None:
        return jsonify({"code": 1, "msg": "用户名不存在"}), 401
    if not check_password_hash(user["password_hash"], password):
        return jsonify({"code": 1, "msg": "密码错误"}), 401
    return jsonify({"code": 0, "msg": "登录成功",
                    "data": {"username": user["username"]}})


@app.route("/api/users", methods=["GET"])
def api_users():
    db = get_db()
    users = db.execute(
        "SELECT id, username, email, created_at FROM users ORDER BY id"
    ).fetchall()
    db.close()
    return jsonify({"code": 0, "data": [dict(u) for u in users]})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
