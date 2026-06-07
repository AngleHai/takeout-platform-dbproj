# 🍜 外卖平台管理系统

数据库原理课程大作业 - 基于 Vue3 + Flask + MySQL 的外卖平台管理系统。

## 项目结构

```
├── frontend/          # 前端 (Vue3 + TypeScript + Arco Design)
├── backend/           # 后端 (Flask + PyJWT + MySQL)
├── database/          # 数据库脚本
│   ├── init.sql       # 建表语句
│   ├── data.sql       # 测试数据
│   ├── triggers.sql   # 触发器与视图
│   └── procedures.sql # 存储过程
└── README.md
```

---

## 环境准备（第一次用的同学看这里）

你需要先安装以下软件，已经装过的跳过：

| 软件 | 版本要求 | 下载地址 |
|------|---------|---------|
| Node.js | >= 14 | https://nodejs.org/ |
| Python | >= 3.8 | https://python.org/ |
| MySQL | >= 8.0 | https://dev.mysql.com/downloads/installer/ |

> 安装 Python 时记得勾选 **Add to PATH**；安装 MySQL 时记住你设的 root 密码。

---

## 快速启动（照着做就行）

### 第一步：初始化数据库

打开 **CMD**（命令提示符），执行以下命令。把 `你的密码` 换成你的 MySQL root 密码：

```bash
mysql -u root -p你的密码 --default-character-set=utf8mb4 < D:/你的路径/database/init.sql
mysql -u root -p你的密码 --default-character-set=utf8mb4 takeout < D:/你的路径/database/data.sql
mysql -u root -p你的密码 --default-character-set=utf8mb4 takeout < D:/你的路径/database/triggers.sql
mysql -u root -p你的密码 --default-character-set=utf8mb4 takeout < D:/你的路径/database/procedures.sql
```

> ⚠️ `-p` 和密码之间**没有空格**！比如密码是 `root123` 就写 `-proot123`
>
> ⚠️ 把 `D:/你的路径/` 替换成你实际的项目路径

看到有 `ERROR` 说明失败，否则为成功。

### 第二步：修改数据库密码配置

用编辑器打开 `backend/cfg.py`，把第 12 行的密码改成你自己的MySQL密码：

```python
DB_PASSWORD = "你的MySQL密码"
```

### 第三步：启动后端

打开一个 **CMD 窗口**（这个窗口不要关，后端一直跑着）：

```bash
cd /d D:\你的路径\backend
pip install -r requirements.txt
python app.py
```

看到下面这样就是成功了：
```
==================================================
外卖平台管理系统 - 后端服务
运行地址: http://localhost:5000
==================================================
```

### 第四步：启动前端

**另开一个新的 CMD 窗口**（后端那个别关）：

```bash
cd /d D:\你的路径\frontend
npm install
npm run dev
```

> `npm install` 第一次会比较慢（几分钟），之后就不用再装了。

看到类似这样就是成功了：
```
  VITE v3.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### 第五步：打开浏览器

访问 http://localhost:5173/ ，用下面的账号登录。

---

## 测试账号

| 用户名 | 密码 | 角色 | 能做什么 |
|--------|------|------|---------|
| user1 | 123456 | 顾客 | 浏览菜品、下单、管理地址 |
| mer1 | 123456 | 商家 | 管理菜品、查看订单、指派配送 |
| del1 | 123456 | 送餐员 | 查看配送任务、确认送达 |
| admin | 123456 | 管理员 | 用户管理、查看所有数据 |

---

## 功能模块

- **用户管理**：注册、登录、角色区分（ISA继承结构）
- **菜品管理**：商家增删改菜品，顾客浏览下单
- **订单管理**：顾客下单/取消，商家指派配送，送餐员确认送达
- **地址管理**：顾客维护多个收货地址
- **配送管理**：自动派单，状态联动（数据库触发器实现）

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue3 + TypeScript + Arco Design Pro |
| 后端 | Flask + PyJWT + mysql-connector |
| 数据库 | MySQL 8.0 |

## 数据库设计亮点

- ISA 继承结构（User → Customer / Merchant / Deliveryman）
- 5 个触发器自动维护销量、配送状态联动
- 3 个视图简化复杂查询（订单详情、商家统计、送餐员统计）
- 1 个存储过程封装商家派单流程（状态校验 + 多表操作）
- 完整的约束体系（CHECK、外键、NOT NULL、级联删除）
