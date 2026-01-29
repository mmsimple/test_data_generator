# 测试数据生成器

基于YAML配置的测试数据生成工具，支持多种数据格式（CSV、JSON、Excel、SQL）和数据分布（正态分布、均匀分布等）。

## 功能特性

- 🎯 **灵活的YAML配置**：通过YAML文件定义数据结构和生成规则
- 📊 **多种数据分布**：支持正态分布、均匀分布、顺序生成等
- 🔧 **丰富的字段类型**：字符串、整数、浮点数、布尔值、日期、UUID、邮箱、姓名、地址、手机号等
- 📁 **多格式输出**：CSV、JSON、Excel、SQL插入语句
- ✅ **数据验证**：支持自定义验证规则
- 🎨 **模板系统**：预置多种场景模板（用户、产品、订单、员工数据）
- 🚀 **命令行工具**：提供便捷的CLI界面

## 安装

### 从源码安装

```bash
git clone <repository-url>
cd test-data-generator
pip install -e .
```

### 依赖

- Python >= 3.8
- PyYAML >= 6.0
- pandas >= 2.0.0
- openpyxl >= 3.1.0
- Faker >= 20.0.0
- click >= 8.1.0
- jsonschema >= 4.20.0

## 快速开始

### 1. 生成配置模板

```bash
# 生成用户数据模板
python -m src.cli template user_data -o user_config.yaml
```

### 2. 修改配置文件

编辑生成的`user_config.yaml`文件，根据需要调整字段配置：

```yaml
version: "1.0"
description: "用户测试数据模板"
config:
  rows: 100      # 生成100行数据
  seed: 42       # 随机种子，确保可重复性
  output_dir: "./output"

fields:
  user_id:
    type: "integer"
    config:
      start: 1
      increment: 1
    metadata:
      description: "用户ID"
      primary_key: true

  username:
    type: "string"
    config:
      generator: "random_string"
      min_length: 5
      max_length: 20
      prefix: "user_"
    metadata:
      description: "用户名"
      unique: true

  age:
    type: "integer"
    config:
      min: 18
      max: 80
      distribution: "normal"  # 正态分布
      mean: 35
      std_dev: 10
```

### 3. 生成数据

```bash
# 生成所有格式的数据
python -m src.cli generate user_config.yaml

# 只生成CSV格式
python -m src.cli generate user_config.yaml --output-format csv

# 生成50行数据并验证
python -m src.cli generate user_config.yaml --rows 50 --validate --summary

# 预览生成的数据
python -m src.cli preview user_config.yaml --rows 5
```

## 配置文件详解

### 基本结构

```yaml
version: "1.0"
description: "配置描述"

# 数据生成配置
config:
  rows: 1000
  seed: 42          # 随机种子，null表示不使用
  output_dir: "./output"

# 字段定义
fields:
  field_name:
    type: "字段类型"  # string, integer, float, boolean, date, choice, uuid, email, name, phone等
    config:          # 字段特定配置
      # 不同类型字段有不同的配置
    metadata:        # 元数据（可选）
      description: "字段描述"
    dependencies:    # 字段依赖（可选）
      - "other_field"

# 输出格式配置
outputs:
  csv:
    enabled: true
    config:
      output_file: "data.csv"
      include_header: true
      delimiter: ","
  
  json:
    enabled: true
    config:
      output_file: "data.json"
      indent: 2
      array_format: true

# 数据验证规则（可选）
validations:
  - field: "age"
    rule: ">= 18"
    message: "年龄必须大于等于18岁"

  - field: "balance"
    rule: ">= 0"
    message: "账户余额不能为负数"

# 数据关系定义（可选）
relations:
  - type: "unique_constraint"
    fields: ["username", "email"]
```

### 支持的字段类型

#### 基础字段
- **string**: 字符串字段
- **integer**: 整数字段（支持正态分布、均匀分布、顺序生成）
- **float**: 浮点数字段
- **boolean**: 布尔字段
- **date**: 日期字段
- **datetime**: 日期时间字段
- **choice**: 选择字段（带权重）
- **uuid**: UUID字段
- **email**: 邮箱字段

#### 扩展字段
- **name**: 姓名字段（支持性别选择）
- **address**: 地址字段
- **phone**: 手机号字段（支持运营商选择）
- **id_card**: 身份证号码字段
- **timestamp**: 时间戳字段
- **ip_address**: IP地址字段
- **money**: 金额字段
- **url**: URL字段

### 字段配置示例

#### 整数字段（正态分布）
```yaml
age:
  type: "integer"
  config:
    min: 18
    max: 80
    distribution: "normal"
    mean: 35
    std_dev: 10
```

#### 浮点数字段（均匀分布）
```yaml
price:
  type: "float"
  config:
    min: 10.0
    max: 1000.0
    precision: 2
```

#### 选择字段（带权重）
```yaml
gender:
  type: "choice"
  config:
    choices: ["M", "F"]
    weights: [0.5, 0.5]
```

#### 日期字段
```yaml
birth_date:
  type: "date"
  config:
    start_date: "1990-01-01"
    end_date: "2000-12-31"
    format: "%Y-%m-%d"
```

#### 邮箱字段（依赖其他字段）
```yaml
email:
  type: "email"
  config:
    domain: "example.com"
  dependencies:
    - "username"
```

## 编程接口

### 基本使用

```python
from src.generator import DataGenerator

# 从配置文件创建生成器
generator = DataGenerator('config.yaml')

# 生成数据
data = generator.generate(rows=100)

# 导出为不同格式
csv_file = generator.to_csv()
json_file = generator.to_json()
excel_file = generator.to_excel()
sql_file = generator.to_sql()

# 获取数据摘要
summary = generator.get_summary()

# 验证数据
validation_results = generator.validate()
```

### 使用配置字典

```python
config = {
    'version': '1.0',
    'config': {
        'rows': 50
    },
    'fields': {
        'id': {
            'type': 'integer',
            'config': {'start': 1, 'increment': 1}
        },
        'name': {
            'type': 'string',
            'config': {'min_length': 5, 'max_length': 10}
        }
    }
}

generator = DataGenerator(config_dict=config)
data = generator.generate()
```

### 使用模板生成器

```python
from src.template_generator import TemplateGenerator

# 获取所有模板
templates = TemplateGenerator.get_all_templates()

# 保存用户数据模板
TemplateGenerator.save_template('user_data', 'user_config.yaml')

# 直接使用模板
yaml_content = TemplateGenerator.create_user_data_template()
```

## 命令行工具

### 主要命令

```bash
# 生成数据
python -m src.cli generate <config_file> [options]

# 生成配置模板
python -m src.cli template <template_name> [-o output_file]

# 验证配置文件
python -m src.cli validate <config_file>

# 预览数据
python -m src.cli preview <config_file> [--rows 10]

# 列出所有模板
python -m src.cli list_templates
```

### 命令行选项

```bash
# 生成命令选项
--rows 100                     # 生成的行数
--output-format csv|json|excel|sql|all  # 输出格式
--output-dir ./my_output      # 输出目录
--validate                    # 生成后验证数据
--summary                     # 显示数据摘要

# 模板命令选项
-o, --output config.yaml      # 输出文件路径
```

## 完整示例

### 用户数据生成示例

1. 创建用户数据配置文件：

```yaml
version: "1.0"
description: "生成用户测试数据"

config:
  rows: 1000
  seed: 42
  output_dir: "./output"

fields:
  user_id:
    type: "integer"
    config:
      start: 1
      increment: 1
    metadata:
      description: "用户ID"
      primary_key: true

  username:
    type: "string"
    config:
      generator: "random_string"
      min_length: 5
      max_length: 20
    metadata:
      description: "用户名"
      unique: true

  full_name:
    type: "name"
    config:
      gender: "both"
    metadata:
      description: "姓名"

  email:
    type: "email"
    config:
      domain: "company.com"
    dependencies: ["username"]

  age:
    type: "integer"
    config:
      min: 18
      max: 65
      distribution: "normal"
      mean: 35
      std_dev: 10

  registration_date:
    type: "date"
    config:
      start_date: "2023-01-01"
      end_date: "2024-12-31"
      format: "%Y-%m-%d"

outputs:
  csv:
    enabled: true
    config:
      output_file: "users.csv"
      include_header: true

  sql:
    enabled: true
    config:
      table_name: "users"
      dialect: "postgresql"
      output_file: "users.sql"
```

2. 运行生成器：

```bash
python -m src.cli generate user_config.yaml --validate --summary
```

### 产品数据生成示例

```yaml
version: "1.0"
description: "产品目录数据"

config:
  rows: 500
  output_dir: "./products"

fields:
  product_id:
    type: "uuid"
    config:
      version: 4

  product_name:
    type: "string"
    config:
      generator: "random_string"
      min_length: 10
      max_length: 50

  category:
    type: "choice"
    config:
      choices: ["Electronics", "Clothing", "Books", "Home", "Sports"]
      weights: [0.3, 0.25, 0.2, 0.15, 0.1]

  price:
    type: "money"
    config:
      min: 10.0
      max: 1000.0
      precision: 2
      distribution: "normal"
      mean: 150.0
      std_dev: 100.0

  stock_quantity:
    type: "integer"
    config:
      min: 0
      max: 1000
      distribution: "normal"
      mean: 200
      std_dev: 100

outputs:
  excel:
    enabled: true
    config:
      output_file: "products.xlsx"
      sheet_name: "Products"
      auto_filter: true
```

## 高级功能

### 数据验证

```yaml
validations:
  - field: "age"
    rule: ">= 18"
    message: "年龄必须大于等于18岁"

  - field: "price"
    rule: "> 0"
    message: "价格必须大于0"

  - field: "username"
    rule: "length >= 5 and length <= 20"
    message: "用户名长度必须在5-20个字符之间"
```

支持的验证规则：
- `>= value` - 大于等于
- `<= value` - 小于等于
- `> value` - 大于
- `< value` - 小于
- `length >= value` - 长度大于等于
- `length <= value` - 长度小于等于

### 字段依赖

```yaml
fields:
  first_name:
    type: "string"
    config:
      generator: "random_string"

  email:
    type: "email"
    config:
      domain: "example.com"
    dependencies: ["first_name"]  # 使用first_name生成邮箱
```

### 随机种子

设置随机种子确保生成结果可重复：

```yaml
config:
  rows: 100
  seed: 42  # 固定种子，每次生成相同的数据
```

## 常见问题

### 1. 如何扩展新的字段类型？

创建新的字段类并注册到字段映射中：

```python
from src.fields.base import Field

class CustomField(Field):
    def generate(self, row_data=None):
        # 实现生成逻辑
        pass
    
    def validate(self, value):
        # 实现验证逻辑
        pass

# 注册到字段映射
from src.fields.base import FIELD_TYPE_MAPPING
FIELD_TYPE_MAPPING['custom'] = CustomField
```

### 2. 如何生成特定语言的数据？

使用Faker库扩展：

```python
from faker import Faker

fake = Faker('zh_CN')
name = fake.name()
address = fake.address()
```

### 3. 如何生成关联数据？

通过字段依赖实现关联：

```yaml
fields:
  user_id:
    type: "integer"
    config:
      start: 1
      increment: 1

  order_id:
    type: "string"
    config:
      generator: "random_string"
      prefix: "ORD_"

  order_user_id:
    type: "integer"
    config:
      min: 1
      max: 100  # 假设有100个用户
    metadata:
      description: "关联到user_id"
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License