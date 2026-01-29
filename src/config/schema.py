"""
配置模式验证模块
定义YAML配置文件的JSON Schema
"""

import json

CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Test Data Generator Configuration",
    "type": "object",
    "required": ["version"],
    "anyOf": [
        { "required": ["fields"] },
        { "required": ["tables"] }
    ],
    "properties": {
        "version": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+$",
            "description": "配置文件版本"
        },
        "description": {
            "type": "string",
            "description": "配置描述"
        },
        "config": {
            "type": "object",
            "properties": {
                "rows": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000000,
                    "default": 1000,
                    "description": "生成的数据行数"
                },
                "seed": {
                    "type": ["integer", "null"],
                    "default": None,
                    "description": "随机种子，确保可重复性"
                },
                "output_dir": {
                    "type": "string",
                    "default": "./output",
                    "description": "输出目录"
                }
            },
            "additionalProperties": False
        },
        "fields": {
            "type": "object",
            "minProperties":1,
            "description": "字段定义（单表模式）",
            "additionalProperties": {
                "type": "object",
                "required": ["type"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "string", "integer", "float", "boolean",
                            "date", "datetime", "choice", "uuid", "email",
                            "name", "address", "phone", "id_card", "timestamp", "ip_address", "money", "url"
                        ],
                        "description": "字段类型"
                    },
                    "config": {
                        "type": "object",
                        "description": "字段配置"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "字段元数据"
                    },
                    "dependencies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "字段依赖"
                    }
                }
            }
        },
        "tables": {
            "type": "object",
            "minProperties":1,
            "description": "表定义（多表模式）",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "config": {
                        "type": "object",
                        "properties": {
                            "rows": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 1000000,
                                "description": "生成的数据行数"
                            }
                        },
                        "additionalProperties": False
                    },
                    "fields": {
                        "type": "object",
                        "minProperties":1,
                        "description": "字段定义",
                        "additionalProperties": {
                            "type": "object",
                            "required": ["type"],
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": [
                                        "string", "integer", "float", "boolean",
                                        "date", "datetime", "choice", "uuid", "email",
                                        "name", "address", "phone", "id_card", "timestamp", "ip_address", "money", "url"
                                    ],
                                    "description": "字段类型"
                                },
                                "config": {
                                    "type": "object",
                                    "description": "字段配置"
                                },
                                "metadata": {
                                    "type": "object",
                                    "description": "字段元数据"
                                },
                                "dependencies": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "字段依赖"
                                }
                            }
                        }
                    }
                },
                "required": ["fields"]
            }
        },
        "outputs": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": False},
                        "config": {"type": "object"}
                    }
                },
                "csv": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": False},
                        "config": {"type": "object"}
                    }
                },
                "excel": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": False},
                        "config": {"type": "object"}
                    }
                },
                "json": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": False},
                        "config": {"type": "object"}
                    }
                }
            },
            "additionalProperties": False
        },
        "validations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["field", "rule"],
                "properties": {
                    "field": {"type": "string"},
                    "rule": {"type": "string"},
                    "message": {"type": "string"}
                }
            }
        },
        "relations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type"],
                "properties": {
                    "type": {"type": "string"},
                    "source_field": {"type": "string"},
                    "target_table": {"type": "string"},
                    "target_field": {"type": "string"},
                    "fields": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    }
}


def get_schema() -> dict:
    """获取配置模式"""
    return CONFIG_SCHEMA


def validate_schema(config: dict) -> bool:
    """简单的模式验证（完整验证使用jsonschema库）"""
    required_keys = {"version"}
    
    # 检查必需字段
    if not required_keys.issubset(config.keys()):
        return False
    
    # 检查版本格式
    import re
    version_pattern = r"^\d+\.\d+$"
    if not re.match(version_pattern, config["version"]):
        return False
    
    # 检查是否为多表配置
    if "tables" in config:
        # 检查tables格式
        if not isinstance(config["tables"], dict) or len(config["tables"]) == 0:
            return False
        
        # 检查每个表
        for table_name, table_config in config["tables"].items():
            # 检查表的fields格式
            if "fields" not in table_config:
                return False
            if not isinstance(table_config["fields"], dict) or len(table_config["fields"]) == 0:
                return False
            
            # 检查每个字段是否有type
            for field_name, field_config in table_config["fields"].items():
                if "type" not in field_config:
                    return False
    else:
        # 单表配置
        if "fields" not in config:
            return False
        # 检查fields格式
        if not isinstance(config["fields"], dict) or len(config["fields"]) == 0:
            return False
        
        # 检查每个字段是否有type
        for field_name, field_config in config["fields"].items():
            if "type" not in field_config:
                return False
    
    return True


def get_default_config() -> dict:
    """获取默认配置"""
    return {
        "version": "1.0",
        "description": "Test data generation configuration",
        "config": {
            "rows": 1000,
            "seed": None,
            "output_dir": "./output"
        },
        "fields": {},
        "outputs": {
            "sql": {"enabled": False, "config": {}},
            "csv": {"enabled": False, "config": {}},
            "excel": {"enabled": False, "config": {}},
            "json": {"enabled": False, "config": {}}
        },
        "validations": [],
        "relations": []
    }