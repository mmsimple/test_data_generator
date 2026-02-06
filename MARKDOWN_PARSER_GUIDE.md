# Markdown Schema 解析功能使用指南

## 功能概述

新增的 `parse` 命令组允许你通过 AI 将 Markdown 格式的数据库表结构文档转换为 YAML 配置文件，然后用于生成测试数据。

## 安装依赖

```bash
pip install -r requirements.txt
```

新添加的依赖：
- `openai>=1.0.0` - OpenAI API 客户端
- `tenacity>=8.2.0` - 重试机制支持

## 配置 API 密钥

在使用前，需要设置 OpenAI API 密钥：

```bash
# 方式 1: 环境变量
export OPENAI_API_KEY="your-api-key-here"

# 方式 2: Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# 方式 3: 命令行参数
python -m src.cli parse schema docs/database.md -o config.yaml --api-key "your-api-key-here"
```

## 使用示例

### 1. 只解析 Markdown 为 YAML 配置

```bash
# 基本用法
python -m src.cli parse schema docs/database_schema.md -o config.yaml

# 带验证和详细输出
python -m src.cli parse schema docs/database_schema.md -o config.yaml --validate --verbose

# 使用不同的模型
python -m src.cli parse schema docs/database_schema.md -o config.yaml --model gpt-4o-mini

# 预览结果（不保存）
python -m src.cli parse schema docs/database_schema.md -o config.yaml --preview
```

### 2. 直接从 Markdown 生成测试数据（一步完成）

```bash
# 生成所有格式的测试数据
python -m src.cli parse data docs/database_schema.md

# 生成指定行数和格式
python -m src.cli parse data docs/database_schema.md --rows 50 --output-format csv

# 带验证和摘要
python -m src.cli parse data docs/database_schema.md --validate --summary
```

### 3. 使用生成的 YAML 配置

```bash
# 先解析
python -m src.cli parse schema docs/database_schema.md -o config.yaml

# 再生成测试数据
python -m src.cli generate config.yaml --rows 100 --output-format all
```

## 完整命令参数

### `parse schema` 命令

| 参数 | 说明 |
|------|------|
| `markdown_file` | Markdown 文档路径（必需） |
| `--output, -o` | 输出 YAML 配置文件路径（必需） |
| `--model` | 使用的 AI 模型：gpt-4o, gpt-4o-mini, gpt-4-turbo（默认：gpt-4o） |
| `--api-key` | OpenAI API 密钥（可从环境变量读取） |
| `--api-base` | OpenAI API base URL（可选，支持兼容的 API 服务） |
| `--timeout` | API 请求超时时间，单位秒（默认：120） |
| `--max-retries` | 最大重试次数（默认：3） |
| `--preview` | 预览生成的配置而不保存 |
| `--validate` | 解析后验证配置 |
| `--verbose, -v` | 显示详细输出 |

### `parse data` 命令

| 参数 | 说明 |
|------|------|
| `markdown_file` | Markdown 文档路径（必需） |
| `--rows` | 生成的行数（覆盖配置中的设置） |
| `--output-format` | 输出格式：csv, json, excel, sql, all（默认：all） |
| `--output-dir` | 输出目录 |
| `--model` | 使用的 AI 模型（默认：gpt-4o） |
| `--api-key` | OpenAI API 密钥 |
| `--api-base` | OpenAI API base URL |
| `--validate` | 生成后验证数据 |
| `--summary` | 显示数据摘要 |
| `--verbose, -v` | 显示详细输出 |

## Markdown 文档格式

Markdown 文档应该包含表格形式的表结构定义。示例格式：

```markdown
# 数据库表结构文档

## 用户表 (users)

| 字段名 | 类型 | 长度 | NULL | 主键 | 默认值 | 说明 |
|--------|------|------|------|------|--------|------|
| user_id | INT | - | NO | YES | - | 用户ID，自增 |
| username | VARCHAR | 50 | NO | NO | - | 用户名 |
| email | VARCHAR | 100 | NO | NO | - | 邮箱地址 |
| age | INT | - | NO | NO | - | 年龄 |

## 订单表 (orders)

| 字段名 | 类型 | 长度 | NULL | 主键 | 默认值 | 说明 |
|--------|------|------|------|------|--------|------|
| order_id | INT | - | NO | YES | - | 订单ID，自增 |
| user_id | INT | - | NO | NO | - | 用户ID，外键关联users.user_id |
| order_date | DATE | - | NO | NO | - | 订单日期 |
```

AI 会自动识别：
- 表名（从标题推断）
- 字段名、类型、约束
- 主键、外键关系
- 唯一约束
- 字段含义（从名称推断，如 email → email type）

## 支持的字段类型映射

| 数据库类型 | 生成器类型 | 说明 |
|-----------|-----------|------|
| INT, INTEGER | integer | 自增ID |
| VARCHAR, TEXT | string | 字符串 |
| DECIMAL, MONEY | money | 金额 |
| FLOAT, DOUBLE | float | 浮点数 |
| DATE | date | 日期 |
| DATETIME, TIMESTAMP | datetime | 日期时间 |
| BOOLEAN, BOOL | boolean | 布尔值 |
| ENUM | choice | 枚举 |
| UUID | uuid | UUID |
| EMAIL | email | 邮箱 |

## 使用兼容的 API 服务

如果使用其他兼容 OpenAI API 的服务（如 Azure OpenAI、国内大模型服务）：

```bash
# Azure OpenAI
python -m src.cli parse schema docs/database.md -o config.yaml \
  --api-base "https://your-resource.openai.azure.com" \
  --api-key "your-api-key"

# 其他兼容服务
python -m src.cli parse schema docs/database.md -o config.yaml \
  --api-base "https://api.your-provider.com/v1"
```

## 注意事项

1. **API 费用**：使用 OpenAI API 会产生费用，建议使用 `gpt-4o-mini` 以降低成本
2. **网络连接**：需要稳定的网络连接访问 OpenAI API
3. **Token 限制**：对于大型数据库，建议分批处理或使用 `gpt-4o`（更大的上下文窗口）
4. **验证结果**：生成的 YAML 配置建议使用 `--validate` 参数验证后再使用

## 故障排除

### 错误：API 密钥未设置

```
ValueError: API 密钥未设置。请设置 OPENAI_API_KEY 环境变量或通过 --api-key 参数提供。
```

解决：设置环境变量或使用 `--api-key` 参数。

### 错误：API 超时

解决：增加 `--timeout` 参数值（如 `--timeout 300`）。

### 错误：速率限制

系统会自动重试，也可以增加 `--max-retries` 参数。

## 实际使用示例

```bash
# 1. 设置环境变量
export OPENAI_API_KEY="sk-xxx"

# 2. 解析文档
python -m src.cli parse schema docs/database_schema.md \
  -o output/config.yaml \
  --validate \
  --verbose

# 3. 查看生成的配置
cat output/config.yaml

# 4. 生成测试数据
python -m src.cli generate output/config.yaml \
  --rows 100 \
  --output-format all \
  --summary

# 或者一步完成
python -m src.cli parse data docs/database_schema.md \
  --rows 100 \
  --output-format csv \
  --output-dir output/test_data
```
