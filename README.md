# 软件测试实习生作品项目：用户管理系统

![CI](https://github.com/auke233/software-testing-portfolio/actions/workflows/ci.yml/badge.svg)

一个完整的软件测试实战项目 —— 从**需求分析 → 测试计划 → 用例设计 → 功能测试 → 缺陷管理 → 接口测试 → 自动化测试**走完整个测试流程。目标是展示一个测试实习生应具备的核心能力。

## 一、项目结构

```
software-testing-portfolio/
├── src/                 # 被测系统（Flask + SQLite）
│   ├── app.py           # 后端：注册/登录/用户列表 + JSON 接口
│   ├── templates/       # 页面模板
│   └── static/          # 样式
├── scripts/
│   └── api_test.py      # 接口测试脚本（requests 版）
├── tests/               # 自动化测试（pytest）
│   ├── conftest.py      # 测试夹具（独立临时数据库）
│   └── test_api.py      # 接口自动化用例（含边界值）
├── docs/                # 测试文档
│   ├── 测试计划.md
│   ├── 测试用例.md
│   ├── 缺陷报告.md
│   └── 接口测试.md
├── requirements.txt
└── README.md
```

## 二、技术栈

- **被测系统**：Python 3.11 + Flask 3 + SQLite（密码哈希存储）
- **测试工具**：pytest（自动化）、requests（接口）、Postman（可选）、curl

## 三、如何运行

```bash
# 1. 安装依赖
python -m venv venv
venv\Scripts\pip install -r requirements.txt

# 2. 启动被测系统（浏览器打开 http://127.0.0.1:5000）
cd src
..\venv\Scripts\python app.py

# 3. 运行自动化测试
cd ..
venv\Scripts\python -m pytest tests/ -v

# 4. 运行接口测试脚本（需先启动系统）
venv\Scripts\python scripts/api_test.py
```

## 四、测试交付物

| 交付物 | 位置 | 内容 |
|---|---|---|
| 测试计划 | docs/测试计划.md | 测试范围、环境、策略、准入准出 |
| 测试用例 | docs/测试用例.md | 47 条用例（等价类/边界值/场景法） |
| 缺陷报告 | docs/缺陷报告.md | 3 个真实缺陷 |
| 接口测试 | docs/接口测试.md + scripts/api_test.py | HTTP 基础 + 8 条接口用例 |
| 自动化测试 | tests/ | 13 条 pytest 用例，一键回归 |

## 五、测试结果摘要

- 用例总数：47 条（注册 27 / 登录 9 / 列表 3 / 接口 8）
- 自动化：13 条 pytest 用例全部通过
- 发现缺陷：3 个（严重 1、一般 2），详见 docs/缺陷报告.md
