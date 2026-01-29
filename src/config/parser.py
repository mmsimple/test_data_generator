"""
YAML配置解析器
"""

import yaml
import os
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError

from .schema import get_schema, validate_schema, get_default_config


class ConfigParser:
    """YAML配置解析器"""
    
    def __init__(self):
        self.schema = get_schema()
    
    def load_from_file(self, filepath: str) -> Dict[str, Any]:
        """
        从YAML文件加载配置
        
        Args:
            filepath: YAML配置文件路径
            
        Returns:
            解析后的配置字典
            
        Raises:
            FileNotFoundError: 文件不存在
            yaml.YAMLError: YAML解析错误
            ValidationError: 配置验证失败
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"配置文件不存在: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.load_from_string(content)
    
    def load_from_string(self, yaml_content: str) -> Dict[str, Any]:
        """
        从YAML字符串加载配置
        
        Args:
            yaml_content: YAML格式的字符串
            
        Returns:
            解析后的配置字典
            
        Raises:
            yaml.YAMLError: YAML解析错误
            ValidationError: 配置验证失败
        """
        config = yaml.safe_load(yaml_content)
        
        # 使用默认配置填充缺失字段
        default_config = get_default_config()
        self._merge_configs(config, default_config)
        
        # 验证配置
        self.validate(config)
        
        return config
    
    def _merge_configs(self, config: Dict[str, Any], default_config: Dict[str, Any]) -> None:
        """递归合并配置，用默认值填充缺失字段"""
        for key, default_value in default_config.items():
            # 如果用户配置中已经有tables，则不合并默认的fields
            if key == "fields" and "tables" in config:
                continue
            # 如果用户配置中已经有fields，则不合并默认的tables
            if key == "tables" and "fields" in config:
                continue
            if key not in config:
                config[key] = default_value
            elif isinstance(default_value, dict) and isinstance(config[key], dict):
                self._merge_configs(config[key], default_value)
    
    def validate(self, config: Dict[str, Any]) -> None:
        """
        验证配置是否符合模式
        
        Args:
            config: 要验证的配置字典
            
        Raises:
            ValidationError: 配置验证失败
        """
        # 首先进行基本验证
        if not validate_schema(config):
            raise ValidationError("配置格式不正确")
        
        # 使用JSON Schema进行详细验证
        try:
            validate(instance=config, schema=self.schema)
        except ValidationError as e:
            raise ValidationError(f"配置验证失败: {e.message}")
    
    def create_example_config(self) -> str:
        """
        创建示例配置文件
        
        Returns:
            示例配置的YAML字符串
        """
        example_config = {
            "version": "1.0",
            "description": "示例配置文件",
            "config": {
                "rows":66,
                "seed": 42,
                "output_dir": "./output"
            },
            "fields": {
                "id": {
                    "type": "integer",
                    "config": {
                        "start": 1,
                        "increment": 1
                    },
                    "metadata": {
                        "description": "ID字段",
                        "primary_key": True
                    }
                },
                "name": {
                    "type": "string",
                    "config": {
                        "generator": "name",
                        "min_length": 3,
                        "max_length": 50
                    },
                    "metadata": {
                        "description": "姓名"
                    }
                },
                "age": {
                    "type": "integer",
                    "config": {
                        "min": 18,
                        "max": 80,
                        "distribution": "uniform"
                    }
                }
            },
            "outputs": {
                "csv": {
                    "enabled": True,
                    "config": {
                        "output_file": "data.csv",
                        "include_header": True
                    }
                },
                "json": {
                    "enabled": True,
                    "config": {
                        "output_file": "data.json",
                        "indent": 2
                    }
                }
            }
        }
        
        return yaml.dump(example_config, default_flow_style=False, allow_unicode=True, sort_keys=False)


def parse_config(filepath: str) -> Dict[str, Any]:
    """
    解析配置文件的便捷函数
    
    Args:
        filepath: 配置文件路径
        
    Returns:
        解析后的配置字典
    """
    parser = ConfigParser()
    return parser.load_from_file(filepath)