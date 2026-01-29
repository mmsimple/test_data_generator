"""
测试数据生成器基本使用示例
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generator import DataGenerator
from src.template_generator import TemplateGenerator


def example_basic_usage():
    """基本使用示例"""
    print("=" * 60)
    print("测试数据生成器 - 基本使用示例")
    print("=" * 60)
    
    # 1. 使用配置字典生成数据
    print("\n1. 使用配置字典生成数据")
    
    config = {
        'version': '1.0',
        'config': {
            'rows': 5,
            'seed': 42
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
            },
            'age': {
                'type': 'integer',
                'config': {
                    'min': 18,
                    'max': 30,
                    'distribution': 'uniform'
                }
            },
            'is_student': {
                'type': 'boolean',
                'config': {
                    'true_probability': 0.7
                }
            }
        }
    }
    
    generator = DataGenerator(config_dict=config)
    data = generator.generate()
    
    print(f"生成了 {len(data)} 行数据:")
    for i, row in enumerate(data, 1):
        print(f"  行{i}: ID={row['id']}, 姓名={row['name']}, 年龄={row['age']}, 是否学生={row['is_student']}")


def example_advanced_features():
    """高级功能示例"""
    print("\n\n" + "=" * 60)
    print("测试数据生成器 - 高级功能示例")
    print("=" * 60)
    
    # 创建更复杂的配置
    config = {
        'version': '1.0',
        'description': '用户数据生成示例',
        'config': {
            'rows': 10,
            'seed': 12345
        },
        'fields': {
            'user_id': {
                'type': 'integer',
                'config': {
                    'start': 1001,
                    'increment': 1
                },
                'metadata': {
                    'description': '用户ID',
                    'primary_key': True
                }
            },
            'username': {
                'type': 'string',
                'config': {
                    'generator': 'random_string',
                    'min_length': 6,
                    'max_length': 12,
                    'prefix': 'user_'
                }
            },
            'email': {
                'type': 'email',
                'config': {
                    'domain': 'example.com'
                },
                'dependencies': ['username']
            },
            'age': {
                'type': 'integer',
                'config': {
                    'min': 18,
                    'max': 65,
                    'distribution': 'normal',
                    'mean': 30,
                    'std_dev': 8
                }
            },
            'registration_date': {
                'type': 'date',
                'config': {
                    'start_date': '2023-01-01',
                    'end_date': '2024-12-31',
                    'format': '%Y-%m-%d'
                }
            }
        },
        'outputs': {
            'csv': {
                'enabled': True,
                'config': {
                    'output_file': 'output/users.csv',
                    'include_header': True
                }
            },
            'json': {
                'enabled': True,
                'config': {
                    'output_file': 'output/users.json',
                    'indent': 2
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
    data = generator.generate()
    
    print(f"\n生成了 {len(data)} 行用户数据")
    print("前3行数据:")
    for i, row in enumerate(data[:3], 1):
        print(f"  行{i}: ID={row['user_id']}, 用户名={row['username']}, "
              f"邮箱={row['email']}, 年龄={row['age']}, 注册日期={row['registration_date']}")
    
    # 导出数据
    print("\n导出数据...")
    try:
        csv_file = generator.to_csv()
        print(f"  ✓ CSV文件: {csv_file}")
        
        json_file = generator.to_json()
        print(f"  ✓ JSON文件: {json_file}")
    except Exception as e:
        print(f"  ✗ 导出失败: {e}")
    
    # 数据验证
    print("\n数据验证...")
    validation_results = generator.validate()
    if validation_results:
        print(f"  ⚠ 发现 {len(validation_results)} 个验证错误")
    else:
        print("  ✓ 所有数据验证通过")
    
    # 数据摘要
    print("\n数据摘要:")
    try:
        summary = generator.get_summary()
        print(f"  总行数: {summary['total_rows']}")
        print(f"  字段数: {summary['total_fields']}")
        print(f"  字段类型: {summary['field_types']}")
        
        if 'age' in summary['field_stats']:
            age_stats = summary['field_stats']['age']
            print(f"  年龄统计: 最小值={age_stats['min']}, 最大值={age_stats['max']}, "
                  f"平均值={age_stats['mean']:.1f}")
    except Exception as e:
        print(f"  摘要生成失败: {e}")


def example_template_generator():
    """模板生成器示例"""
    print("\n\n" + "=" * 60)
    print("测试数据生成器 - 模板生成器示例")
    print("=" * 60)
    
    # 获取所有模板
    templates = TemplateGenerator.get_all_templates()
    
    print(f"可用模板数量: {len(templates)}")
    print("\n模板列表:")
    for template_name in templates.keys():
        print(f"  - {template_name}")
    
    # 生成用户数据模板
    print("\n用户数据模板示例:")
    user_template = TemplateGenerator.create_user_data_template()
    
    # 显示前几行
    lines = user_template.split('\n')[:20]
    print('\n'.join(lines))
    print("...")
    
    # 保存模板到文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        f.write(user_template)
        temp_file = f.name
    
    print(f"\n模板已保存到临时文件: {temp_file}")
    
    # 可以在这里使用保存的模板文件
    # generator = DataGenerator(temp_file)
    
    import os
    os.unlink(temp_file)
    print("临时文件已删除")


def example_custom_fields():
    """自定义字段示例"""
    print("\n\n" + "=" * 60)
    print("测试数据生成器 - 自定义字段示例")
    print("=" * 60)
    
    # 使用扩展字段的配置
    config = {
        'version': '1.0',
        'config': {
            'rows': 5
        },
        'fields': {
            'full_name': {
                'type': 'name',
                'config': {
                    'gender': 'both'
                }
            },
            'phone_number': {
                'type': 'phone',
                'config': {
                    'operator': None
                }
            },
            'home_address': {
                'type': 'address',
                'config': {
                    'include_detail': True
                }
            },
            'salary': {
                'type': 'money',
                'config': {
                    'min': 3000.0,
                    'max': 20000.0,
                    'precision': 0,
                    'distribution': 'normal',
                    'mean': 7780.0,
                    'std_dev': 3000.0
                }
            }
        }
    }
    
    try:
        generator = DataGenerator(config_dict=config)
        data = generator.generate()
        
        print("生成的数据:")
        for i, row in enumerate(data, 1):
            print(f"\n行{i}:")
            print(f"  姓名: {row.get('full_name', 'N/A')}")
            print(f"  电话: {row.get('phone_number', 'N/A')}")
            print(f"  地址: {row.get('home_address', 'N/A')}")
            print(f"  薪资: {row.get('salary', 'N/A')}")
    except ValueError as e:
        print(f"注意: {e}")
        print("可能需要安装扩展字段模块")


if __name__ == '__main__':
    print("测试数据生成器示例程序")
    print("=" * 60)
    
    # 创建输出目录
    os.makedirs('output', exist_ok=True)
    
    # 运行示例
    example_basic_usage()
    example_advanced_features()
    example_template_generator()
    example_custom_fields()
    
    print("\n" + "=" * 60)
    print("示例程序运行完成!")
    print("生成的文件保存在 'output' 目录中")
    print("=" * 60)