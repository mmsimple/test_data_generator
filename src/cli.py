"""
命令行接口
"""
import click
import yaml
from pathlib import Path
import json
import sys

from .generator import DataGenerator
from .template_generator import TemplateGenerator


@click.group()
def cli():
    """测试数据生成器"""
    pass


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--rows', type=int, help='生成的行数（覆盖配置文件中的设置）')
@click.option('--output-format', type=click.Choice(['csv', 'json', 'excel', 'sql', 'all']), 
              default='all', help='输出格式')
@click.option('--output-dir', type=click.Path(), help='输出目录（覆盖配置文件中的设置）')
@click.option('--validate', is_flag=True, help='生成后验证数据')
@click.option('--summary', is_flag=True, help='显示数据摘要')
def generate(config_file, rows, output_format, output_dir, validate, summary):
    """根据配置文件生成测试数据"""
    try:
        # 初始化生成器
        generator = DataGenerator(config_file)
        
        # 覆盖配置
        if rows:
            generator.config['config']['rows'] = rows
        if output_dir:
            generator.config['config']['output_dir'] = output_dir
        
        # 生成数据
        click.echo(f"生成 {generator.config['config']['rows']} 行数据...")
        data = generator.generate()
        click.echo(f"✓ 成功生成 {len(data)} 行数据")
        
        # 验证数据
        if validate:
            validation_results = generator.validate()
            if validation_results:
                click.echo(f"⚠ 发现 {len(validation_results)} 个验证错误:")
                for result in validation_results[:5]:  # 只显示前5个错误
                    click.echo(f"  行 {result['row']}, 字段 {result['field']}: {result['message']}")
                if len(validation_results) > 5:
                    click.echo(f"  ... 还有 {len(validation_results) - 5} 个错误")
            else:
                click.echo("✓ 所有数据验证通过")
        
        # 导出数据
        exported_files = {}
        
        if output_format in ['csv', 'all']:
            try:
                filepath = generator.to_csv()
                exported_files['csv'] = filepath
                click.echo(f"✓ CSV文件: {filepath}")
            except Exception as e:
                click.echo(f"✗ CSV导出失败: {e}")
        
        if output_format in ['json', 'all']:
            try:
                filepath = generator.to_json()
                exported_files['json'] = filepath
                click.echo(f"✓ JSON文件: {filepath}")
            except Exception as e:
                click.echo(f"✗ JSON导出失败: {e}")
        
        if output_format in ['excel', 'all']:
            try:
                filepath = generator.to_excel()
                exported_files['excel'] = filepath
                click.echo(f"✓ Excel文件: {filepath}")
            except Exception as e:
                click.echo(f"✗ Excel导出失败: {e}")
        
        if output_format in ['sql', 'all']:
            try:
                filepath = generator.to_sql()
                exported_files['sql'] = filepath
                click.echo(f"✓ SQL文件: {filepath}")
            except Exception as e:
                click.echo(f"✗ SQL导出失败: {e}")
        
        # 显示摘要
        if summary:
            try:
                summary_info = generator.get_summary()
                click.echo("\n数据摘要:")
                click.echo(f"  总行数: {summary_info['total_rows']}")
                click.echo(f"  字段数: {summary_info['total_fields']}")
                click.echo(f"  字段类型分布: {json.dumps(summary_info['field_types'], ensure_ascii=False, indent=2)}")
            except Exception as e:
                click.echo(f"✗ 摘要生成失败: {e}")
        
        click.echo("\n🎉 数据生成完成!")
        
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('template_name', type=click.Choice(['user_data', 'product_data', 'order_data', 'employee_data']))
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
def template(template_name, output):
    """生成配置模板"""
    try:
        templates = TemplateGenerator.get_all_templates()
        
        if template_name not in templates:
            click.echo(f"❌ 未知的模板: {template_name}", err=True)
            sys.exit(1)
        
        template_content = templates[template_name]
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(template_content)
            click.echo(f"✓ 模板已保存到: {output}")
        else:
            click.echo(template_content)
            
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
def validate(config_file):
    """验证配置文件"""
    try:
        from .config.parser import ConfigParser
        
        parser = ConfigParser()
        config = parser.load_from_file(config_file)
        
        click.echo("✓ 配置文件验证通过")
        click.echo(f"  版本: {config['version']}")
        click.echo(f"  描述: {config.get('description', '无')}")
        click.echo(f"  数据行数: {config['config']['rows']}")
        click.echo(f"  字段数量: {len(config['fields'])}")
        
        # 显示字段信息
        click.echo("\n字段列表:")
        for field_name, field_config in config['fields'].items():
            field_type = field_config.get('type', '未知')
            description = field_config.get('metadata', {}).get('description', '无描述')
            click.echo(f"  {field_name}: {field_type} - {description}")
        
        # 显示启用的输出格式
        enabled_outputs = []
        for format_name, format_config in config.get('outputs', {}).items():
            if format_config.get('enabled', False):
                enabled_outputs.append(format_name)
        
        if enabled_outputs:
            click.echo(f"\n启用的输出格式: {', '.join(enabled_outputs)}")
        
    except Exception as e:
        click.echo(f"❌ 配置文件验证失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--rows', type=int, default=10, help='生成的预览行数')
def preview(config_file, rows):
    """预览生成的数据"""
    try:
        generator = DataGenerator(config_file)
        generator.config['config']['rows'] = rows  # 临时修改行数
        
        data = generator.generate()
        
        # 显示数据
        click.echo(f"预览数据 (前{len(data)}行):\n")
        
        if not data:
            click.echo("没有数据生成")
            return
        
        # 获取所有字段名
        field_names = list(data[0].keys())
        
        # 计算每列的最大宽度
        col_widths = {}
        for field in field_names:
            # 字段名宽度
            col_widths[field] = len(field)
            # 数据宽度
            for row in data:
                value_str = str(row[field])
                if len(value_str) > col_widths[field]:
                    col_widths[field] = len(value_str)
        
        # 限制最大宽度
        max_width = 30
        for field in field_names:
            if col_widths[field] > max_width:
                col_widths[field] = max_width
        
        # 打印表头
        header = " | ".join([f"{field:<{col_widths[field]}}" for field in field_names])
        separator = "-+-".join(["-" * col_widths[field] for field in field_names])
        
        click.echo(header)
        click.echo(separator)
        
        # 打印数据
        for row in data:
            row_str = []
            for field in field_names:
                value = str(row[field])
                if len(value) > max_width:
                    value = value[:max_width-3] + "..."
                row_str.append(f"{value:<{col_widths[field]}}")
            click.echo(" | ".join(row_str))
        
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
def list_templates():
    """列出所有可用的模板"""
    try:
        templates = TemplateGenerator.get_all_templates()
        
        click.echo("可用模板:")
        click.echo("  user_data     - 用户数据模板")
        click.echo("  product_data  - 产品数据模板")
        click.echo("  order_data    - 订单数据模板")
        click.echo("  employee_data - 员工数据模板")
        
        click.echo("\n使用方法:")
        click.echo("  python -m src.cli template <template_name> -o config.yaml")
        
    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


def main():
    """主函数"""
    cli()


if __name__ == '__main__':
    main()