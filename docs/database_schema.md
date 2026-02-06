# 数据库表结构文档

## 用户表 (users)

| 字段名 | 类型 | 长度 | NULL | 主键 | 默认值 | 说明 |
|--------|------|------|------|------|--------|------|
| user_id | INT | - | NO | YES | - | 用户ID，自增 |
| username | VARCHAR | 50 | NO | NO | - | 用户名 |
| full_name | VARCHAR | 100 | NO | NO | - | 姓名 |
| email | VARCHAR | 100 | NO | NO | - | 邮箱地址 |
| age | INT | - | NO | NO | - | 年龄 |
| gender | ENUM | - | NO | NO | - | 性别 (M/F) |
| phone | VARCHAR | 20 | YES | NO | - | 手机号 |
| is_active | BOOLEAN | - | YES | NO | true | 是否激活 |
| created_at | TIMESTAMP | - | NO | NO | CURRENT_TIMESTAMP | 创建时间 |

## 订单表 (orders)

| 字段名 | 类型 | 长度 | NULL | 主键 | 默认值 | 说明 |
|--------|------|------|------|------|--------|------|
| order_id | INT | - | NO | YES | - | 订单ID，自增 |
| user_id | INT | - | NO | NO | - | 用户ID，外键关联users.user_id |
| order_date | DATE | - | NO | NO | - | 订单日期 |
| total_amount | DECIMAL | (10,2) | NO | NO | - | 订单总金额 |
| status | ENUM | - | NO | NO | - | 订单状态 |

## 订单项表 (order_items)

| 字段名 | 类型 | 长度 | NULL | 主键 | 默认值 | 说明 |
|--------|------|------|------|------|--------|------|
| order_item_id | INT | - | NO | YES | - | 订单项ID，自增 |
| order_id | INT | - | NO | NO | - | 订单ID，外键关联orders.order_id |
| product_name | VARCHAR | 200 | NO | NO | - | 产品名称 |
| quantity | INT | - | NO | NO | - | 产品数量 |
| unit_price | DECIMAL | (10,2) | NO | NO | - | 单价 |
| subtotal | DECIMAL | (10,2) | NO | NO | - | 小计金额 |
