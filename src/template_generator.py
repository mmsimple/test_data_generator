"""
YAML模板生成器
用于生成各种场景的示例配置文件
"""
import yaml
from typing import Dict, Any, List


class TemplateGenerator:
    """YAML模板生成器"""
    
    @staticmethod
    def create_user_data_template() -> str:
        """创建用户数据模板"""
        template = {
            "version": "1.0",
            "description": "用户测试数据模板",
            "config": {
                "rows": 100,
                "seed": 42,
                "output_dir": "./output"
            },
            "fields": {
                "user_id": {
                    "type": "integer",
                    "config": {
                        "start": 1,
                        "increment": 1
                    },
                    "metadata": {
                        "description": "用户ID",
                        "primary_key": True,
                        "nullable": False
                    }
                },
                "username": {
                    "type": "string",
                    "config": {
                        "generator": "random_string",
                        "min_length": 5,
                        "max_length": 20,
                        "prefix": "user_"
                    },
                    "metadata": {
                        "description": "用户名",
                        "unique": True
                    }
                },
                "name": {
                    "type": "name",
                    "config": {
                        "gender": "both",
                        "locale": "zh_CN"
                    },
                    "metadata": {
                        "description": "姓名"
                    }
                },
                "email": {
                    "type": "email",
                    "config": {
                        "domain": "example.com"
                    },
                    "dependencies": ["username"],
                    "metadata": {
                        "description": "邮箱地址"
                    }
                },
                "age": {
                    "type": "integer",
                    "config": {
                        "min": 18,
                        "max": 80,
                        "distribution": "normal",
                        "mean": 35,
                        "std_dev": 10
                    },
                    "metadata": {
                        "description": "年龄"
                    }
                },
                "gender": {
                    "type": "choice",
                    "config": {
                        "choices": ["M", "F"],
                        "weights": [0.5, 0.5]
                    },
                    "metadata": {
                        "description": "性别"
                    }
                },
                "phone": {
                    "type": "phone",
                    "config": {
                        "operator": None
                    },
                    "metadata": {
                        "description": "手机号码"
                    }
                },
                "registration_date": {
                    "type": "date",
                    "config": {
                        "start_date": "2023-01-01",
                        "end_date": "2024-12-31",
                        "format": "%Y-%m-%d"
                    },
                    "metadata": {
                        "description": "注册日期"
                    }
                },
                "balance": {
                    "type": "money",
                    "config": {
                        "min": 0.0,
                        "max": 10000.0,
                        "precision": 2,
                        "currency": "CNY",
                        "distribution": "normal",
                        "mean": 5000.0,
                        "std_dev": 1200.0
                    },
                    "metadata": {
                        "description": "账户余额"
                    }
                },
                "is_active": {
                    "type": "boolean",
                    "config": {
                        "true_probability": 0.8
                    },
                    "metadata": {
                        "description": "是否激活"
                    }
                }
            },
            "outputs": {
                "csv": {
                    "enabled": True,
                    "config": {
                        "output_file": "users.csv",
                        "include_header": True,
                        "delimiter": ","
                    }
                },
                "json": {
                    "enabled": True,
                    "config": {
                        "output_file": "users.json",
                        "indent": 2,
                        "array_format": True
                    }
                },
                "excel": {
                    "enabled": True,
                    "config": {
                        "output_file": "users.xlsx",
                        "sheet_name": "Users",
                        "auto_filter": True
                    }
                },
                "sql": {
                    "enabled": True,
                    "config": {
                        "table_name": "users",
                        "dialect": "postgresql",
                        "output_file": "users.sql",
                        "batch_size": 100
                    }
                }
            },
            "validations": [
                {
                    "field": "age",
                    "rule": ">= 18",
                    "message": "年龄必须大于等于18岁"
                },
                {
                    "field": "balance",
                    "rule": ">= 0",
                    "message": "账户余额不能为负数"
                },
                {
                    "field": "username",
                    "rule": "length >= 5 and length <= 20",
                    "message": "用户名长度必须在5-20个字符之间"
                }
            ],
            "relations": [
                {
                    "type": "unique_constraint",
                    "fields": ["username", "email"]
                }
            ]
        }
        
        return yaml.dump(template, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    @staticmethod
    def create_product_data_template() -> str:
        """创建产品数据模板"""
        template = {
            "version": "1.0",
            "description": "产品测试数据模板",
            "config": {
                "rows": 50,
                "seed": 123,
                "output_dir": "./output"
            },
            "fields": {
                "product_id": {
                    "type": "uuid",
                    "config": {
                        "version": 4
                    },
                    "metadata": {
                        "description": "产品ID",
                        "primary_key": True
                    }
                },
                "product_name": {
                    "type": "string",
                    "config": {
                        "generator": "random_string",
                        "min_length": 10,
                        "max_length": 100
                    },
                    "metadata": {
                        "description": "产品名称"
                    }
                },
                "category": {
                    "type": "choice",
                    "config": {
                        "choices": ["电子产品", "服装", "食品", "图书", "家居", "美妆"],
                        "weights": [0.3, 0.2, 0.15, 0.15, 0.1, 0.1]
                    },
                    "metadata": {
                        "description": "产品类别"
                    }
                },
                "price": {
                    "type": "money",
                    "config": {
                        "min": 10.0,
                        "max": 5000.0,
                        "precision": 2,
                        "distribution": "normal",
                        "mean": 500.0,
                        "std_dev": 300.0
                    },
                    "metadata": {
                        "description": "价格"
                    }
                },
                "stock_quantity": {
                    "type": "integer",
                    "config": {
                        "min": 0,
                        "max": 1000,
                        "distribution": "normal",
                        "mean": 200,
                        "std_dev": 100
                    },
                    "metadata": {
                        "description": "库存数量"
                    }
                },
                "created_at": {
                    "type": "timestamp",
                    "config": {
                        "start_timestamp": 1672531200,
                        "end_timestamp": 1704067200,
                        "format": "datetime_string"
                    },
                    "metadata": {
                        "description": "创建时间"
                    }
                },
                "is_available": {
                    "type": "boolean",
                    "config": {
                        "true_probability": 0.9
                    },
                    "metadata": {
                        "description": "是否可用"
                    }
                },
                "rating": {
                    "type": "float",
                    "config": {
                        "min": 1.0,
                        "max": 5.0,
                        "precision": 1,
                        "distribution": "normal",
                        "mean": 4.2,
                        "std_dev": 0.5
                    },
                    "metadata": {
                        "description": "评分"
                    }
                }
            },
            "outputs": {
                "csv": {
                    "enabled": True,
                    "config": {
                        "output_file": "products.csv",
                        "include_header": True
                    }
                },
                "json": {
                    "enabled": True,
                    "config": {
                        "output_file": "products.json",
                        "indent": 2
                    }
                }
            },
            "validations": [
                {
                    "field": "price",
                    "rule": ">= 0",
                    "message": "价格不能为负数"
                },
                {
                    "field": "stock_quantity",
                    "rule": ">= 0",
                    "message": "库存数量不能为负数"
                },
                {
                    "field": "rating",
                    "rule": ">= 1 and <= 5",
                    "message": "评分必须在1-5之间"
                }
            ]
        }
        
        return yaml.dump(template, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    @staticmethod
    def create_order_data_template() -> str:
        """创建订单数据模板"""
        template = {
            "version": "1.0",
            "description": "订单测试数据模板",
            "config": {
                "rows": 200,
                "seed": 456,
                "output_dir": "./output"
            },
            "fields": {
                "order_id": {
                    "type": "string",
                    "config": {
                        "generator": "random_string",
                        "min_length": 10,
                        "max_length": 20,
                        "prefix": "ORD_"
                    },
                    "metadata": {
                        "description": "订单号",
                        "primary_key": True
                    }
                },
                "customer_id": {
                    "type": "integer",
                    "config": {
                        "min": 1,
                        "max": 100
                    },
                    "metadata": {
                        "description": "客户ID"
                    }
                },
                "order_date": {
                    "type": "date",
                    "config": {
                        "start_date": "2024-01-01",
                        "end_date": "2024-12-31",
                        "format": "%Y-%m-%d"
                    },
                    "metadata": {
                        "description": "订单日期"
                    }
                },
                "total_amount": {
                    "type": "money",
                    "config": {
                        "min": 50.0,
                        "max": 5000.0,
                        "precision": 2,
                        "distribution": "normal",
                        "mean": 800.0,
                        "std_dev": 500.0
                    },
                    "metadata": {
                        "description": "总金额"
                    }
                },
                "status": {
                    "type": "choice",
                    "config": {
                        "choices": ["pending", "processing", "shipped", "delivered", "cancelled"],
                        "weights": [0.1, 0.2, 0.3, 0.35, 0.05]
                    },
                    "metadata": {
                        "description": "订单状态"
                    }
                },
                "payment_method": {
                    "type": "choice",
                    "config": {
                        "choices": ["credit_card", "debit_card", "paypal", "alipay", "wechat_pay"],
                        "weights": [0.3, 0.2, 0.2, 0.15, 0.15]
                    },
                    "metadata": {
                        "description": "支付方式"
                    }
                },
                "shipping_address": {
                    "type": "address",
                    "config": {
                        "include_detail": True,
                        "locale": "zh_CN"
                    },
                    "metadata": {
                        "description": "收货地址"
                    }
                },
                "notes": {
                    "type": "string",
                    "config": {
                        "generator": "random_string",
                        "min_length": 0,
                        "max_length": 200
                    },
                    "metadata": {
                        "description": "备注",
                        "nullable": True
                    }
                }
            },
            "outputs": {
                "csv": {
                    "enabled": True,
                    "config": {
                        "output_file": "orders.csv",
                        "include_header": True
                    }
                },
                "sql": {
                    "enabled": True,
                    "config": {
                        "table_name": "orders",
                        "dialect": "mysql",
                        "output_file": "orders.sql"
                    }
                }
            },
            "validations": [
                {
                    "field": "total_amount",
                    "rule": ">= 0",
                    "message": "总金额不能为负数"
                },
                {
                    "field": "customer_id",
                    "rule": ">= 1",
                    "message": "客户ID必须大于0"
                }
            ]
        }
        
        return yaml.dump(template, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    @staticmethod
    def create_employee_data_template() -> str:
        """创建员工数据模板"""
        template = {
            "version": "1.0",
            "description": "员工测试数据模板",
            "config": {
                "rows": 30,
                "seed": 789,
                "output_dir": "./output"
            },
            "fields": {
                "employee_id": {
                    "type": "string",
                    "config": {
                        "generator": "random_string",
                        "min_length": 6,
                        "max_length": 8,
                        "prefix": "EMP"
                    },
                    "metadata": {
                        "description": "员工ID",
                        "primary_key": True
                    }
                },
                "full_name": {
                    "type": "name",
                    "config": {
                        "gender": "both"
                    },
                    "metadata": {
                        "description": "姓名"
                    }
                },
                "department": {
                    "type": "choice",
                    "config": {
                        "choices": ["技术部", "市场部", "销售部", "人力资源部", "财务部", "行政部"],
                        "weights": [0.25, 0.15, 0.20, 0.15, 0.15, 0.10]
                    },
                    "metadata": {
                        "description": "部门"
                    }
                },
                "position": {
                    "type": "choice",
                    "config": {
                        "choices": ["工程师", "经理", "主管", "专员", "助理", "总监"],
                        "weights": [0.35, 0.15, 0.15, 0.20, 0.10, 0.05]
                    },
                    "metadata": {
                        "description": "职位"
                    }
                },
                "salary": {
                    "type": "money",
                    "config": {
                        "min": 3000.0,
                        "max": 30000.0,
                        "precision": 0,
                        "distribution": "normal",
                        "mean": 12000.0,
                        "std_dev": 5000.0
                    },
                    "metadata": {
                        "description": "薪资"
                    }
                },
                "hire_date": {
                    "type": "date",
                    "config": {
                        "start_date": "2018-01-01",
                        "end_date": "2024-01-01",
                        "format": "%Y-%m-%d"
                    },
                    "metadata": {
                        "description": "入职日期"
                    }
                },
                "email": {
                    "type": "email",
                    "config": {
                        "domain": "company.com"
                    },
                    "dependencies": ["full_name"],
                    "metadata": {
                        "description": "公司邮箱"
                    }
                },
                "phone": {
                    "type": "phone",
                    "config": {
                        "operator": None
                    },
                    "metadata": {
                        "description": "联系电话"
                    }
                },
                "is_full_time": {
                    "type": "boolean",
                    "config": {
                        "true_probability": 0.85
                    },
                    "metadata": {
                        "description": "是否全职"
                    }
                }
            },
            "outputs": {
                "excel": {
                    "enabled": True,
                    "config": {
                        "output_file": "employees.xlsx",
                        "sheet_name": "Employees",
                        "auto_filter": True
                    }
                },
                "json": {
                    "enabled": True,
                    "config": {
                        "output_file": "employees.json",
                        "indent": 2
                    }
                }
            },
            "validations": [
                {
                    "field": "salary",
                    "rule": ">= 3000",
                    "message": "薪资必须大于等于3000"
                },
                {
                    "field": "full_name",
                    "rule": "length >= 2 and length <= 4",
                    "message": "姓名长度必须在2-4个字符之间"
                }
            ]
        }
        
        return yaml.dump(template, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    @staticmethod
    def get_all_templates() -> Dict[str, str]:
        """获取所有模板"""
        return {
            "user_data": TemplateGenerator.create_user_data_template(),
            "product_data": TemplateGenerator.create_product_data_template(),
            "order_data": TemplateGenerator.create_order_data_template(),
            "employee_data": TemplateGenerator.create_employee_data_template()
        }
    
    @staticmethod
    def save_template(template_name: str, filepath: str) -> None:
        """
        保存模板到文件
        
        Args:
            template_name: 模板名称
            filepath: 文件路径
        """
        templates = TemplateGenerator.get_all_templates()
        
        if template_name not in templates:
            raise ValueError(f"未知的模板: {template_name}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(templates[template_name])