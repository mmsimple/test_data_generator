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
@click.argument("config_file", type=click.Path(exists=True))
@click.option("--rows", type=int, help="生成的行数（覆盖配置文件中的设置）")
@click.option(
    "--output-format",
    type=click.Choice(["csv", "json", "excel", "sql", "all"]),
    default="all",
    help="输出格式",
)
@click.option(
    "--output-dir", type=click.Path(), help="输出目录（覆盖配置文件中的设置）"
)
@click.option("--validate", is_flag=True, help="生成后验证数据")
@click.option("--summary", is_flag=True, help="显示数据摘要")
def generate(config_file, rows, output_format, output_dir, validate, summary):
    """根据配置文件生成测试数据"""
    try:
        # 初始化生成器
        generator = DataGenerator(config_file)

        # 覆盖配置
        if rows:
            generator.config["config"]["rows"] = rows
        if output_dir:
            generator.config["config"]["output_dir"] = output_dir

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
                    click.echo(
                        f"  行 {result['row']}, 字段 {result['field']}: {result['message']}"
                    )
                if len(validation_results) > 5:
                    click.echo(f"  ... 还有 {len(validation_results) - 5} 个错误")
            else:
                click.echo("✓ 所有数据验证通过")

        # 导出数据
        exported_files = {}

        if output_format in ["csv", "all"]:
            try:
                filepath = generator.to_csv()
                exported_files["csv"] = filepath
                click.echo(f"✓ CSV文件: {filepath}")
            except Exception as e:
                click.echo(f"✗ CSV导出失败: {e}")

        if output_format in ["json", "all"]:
            try:
                filepath = generator.to_json()
                exported_files["json"] = filepath
                click.echo(f"✓ JSON文件: {filepath}")
            except Exception as e:
                click.echo(f"✗ JSON导出失败: {e}")

        if output_format in ["excel", "all"]:
            try:
                filepath = generator.to_excel()
                exported_files["excel"] = filepath
                click.echo(f"✓ Excel文件: {filepath}")
            except Exception as e:
                click.echo(f"✗ Excel导出失败: {e}")

        if output_format in ["sql", "all"]:
            try:
                filepath = generator.to_sql()
                exported_files["sql"] = filepath
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
                click.echo(
                    f"  字段类型分布: {json.dumps(summary_info['field_types'], ensure_ascii=False, indent=2)}"
                )
            except Exception as e:
                click.echo(f"✗ 摘要生成失败: {e}")

        click.echo("\n🎉 数据生成完成!")

    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument(
    "template_name",
    type=click.Choice(["user_data", "product_data", "order_data", "employee_data"]),
)
@click.option("--output", "-o", type=click.Path(), help="输出文件路径")
def template(template_name, output):
    """生成配置模板"""
    try:
        templates = TemplateGenerator.get_all_templates()

        if template_name not in templates:
            click.echo(f"❌ 未知的模板: {template_name}", err=True)
            sys.exit(1)

        template_content = templates[template_name]

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(template_content)
            click.echo(f"✓ 模板已保存到: {output}")
        else:
            click.echo(template_content)

    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
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
        for field_name, field_config in config["fields"].items():
            field_type = field_config.get("type", "未知")
            description = field_config.get("metadata", {}).get("description", "无描述")
            click.echo(f"  {field_name}: {field_type} - {description}")

        # 显示启用的输出格式
        enabled_outputs = []
        for format_name, format_config in config.get("outputs", {}).items():
            if format_config.get("enabled", False):
                enabled_outputs.append(format_name)

        if enabled_outputs:
            click.echo(f"\n启用的输出格式: {', '.join(enabled_outputs)}")

    except Exception as e:
        click.echo(f"❌ 配置文件验证失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("--rows", type=int, default=10, help="生成的预览行数")
def preview(config_file, rows):
    """预览生成的数据"""
    try:
        generator = DataGenerator(config_file)
        generator.config["config"]["rows"] = rows  # 临时修改行数

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
                    value = value[: max_width - 3] + "..."
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


# ===== 新增：Parse 命令组 =====


@cli.group()
def parse():
    """解析 Markdown 文档并生成配置"""
    pass


@parse.command()
@click.argument("markdown_file", type=click.Path(exists=True))
@click.option(
    "--output", "-o", type=click.Path(), required=True, help="输出 YAML 配置文件路径"
)
@click.option(
    "--model",
    type=click.Choice(["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]),
    default="gpt-4o",
    help="使用的 AI 模型",
)
@click.option("--api-key", envvar="OPENAI_API_KEY", help="OpenAI API 密钥")
@click.option(
    "--api-base",
    envvar="OPENAI_API_BASE",
    help="OpenAI API base URL (可选，支持兼容的API)",
)
@click.option("--timeout", type=int, default=120, help="API 请求超时时间（秒）")
@click.option("--max-retries", type=int, default=3, help="最大重试次数")
@click.option("--preview", is_flag=True, help="预览生成的配置而不保存")
@click.option("--validate", is_flag=True, help="解析后验证配置")
@click.option("--verbose", "-v", is_flag=True, help="显示详细输出")
def schema(
    markdown_file,
    output,
    model,
    api_key,
    api_base,
    timeout,
    max_retries,
    preview,
    validate,
    verbose,
):
    """将 Markdown 数据库 schema 文档解析为 YAML 配置"""
    try:
        from .schema_parser import SchemaParser

        if verbose:
            click.echo(f"📄 读取 Markdown 文件: {markdown_file}")

        # 初始化解析器
        parser = SchemaParser(
            api_key=api_key,
            model=model,
            api_base=api_base,
            timeout=timeout,
            max_retries=max_retries,
            verbose=verbose,
        )

        # 解析 Markdown
        click.echo(f"🤖 使用 {model} 解析文档...")
        yaml_content = parser.parse_markdown_to_yaml(markdown_file)

        # 显示解析结果
        if verbose:
            click.echo("\n✓ 解析完成！生成的配置：")
            click.echo("-" * 80)
            click.echo(yaml_content)
            click.echo("-" * 80)

        # 验证配置
        if validate:
            click.echo("\n🔍 验证配置...")
            from .config.parser import ConfigParser

            config_parser = ConfigParser()
            config = config_parser.load_from_string(yaml_content)
            click.echo("✓ 配置验证通过")

            # 显示统计信息
            if "tables" in config:
                click.echo(f"  - 表数量: {len(config['tables'])}")
                for table_name, table_config in config["tables"].items():
                    click.echo(
                        f"    • {table_name}: {len(table_config['fields'])} 个字段"
                    )
            else:
                click.echo(f"  - 字段数量: {len(config['fields'])}")

            if "relations" in config:
                click.echo(f"  - 关系数量: {len(config['relations'])}")

        # 预览或保存
        if preview:
            click.echo("\n📋 预览模式 - 不保存文件")
        else:
            # 确保输出目录存在
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存配置
            with open(output, "w", encoding="utf-8") as f:
                f.write(yaml_content)

            click.echo(f"\n✓ 配置已保存到: {output}")

            # 下一步提示
            click.echo("\n💡 下一步：")
            click.echo(f"  python -m src.cli generate {output}")

        click.echo("\n🎉 解析完成！")

    except Exception as e:
        click.echo(f"\n❌ 错误: {e}", err=True)
        if verbose:
            import traceback

            click.echo(traceback.format_exc())
        sys.exit(1)


@parse.command()
@click.argument("markdown_file", type=click.Path(exists=True))
@click.option("--rows", type=int, help="生成的行数（覆盖配置中的设置）")
@click.option(
    "--output-format",
    type=click.Choice(["csv", "json", "excel", "sql", "all"]),
    default="all",
    help="输出格式",
)
@click.option("--output-dir", type=click.Path(), help="输出目录")
@click.option(
    "--model",
    type=click.Choice(["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]),
    default="gpt-4o",
    help="使用的 AI 模型",
)
@click.option("--api-key", envvar="OPENAI_API_KEY", help="OpenAI API 密钥")
@click.option("--api-base", envvar="OPENAI_API_BASE", help="OpenAI API base URL")
@click.option("--validate", is_flag=True, help="生成后验证数据")
@click.option("--summary", is_flag=True, help="显示数据摘要")
@click.option("--verbose", "-v", is_flag=True, help="显示详细输出")
def data(
    markdown_file,
    rows,
    output_format,
    output_dir,
    model,
    api_key,
    api_base,
    validate,
    summary,
    verbose,
):
    """从 Markdown 文档直接生成测试数据（一步完成）"""
    import tempfile
    import os

    try:
        if verbose:
            click.echo(f"📄 读取 Markdown 文件: {markdown_file}")

        # 第一步：解析 Markdown 为 YAML
        from .schema_parser import SchemaParser

        parser = SchemaParser(
            api_key=api_key, model=model, api_base=api_base, verbose=verbose
        )

        click.echo("🤖 解析 Markdown 为配置...")

        # 生成临时 YAML 配置文件
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as f:
            temp_yaml_file = f.name
            yaml_content = parser.parse_markdown_to_yaml(markdown_file)
            f.write(yaml_content)

        try:
            if verbose:
                click.echo(f"   临时配置: {temp_yaml_file}")

            # 第二步：使用现有的 generate 命令
            click.echo("🚀 生成测试数据...")

            # 复用现有的生成逻辑
            generator = DataGenerator(temp_yaml_file)

            # 覆盖配置
            if rows:
                generator.config["config"]["rows"] = rows
            if output_dir:
                generator.config["config"]["output_dir"] = output_dir

            # 生成数据
            data = generator.generate()
            click.echo(f"✓ 成功生成 {len(data)} 行数据")

            # 验证数据
            if validate:
                validation_results = generator.validate()
                if validation_results:
                    click.echo(f"⚠ 发现 {len(validation_results)} 个验证错误")
                else:
                    click.echo("✓ 所有数据验证通过")

            # 导出数据
            exported_files = {}

            if output_format in ["csv", "all"]:
                try:
                    filepath = generator.to_csv()
                    exported_files["csv"] = filepath
                    click.echo(f"✓ CSV: {filepath}")
                except Exception as e:
                    click.echo(f"✗ CSV导出失败: {e}")

            if output_format in ["json", "all"]:
                try:
                    filepath = generator.to_json()
                    exported_files["json"] = filepath
                    click.echo(f"✓ JSON: {filepath}")
                except Exception as e:
                    click.echo(f"✗ JSON导出失败: {e}")

            if output_format in ["excel", "all"]:
                try:
                    filepath = generator.to_excel()
                    exported_files["excel"] = filepath
                    click.echo(f"✓ Excel: {filepath}")
                except Exception as e:
                    click.echo(f"✗ Excel导出失败: {e}")

            if output_format in ["sql", "all"]:
                try:
                    filepath = generator.to_sql()
                    exported_files["sql"] = filepath
                    click.echo(f"✓ SQL: {filepath}")
                except Exception as e:
                    click.echo(f"✗ SQL导出失败: {e}")

            # 显示摘要
            if summary:
                try:
                    summary_info = generator.get_summary()
                    click.echo("\n数据摘要:")
                    click.echo(f"  总行数: {summary_info['total_rows']}")
                    click.echo(f"  字段数: {summary_info['total_fields']}")
                    click.echo(
                        f"  字段类型: {json.dumps(summary_info['field_types'], ensure_ascii=False, indent=2)}"
                    )
                except Exception as e:
                    click.echo(f"✗ 摘要生成失败: {e}")

            click.echo("\n🎉 数据生成完成！")

        finally:
            # 清理临时文件
            try:
                os.unlink(temp_yaml_file)
                if verbose:
                    click.echo(f"   清理临时文件: {temp_yaml_file}")
            except:
                pass

    except Exception as e:
        click.echo(f"❌ 错误: {e}", err=True)
        if verbose:
            import traceback

            click.echo(traceback.format_exc())
        sys.exit(1)


# ============================


def main():
    """主函数"""
    cli()


if __name__ == "__main__":
    main()
