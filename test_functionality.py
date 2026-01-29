#!/usr/bin/env python3
"""
测试数据生成器功能验证脚本
"""
import os
import sys
import shutil

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.generator import DataGenerator
from src.template_generator import TemplateGenerator
from src.config.parser import ConfigParser


def test_config_parsing():
    """测试配置解析"""
    print("=" * 60)
    print("测试配置解析")
    print("=" * 60)
    
    # 创建简单配置
    config_yaml = """
    version: "1.0"
    description: "测试配置解析"
    config:
      rows: 5
    fields:
      test_field:
        type: "string"
    """
    
    parser = ConfigParser()
    try:
        config = parser.load_from_string(config_yaml)
        print("✓ 配置解析成功")
        print(f"  版本: {config['version']}")
        print(f"  描述: {config['description']}")
        print(f"  行数: {config['config']['rows']}")
        return True
    except Exception as e:
        print(f"✗ 配置解析失败: {e}")
        return False


def test_simple_generation():
    """测试简单数据生成"""
    print("\n" + "=" * 60)
    print("测试简单数据生成")
    print("=" * 60)
    
    config = {
        'version': '1.0',
        'config': {
            'rows': 3,
            'seed': 999
        },
        'fields': {
            'id': {
                'type': 'integer',
                'config': {
                    'start': 100,
                    'increment': 10
                }
            },
            'name': {
                'type': 'string',
                'config': {
                    'min_length': 3,
                    'max_length': 6
                }
            }
        }
    }
    
    try:
        generator = DataGenerator(config_dict=config)
        data = generator.generate()
        
        print("✓ 数据生成成功")
        print(f"  生成行数: {len(data)}")
        
        print("  生成的数据:")
        for i, row in enumerate(data, 1):
            print(f"    行{i}: ID={row['id']}, 姓名='{row['name']}'")
        
        # 验证数据
        assert len(data) == 3
        assert data[0]['id'] == 100
        assert data[1]['id'] == 110
        assert data[2]['id'] == 120
        
        return True
    except Exception as e:
        print(f"✗ 数据生成失败: {e}")
        return False


def test_field_types():
    """测试各种字段类型"""
    print("\n" + "=" * 60)
    print("测试各种字段类型")
    print("=" * 60)
    
    config = {
        'version': '1.0',
        'config': {
            'rows': 2
        },
        'fields': {
            'int_field': {
                'type': 'integer',
                'config': {'min': 1, 'max': 10}
            },
            'float_field': {
                'type': 'float',
                'config': {'min': 0.0, 'max': 1.0, 'precision': 2}
            },
            'bool_field': {
                'type': 'boolean',
                'config': {'true_probability': 0.5}
            },
            'string_field': {
                'type': 'string',
                'config': {'min_length': 5, 'max_length': 10}
            },
            'choice_field': {
                'type': 'choice',
                'config': {'choices': ['A', 'B', 'C']}
            }
        }
    }
    
    try:
        generator = DataGenerator(config_dict=config)
        data = generator.generate()
        
        print("✓ 多种字段类型生成成功")
        
        for i, row in enumerate(data, 1):
            print(f"\n  行{i}:")
            for field_name, value in row.items():
                print(f"    {field_name}: {value} ({type(value).__name__})")
        
        # 验证字段类型
        for row in data:
            assert isinstance(row['int_field'], int)
            assert isinstance(row['float_field'], float)
            assert isinstance(row['bool_field'], bool)
            assert isinstance(row['string_field'], str)
            assert row['choice_field'] in ['A', 'B', 'C']
        
        return True
    except Exception as e:
        print(f"✗ 字段类型测试失败: {e}")
        return False


def test_output_formats():
    """测试输出格式"""
    print("\n" + "=" * 60)
    print("测试输出格式")
    print("=" * 60)
    
    # 清理测试目录
    output_dir = './test_output'
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    config = {
        'version': '1.0',
        'config': {
            'rows': 3,
            'output_dir': output_dir
        },
        'fields': {
            'id': {'type': 'integer', 'config': {'start': 1, 'increment': 1}},
            'value': {'type': 'string', 'config': {'min_length': 3, 'max_length': 5}}
        },
        'outputs': {
            'csv': {
                'enabled': True,
                'config': {'output_file': 'test.csv'}
            },
            'json': {
                'enabled': True,
                'config': {'output_file': 'test.json', 'indent': 2}
            }
        }
    }
    
    try:
        generator = DataGenerator(config_dict=config)
        generator.generate()
        
        print("✓ 数据生成完成")
        
        # 测试CSV导出
        try:
            csv_file = generator.to_csv()
            if os.path.exists(csv_file):
                print(f"  ✓ CSV文件创建成功: {csv_file}")
                print(f"    文件大小: {os.path.getsize(csv_file)} 字节")
            else:
                print(f"  ✗ CSV文件不存在: {csv_file}")
                return False
        except Exception as e:
            print(f"  ✗ CSV导出失败: {e}")
            return False
        
        # 测试JSON导出
        try:
            json_file = generator.to_json()
            if os.path.exists(json_file):
                print(f"  ✓ JSON文件创建成功: {json_file}")
                print(f"    文件大小: {os.path.getsize(json_file)} 字节")
            else:
                print(f"  ✗ JSON文件不存在: {json_file}")
                return False
        except Exception as e:
            print(f"  ✗ JSON导出失败: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 输出格式测试失败: {e}")
        return False
    finally:
        # 清理测试目录
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)


def test_template_generation():
    """测试模板生成"""
    print("\n" + "=" * 60)
    print("测试模板生成")
    print("=" * 60)
    
    try:
        templates = TemplateGenerator.get_all_templates()
        
        print(f"✓ 获取到 {len(templates)} 个模板")
        
        for template_name in templates.keys():
            print(f"  - {template_name}")
        
        # 测试用户数据模板
        user_template = TemplateGenerator.create_user_data_template()
        if 'user_data' in user_template:
            print("✓ 用户数据模板生成成功")
        else:
            print("✗ 用户数据模板生成失败")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 模板生成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("测试数据生成器功能验证")
    print("=" * 60)
    
    tests = [
        test_config_parsing,
        test_simple_generation,
        test_field_types,
        test_output_formats,
        test_template_generation
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"测试 {test_func.__name__} 时发生异常: {e}")
            results.append((test_func.__name__, False))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {len(results)} 个测试")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    
    if failed == 0:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print(f"\n⚠ 有 {failed} 个测试失败")
        return 1


if __name__ == '__main__':
    # 修复测试中的语法错误
    import sys
    sys.exit(main())