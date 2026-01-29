"""
基础字段测试用例
"""
import pytest
import tempfile
import os
import yaml
from pathlib import Path

from src.fields.base import create_field, StringField, IntegerField, FloatField, BooleanField, DateField, ChoiceField, EmailField, UUIDField
from src.generator import DataGenerator
from src.config.parser import ConfigParser


class TestBaseFields:
    """基础字段测试"""
    
    def test_string_field_generation(self):
        """测试字符串字段生成"""
        config = {
            'type': 'string',
            'config': {
                'min_length': 5,
                'max_length': 10
            }
        }
        
        field = create_field('test_string', config)
        value = field.generate()
        
        assert isinstance(value, str)
        assert 5 <= len(value) <= 10
    
    def test_integer_field_uniform_distribution(self):
        """测试整数字段均匀分布"""
        config = {
            'type': 'integer',
            'config': {
                'min': 1,
                'max': 10,
                'distribution': 'uniform'
            }
        }
        
        field = create_field('test_int', config)
        values = [field.generate() for _ in range(100)]
        
        assert all(1 <= v <= 10 for v in values)
        assert min(values) >= 1
        assert max(values) <= 10
    
    def test_integer_field_normal_distribution(self):
        """测试整数字段正态分布"""
        config = {
            'type': 'integer',
            'config': {
                'min': 1,
                'max': 100,
                'distribution': 'normal',
                'mean': 50,
                'std_dev': 10
            }
        }
        
        field = create_field('test_int_normal', config)
        values = [field.generate() for _ in range(100)]
        
        assert all(1 <= v <= 100 for v in values)
    
    def test_integer_field_sequential(self):
        """测试整数字段顺序生成"""
        config = {
            'type': 'integer',
            'config': {
                'start': 1,
                'increment': 2,
                'distribution': 'sequential'
            }
        }
        
        field = create_field('test_int_seq', config)
        values = [field.generate() for _ in range(5)]
        
        assert values == [1, 3, 5, 7, 9]
    
    def test_float_field_generation(self):
        """测试浮点数字段生成"""
        config = {
            'type': 'float',
            'config': {
                'min': 0.0,
                'max': 1.0,
                'precision': 2
            }
        }
        
        field = create_field('test_float', config)
        value = field.generate()
        
        assert isinstance(value, float)
        assert 0.0 <= value <= 1.0
    
    def test_boolean_field_generation(self):
        """测试布尔字段生成"""
        config = {
            'type': 'boolean',
            'config': {
                'true_probability': 0.3
            }
        }
        
        field = create_field('test_bool', config)
        values = [field.generate() for _ in range(100)]
        
        true_count = sum(values)
        false_count = len(values) - true_count
        
        # 允许一定的误差范围
        assert 20 <= true_count <= 40  # 30% of 100 ±10
    
    def test_date_field_generation(self):
        """测试日期字段生成"""
        config = {
            'type': 'date',
            'config': {
                'start_date': '2023-01-01',
                'end_date': '2023-12-31',
                'format': '%Y-%m-%d'
            }
        }
        
        field = create_field('test_date', config)
        value = field.generate()
        
        assert isinstance(value, str)
        assert value.startswith('2023-')
    
    def test_choice_field_generation(self):
        """测试选择字段生成"""
        config = {
            'type': 'choice',
            'config': {
                'choices': ['A', 'B', 'C'],
                'weights': [0.5, 0.3, 0.2]
            }
        }
        
        field = create_field('test_choice', config)
        value = field.generate()
        
        assert value in ['A', 'B', 'C']
    
    def test_email_field_generation(self):
        """测试邮箱字段生成"""
        config = {
            'type': 'email',
            'config': {
                'domain': 'test.com'
            }
        }
        
        field = create_field('test_email', config)
        value = field.generate()
        
        assert isinstance(value, str)
        assert '@test.com' in value
        assert field.validate(value) == True
    
    def test_uuid_field_generation(self):
        """测试UUID字段生成"""
        config = {
            'type': 'uuid',
            'config': {
                'version': 4
            }
        }
        
        field = create_field('test_uuid', config)
        value = field.generate()
        
        assert isinstance(value, str)
        assert len(value) == 36  # UUID长度
        assert field.validate(value) == True
    
    def test_field_validation(self):
        """测试字段验证"""
        config = {
            'type': 'integer',
            'config': {
                'min': 10,
                'max': 20
            }
        }
        
        field = create_field('test_validation', config)
        
        assert field.validate(15) == True
        assert field.validate(5) == False
        assert field.validate(25) == False
        assert field.validate("15") == False
    
    def test_field_dependencies(self):
        """测试字段依赖"""
        config = {
            'type': 'string',
            'config': {
                'generator': 'random_string',
                'min_length': 5,
                'max_length': 10
            },
            'dependencies': ['other_field']
        }
        
        field = create_field('test_dependent', config)
        
        # 生成时应该可以接收依赖数据
        row_data = {'other_field': 'test_value'}
        value = field.generate(row_data)
        
        assert isinstance(value, str)
        assert 5 <= len(value) <= 10


class TestExtendedFields:
    """扩展字段测试"""
    
    def test_name_field_generation(self):
        """测试姓名字段生成"""
        config = {
            'type': 'name',
            'config': {
                'gender': 'both',
                'locale': 'zh_CN'
            }
        }
        
        try:
            field = create_field('test_name', config)
            value = field.generate()
            
            assert isinstance(value, str)
            assert 2 <= len(value) <= 4
            # 中文姓名验证
            import re
            assert re.match(r'^[\u4e00-\u9fa5]+$', value)
        except ValueError:
            # 如果扩展字段未加载，跳过测试
            pytest.skip("扩展字段未加载")
    
    def test_phone_field_generation(self):
        """测试手机号字段生成"""
        config = {
            'type': 'phone',
            'config': {
                'operator': None
            }
        }
        
        try:
            field = create_field('test_phone', config)
            value = field.generate()
            
            assert isinstance(value, str)
            assert len(value) == 11
            # 手机号格式验证
            import re
            assert re.match(r'^1[3-9]\d{9}$', value)
        except ValueError:
            pytest.skip("扩展字段未加载")
    
    def test_address_field_generation(self):
        """测试地址字段生成"""
        config = {
            'type': 'address',
            'config': {
                'include_detail': True,
                'locale': 'zh_CN'
            }
        }
        
        try:
            field = create_field('test_address', config)
            value = field.generate()
            
            assert isinstance(value, str)
            assert len(value) >= 6
        except ValueError:
            pytest.skip("扩展字段未加载")


class TestConfigParser:
    """配置解析器测试"""
    
    def test_load_from_string(self):
        """测试从字符串加载配置"""
        yaml_content = """
        version: "1.0"
        description: "测试配置"
        config:
          rows: 10
          seed: 42
          output_dir: "./test_output"
        fields:
          id:
            type: "integer"
            config:
              start: 1
              increment: 1
        outputs:
          csv:
            enabled: true
            config:
              output_file: "test.csv"
        """
        
        parser = ConfigParser()
        config = parser.load_from_string(yaml_content)
        
        assert config['version'] == '1.0'
        assert config['config']['rows'] == 10
        assert 'id' in config['fields']
        assert config['fields']['id']['type'] == 'integer'
        assert config['outputs']['csv']['enabled'] == True
    
    def test_create_example_config(self):
        """测试创建示例配置"""
        parser = ConfigParser()
        example_config = parser.create_example_config()
        
        # 验证生成的YAML是否有效
        config = yaml.safe_load(example_config)
        
        assert 'version' in config
        assert 'fields' in config
        assert 'outputs' in config
    
    def test_config_validation(self):
        """测试配置验证"""
        parser = ConfigParser()
        
        # 有效的配置
        valid_config = {
            'version': '1.0',
            'fields': {
                'test': {'type': 'string'}
            }
        }
        
        # 应该不会抛出异常
        parser.validate(valid_config)
        
        # 无效的配置 - 缺少必填字段
        invalid_config = {
            'version': '1.0'
            # 缺少fields
        }
        
        with pytest.raises(Exception):
            parser.validate(invalid_config)
    
    def test_save_and_load_config_file(self):
        """测试保存和加载配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml_content = """
            version: "1.0"
            description: "测试配置文件"
            config:
              rows: 5
            fields:
              id:
                type: "integer"
                config:
                  start: 1
                  increment: 1
            """
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            parser = ConfigParser()
            config = parser.load_from_file(temp_file)
            
            assert config['version'] == '1.0'
            assert config['config']['rows'] == 5
            assert 'id' in config['fields']
        finally:
            os.unlink(temp_file)


class TestDataGenerator:
    """数据生成器测试"""
    
    def test_simple_generation(self):
        """测试简单数据生成"""
        config = {
            'version': '1.0',
            'config': {
                'rows': 5,
                'seed': 123
            },
            'fields': {
                'id': {
                    'type': 'integer',
                    'config': {
                        'start': 1,
                        'increment': 1
                    }
                },
                'name': {
                    'type': 'string',
                    'config': {
                        'min_length': 5,
                        'max_length': 10
                    }
                }
            }
        }
        
        generator = DataGenerator(config_dict=config)
        data = generator.generate()
        
        assert len(data) == 5
        assert all('id' in row for row in data)
        assert all('name' in row for row in data)
        assert all(isinstance(row['id'], int) for row in data)
        assert all(isinstance(row['name'], str) for row in data)
        
        # 验证ID是顺序的
        ids = [row['id'] for row in data]
        assert ids == [1, 2, 3, 4, 5]
    
    def test_generation_with_dependencies(self):
        """测试带依赖的数据生成"""
        config = {
            'version': '1.0',
            'config': {
                'rows': 3
            },
            'fields': {
                'first_name': {
                    'type': 'string',
                    'config': {
                        'generator': 'random_string',
                        'min_length': 3,
                        'max_length': 5
                    }
                },
                'email': {
                    'type': 'email',
                    'config': {
                        'domain': 'test.com'
                    },
                    'dependencies': ['first_name']
                }
            }
        }
        
        generator = DataGenerator(config_dict=config)
        data = generator.generate()
        
        assert len(data) == 3
        for row in data:
            assert 'first_name' in row
            assert 'email' in row
            assert '@test.com' in row['email']
    
    def test_export_to_dataframe(self):
        """测试导出为DataFrame"""
        config = {
            'version': '1.0',
            'config': {
                'rows': 3
            },
            'fields': {
                'id': {
                    'type': 'integer',
                    'config': {
                        'start': 1,
                        'increment': 1
                    }
                }
            }
        }
        
        generator = DataGenerator(config_dict=config)
        generator.generate()
        df = generator.to_dataframe()
        
        assert len(df) == 3
        assert 'id' in df.columns
        assert df['id'].tolist() == [1, 2, 3]
    
    def test_validation_functionality(self):
        """测试验证功能"""
        config = {
            'version': '1.0',
            'config': {
                'rows': 5
            },
            'fields': {
                'age': {
                    'type': 'integer',
                    'config': {
                        'min': 18,
                        'max': 80
                    }
                }
            },
            'validations': [
                {
                    'field': 'age',
                    'rule': '>= 18',
                    'message': '年龄必须大于等于18岁'
                }
            ]
        }
        
        generator = DataGenerator(config_dict=config)
        generator.generate()
        
        # 由于数据在生成时已经符合范围，验证应该通过
        validation_results = generator.validate()
        assert len(validation_results) == 0  # 应该没有验证错误