"""
主数据生成器模块
"""
import random
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import pandas as pd
from pathlib import Path

from .config.parser import parse_config
from .fields.base import create_field, FIELD_TYPE_MAPPING


class DataGenerator:
    """主数据生成器类"""
    
    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None):
        """
        初始化数据生成器
        
        Args:
            config_path: YAML配置文件路径
            config_dict: 配置字典
        """
        if config_path:
            self.config = parse_config(config_path)
        elif config_dict:
            self.config = config_dict
        else:
            raise ValueError("必须提供config_path或config_dict")
        
        # 设置随机种子
        seed = self.config.get('config', {}).get('seed')
        if seed is not None:
            random.seed(seed)
        
        # 检查是否为多表配置
        self.tables_config = self.config.get('tables', {})
        self.is_multi_table = len(self.tables_config) > 0
        
        if self.is_multi_table:
            # 多表模式
            self.tables = {}
            self.table_data = {}
            self._init_tables()
        else:
            # 单表模式
            self.fields = {}
            self.data: List[Dict[str, Any]] = []
            self._init_fields()
        
    def _init_fields(self) -> None:
        """初始化字段实例（单表模式）"""
        fields_config = self.config.get('fields', {})
        
        for field_name, field_config in fields_config.items():
            try:
                field = create_field(field_name, field_config)
                self.fields[field_name] = field
            except Exception as e:
                raise ValueError(f"初始化字段'{field_name}'失败: {str(e)}")
    
    def _init_tables(self) -> None:
        """初始化表实例（多表模式）"""
        for table_name, table_config in self.tables_config.items():
            try:
                table = {
                    'name': table_name,
                    'config': table_config.get('config', {}),
                    'fields': {}
                }
                
                # 初始化表字段
                fields_config = table_config.get('fields', {})
                for field_name, field_config in fields_config.items():
                    try:
                        field = create_field(field_name, field_config)
                        table['fields'][field_name] = field
                    except Exception as e:
                        raise ValueError(f"初始化表'{table_name}'的字段'{field_name}'失败: {str(e)}")
                
                self.tables[table_name] = table
                self.table_data[table_name] = []
            except Exception as e:
                raise ValueError(f"初始化表'{table_name}'失败: {str(e)}")
    
    def generate(self, rows: Optional[int] = None) -> Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
        """
        生成测试数据

        Args:
            rows: 生成的行数，如果为None则使用配置中的rows

        Returns:
            生成的数据列表（单表模式）或字典（多表模式）
        """
        if self.is_multi_table:
            # 多表模式
            for table_name, table in self.tables.items():
                table_rows = table['config'].get('rows', self.config.get('config', {}).get('rows', 100))
                print(f"生成表'{table_name}'的 {table_rows} 行数据...")

                table_data = []
                for i in range(table_rows):
                    row_data = {}

                    # 按照依赖顺序生成字段
                    for field_name, field in table['fields'].items():
                        try:
                            # 传递当前行数据以便处理字段依赖
                            value = field.generate(row_data)
                            row_data[field_name] = value
                        except Exception as e:
                            raise ValueError(f"生成表'{table_name}'的字段'{field_name}'第{i+1}行数据失败: {str(e)}")

                    table_data.append(row_data)

                self.table_data[table_name] = table_data
                print(f"✓ 成功生成表'{table_name}'的 {len(table_data)} 行数据")

            return self.table_data
        else:
            # 单表模式
            rows_to_generate = rows or self.config.get('config', {}).get('rows', 100)
            
            self.data = []
            for i in range(rows_to_generate):
                row_data = {}
                
                # 按照依赖顺序生成字段
                for field_name, field in self.fields.items():
                    try:
                        # 传递当前行数据以便处理字段依赖
                        value = field.generate(row_data)
                        row_data[field_name] = value
                    except Exception as e:
                        raise ValueError(f"生成字段'{field_name}'第{i+1}行数据失败: {str(e)}")
                
                self.data.append(row_data)
            
            return self.data
    
    def validate(self) -> List[Dict[str, Any]]:
        """
        验证生成的数据
        
        Returns:
            验证结果列表，每个元素包含字段名、行号、验证结果
        """
        validation_results = []
        validations = self.config.get('validations', [])
        
        if self.is_multi_table:
            # 多表模式
            for table_name, table_data in self.table_data.items():
                for i, row_data in enumerate(table_data):
                    for validation in validations:
                        field_full_name = validation.get('field')
                        if '.' in field_full_name:
                            # 格式：table.field
                            validation_table, field_name = field_full_name.split('.', 1)
                            if validation_table != table_name:
                                continue
                        else:
                            # 单表模式或未指定表
                            field_name = field_full_name
                        
                        rule = validation.get('rule')
                        message = validation.get('message', '')
                        
                        if field_name in row_data:
                            value = row_data[field_name]
                            # 简单的规则验证，可以根据需要扩展
                            if rule.startswith('>='):
                                try:
                                    min_value = float(rule[2:].strip())
                                    is_valid = value >= min_value
                                except:
                                    is_valid = False
                            elif rule.startswith('<='):
                                try:
                                    max_value = float(rule[2:].strip())
                                    is_valid = value <= max_value
                                except:
                                    is_valid = False
                            elif rule.startswith('>'):
                                try:
                                    min_value = float(rule[1:].strip())
                                    is_valid = value > min_value
                                except:
                                    is_valid = False
                            elif rule.startswith('<'):
                                try:
                                    max_value = float(rule[1:].strip())
                                    is_valid = value < max_value
                                except:
                                    is_valid = False
                            elif 'length' in rule:
                                # 处理字符串长度验证
                                import re
                                length_match = re.search(r'length\s*>=>\s*(\d+)', rule)
                                if length_match:
                                    min_length = int(length_match.group(1))
                                    is_valid = len(str(value)) >= min_length
                                else:
                                    length_match = re.search(r'length\s*<=\s*(\d+)', rule)
                                    if length_match:
                                        max_length = int(length_match.group(1))
                                        is_valid = len(str(value)) <= max_length
                                    else:
                                        is_valid = True
                            else:
                                is_valid = True
                            
                            if not is_valid:
                                validation_results.append({
                                    'table': table_name,
                                    'row': i + 1,
                                    'field': field_name,
                                    'value': value,
                                    'rule': rule,
                                    'message': message,
                                    'valid': False
                                })
        else:
            # 单表模式
            for i, row_data in enumerate(self.data):
                for validation in validations:
                    field_name = validation.get('field')
                    rule = validation.get('rule')
                    message = validation.get('message', '')
                    
                    if field_name in row_data:
                        value = row_data[field_name]
                        # 简单的规则验证，可以根据需要扩展
                        if rule.startswith('>='):
                            try:
                                min_value = float(rule[2:].strip())
                                is_valid = value >= min_value
                            except:
                                is_valid = False
                        elif rule.startswith('<='):
                            try:
                                max_value = float(rule[2:].strip())
                                is_valid = value <= max_value
                            except:
                                is_valid = False
                        elif rule.startswith('>'):
                            try:
                                min_value = float(rule[1:].strip())
                                is_valid = value > min_value
                            except:
                                is_valid = False
                        elif rule.startswith('<'):
                            try:
                                max_value = float(rule[1:].strip())
                                is_valid = value < max_value
                            except:
                                is_valid = False
                        elif 'length' in rule:
                            # 处理字符串长度验证
                            import re
                            length_match = re.search(r'length\s*>=>\s*(\d+)', rule)
                            if length_match:
                                min_length = int(length_match.group(1))
                                is_valid = len(str(value)) >= min_length
                            else:
                                length_match = re.search(r'length\s*<=\s*(\d+)', rule)
                                if length_match:
                                    max_length = int(length_match.group(1))
                                    is_valid = len(str(value)) <= max_length
                                else:
                                    is_valid = True
                        else:
                            is_valid = True
                        
                        if not is_valid:
                            validation_results.append({
                                'row': i + 1,
                                'field': field_name,
                                'value': value,
                                'rule': rule,
                                'message': message,
                                'valid': False
                            })
        
        return validation_results
    
    def to_dataframe(self, table_name: Optional[str] = None) -> pd.DataFrame:
        """将生成的数据转换为pandas DataFrame"""
        if self.is_multi_table:
            if not table_name:
                raise ValueError("多表模式下必须指定表名")
            if not self.table_data.get(table_name):
                raise ValueError(f"表'{table_name}'没有生成数据")
            return pd.DataFrame(self.table_data[table_name])
        else:
            if not self.data:
                raise ValueError("请先生成数据")
            return pd.DataFrame(self.data)
    
    def _get_output_path(self, format_type: str, default_filename: str, table_name: Optional[str] = None) -> str:
        """获取输出文件路径"""
        outputs_config = self.config.get('outputs', {})
        format_config = outputs_config.get(format_type, {}).get('config', {})
        
        # 获取配置中的输出目录
        output_dir = self.config.get('config', {}).get('output_dir', './output')
        
        # 多表模式下使用表名作为文件名前缀
        if table_name:
            default_filename = f"{table_name}_{default_filename}"
        
        filepath = format_config.get('output_file', f"{output_dir}/{default_filename}")
        
        # 确保文件路径是字符串
        if not isinstance(filepath, str):
            filepath = f"{output_dir}/{default_filename}"
            
        return filepath
    
    def to_csv(self, filepath: Optional[str] = None, table_name: Optional[str] = None) -> Union[str, Dict[str, str]]:
        """
        将数据导出为CSV文件
        
        Args:
            filepath: 输出文件路径，如果为None则使用配置中的路径
            table_name: 表名（多表模式）
            
        Returns:
            文件路径（单表模式）或字典（多表模式）
        """
        if self.is_multi_table:
            # 多表模式
            if table_name:
                # 导出指定表
                if not self.table_data.get(table_name):
                    raise ValueError(f"表'{table_name}'没有生成数据")
                
                filepath = filepath or self._get_output_path('csv', 'data.csv', table_name)
                
                df = self.to_dataframe(table_name)
                
                # 确保目录存在
                Path(filepath).parent.mkdir(parents=True, exist_ok=True)
                
                # 获取配置
                outputs_config = self.config.get('outputs', {})
                csv_config = outputs_config.get('csv', {}).get('config', {})
                include_header = csv_config.get('include_header', True)
                delimiter = csv_config.get('delimiter', ',')
                
                df.to_csv(filepath, index=False, header=include_header, sep=delimiter)
                return filepath
            else:
                # 导出所有表
                filepaths = {}
                for table_name in self.table_data:
                    filepaths[table_name] = self.to_csv(table_name=table_name)
                return filepaths
        else:
            # 单表模式
            if not self.data:
                raise ValueError("请先生成数据")
            
            filepath = filepath or self._get_output_path('csv', 'data.csv')
            
            df = self.to_dataframe()
            
            # 确保目录存在
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # 获取配置
            outputs_config = self.config.get('outputs', {})
            csv_config = outputs_config.get('csv', {}).get('config', {})
            include_header = csv_config.get('include_header', True)
            delimiter = csv_config.get('delimiter', ',')
            
            df.to_csv(filepath, index=False, header=include_header, sep=delimiter)
            return filepath
    
    def to_json(self, filepath: Optional[str] = None, table_name: Optional[str] = None) -> Union[str, Dict[str, str]]:
        """
        将数据导出为JSON文件
        
        Args:
            filepath: 输出文件路径，如果为None则使用配置中的路径
            table_name: 表名（多表模式）
            
        Returns:
            文件路径（单表模式）或字典（多表模式）
        """
        if self.is_multi_table:
            # 多表模式
            if table_name:
                # 导出指定表
                if not self.table_data.get(table_name):
                    raise ValueError(f"表'{table_name}'没有生成数据")
                
                filepath = filepath or self._get_output_path('json', 'data.json', table_name)
                
                df = self.to_dataframe(table_name)
                
                # 确保目录存在
                Path(filepath).parent.mkdir(parents=True, exist_ok=True)
                
                # 获取配置
                outputs_config = self.config.get('outputs', {})
                json_config = outputs_config.get('json', {}).get('config', {})
                indent = json_config.get('indent', 2)
                array_format = json_config.get('array_format', True)
                
                if array_format:
                    df.to_json(filepath, orient='records', indent=indent)
                else:
                    df.to_json(filepath, indent=indent)
                return filepath
            else:
                # 导出所有表
                filepaths = {}
                for table_name in self.table_data:
                    filepaths[table_name] = self.to_json(table_name=table_name)
                return filepaths
        else:
            # 单表模式
            if not self.data:
                raise ValueError("请先生成数据")
            
            filepath = filepath or self._get_output_path('json', 'data.json')
            
            df = self.to_dataframe()
            
            # 确保目录存在
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # 获取配置
            outputs_config = self.config.get('outputs', {})
            json_config = outputs_config.get('json', {}).get('config', {})
            indent = json_config.get('indent', 2)
            array_format = json_config.get('array_format', True)
            
            if array_format:
                df.to_json(filepath, orient='records', indent=indent)
            else:
                df.to_json(filepath, indent=indent)
            
            return filepath
    
    def to_excel(self, filepath: Optional[str] = None) -> str:
        """
        将数据导出为Excel文件
        
        Args:
            filepath: 输出文件路径，如果为None则使用配置中的路径
            
        Returns:
            文件路径
        """
        filepath = filepath or self._get_output_path('excel', 'data.xlsx')
        
        # 确保目录存在
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # 获取配置
        outputs_config = self.config.get('outputs', {})
        excel_config = outputs_config.get('excel', {}).get('config', {})
        auto_filter = excel_config.get('auto_filter', True)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            if self.is_multi_table:
                # 多表模式：每个表一个工作表
                for table_name in self.table_data:
                    if self.table_data[table_name]:
                        df = self.to_dataframe(table_name)
                        df.to_excel(writer, sheet_name=table_name[:31], index=False)  # 工作表名最多31个字符
                        
                        # 如果启用了自动筛选
                        if auto_filter:
                            worksheet = writer.sheets[table_name[:31]]
                            worksheet.auto_filter.ref = worksheet.dimensions
            else:
                # 单表模式
                if not self.data:
                    raise ValueError("请先生成数据")
                
                df = self.to_dataframe()
                sheet_name = excel_config.get('sheet_name', 'Data')
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 如果启用了自动筛选
                if auto_filter:
                    worksheet = writer.sheets[sheet_name]
                    worksheet.auto_filter.ref = worksheet.dimensions
        
        return filepath
    
    def to_sql(self, filepath: Optional[str] = None, table_name: Optional[str] = None) -> Union[str, Dict[str, str]]:
        """
        将数据导出为SQL插入语句文件
        
        Args:
            filepath: 输出文件路径，如果为None则使用配置中的路径
            table_name: 表名（多表模式）
            
        Returns:
            文件路径（单表模式）或字典（多表模式）
        """
        if self.is_multi_table:
            # 多表模式
            if table_name:
                # 导出指定表
                if not self.table_data.get(table_name):
                    raise ValueError(f"表'{table_name}'没有生成数据")
                
                return self._export_single_table_sql(table_name, filepath)
            else:
                # 导出所有表到一个文件
                filepath = filepath or self._get_output_path('sql', 'data.sql')
                
                # 确保目录存在
                Path(filepath).parent.mkdir(parents=True, exist_ok=True)
                
                # 获取配置
                outputs_config = self.config.get('outputs', {})
                sql_config = outputs_config.get('sql', {}).get('config', {})
                dialect = sql_config.get('dialect', 'postgresql')
                batch_size = sql_config.get('batch_size', 100)
                include_create_table = sql_config.get('include_create_table', True)
                include_truncate_table = sql_config.get('include_truncate_table', True)
                insert_mode = sql_config.get('insert_mode', 'insert')
                
                # 生成SQL语句
                sql_lines = []
                
                # 导出每个表
                for table_name in self.table_data:
                    if self.table_data[table_name]:
                        table_sql = self._generate_table_sql(table_name, dialect, batch_size, include_create_table, include_truncate_table, insert_mode)
                        sql_lines.extend(table_sql)
                        sql_lines.append('')  # 添加空行分隔
                
                # 写入文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(sql_lines))
                
                return filepath
        else:
            # 单表模式
            if not self.data:
                raise ValueError("请先生成数据")
            
            return self._export_single_table_sql('test_data', filepath)
    
    def _export_single_table_sql(self, table_name: str, filepath: Optional[str] = None) -> str:
        """导出单个表的SQL"""
        if self.is_multi_table:
            if not self.table_data.get(table_name):
                raise ValueError(f"表'{table_name}'没有生成数据")
            df = self.to_dataframe(table_name)
        else:
            if not self.data:
                raise ValueError("请先生成数据")
            df = self.to_dataframe()
        
        filepath = filepath or self._get_output_path('sql', 'data.sql', table_name)
        
        # 确保目录存在
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # 获取配置
        outputs_config = self.config.get('outputs', {})
        sql_config = outputs_config.get('sql', {}).get('config', {})
        dialect = sql_config.get('dialect', 'postgresql')
        batch_size = sql_config.get('batch_size', 100)
        include_create_table = sql_config.get('include_create_table', True)
        include_truncate_table = sql_config.get('include_truncate_table', True)
        insert_mode = sql_config.get('insert_mode', 'insert')
        
        # 生成SQL语句
        sql_lines = self._generate_table_sql(table_name, dialect, batch_size, include_create_table, include_truncate_table, insert_mode)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_lines))
        
        return filepath
    
    def _generate_table_sql(self, table_name: str, dialect: str, batch_size: int, include_create_table: bool, include_truncate_table: bool, insert_mode: str) -> List[str]:
        """生成单个表的SQL语句列表"""
        sql_lines = []
        
        # 获取数据框
        df = self.to_dataframe(table_name)
        
        # 根据方言处理标识符
        if dialect.lower() == 'mysql':
            quote_char = '`'
        elif dialect.lower() == 'postgresql':
            quote_char = '"'
        else:
            quote_char = ''
        
        # 处理列名
        columns = [f"{quote_char}{col}{quote_char}" if quote_char else col for col in df.columns]
        
        # 生成创建表语句
        if include_create_table:
            create_table_sql = self._generate_create_table_sql(table_name, df, dialect, quote_char)
            sql_lines.append(create_table_sql)
        
        # 生成清空表语句
        if include_truncate_table:
            truncate_sql = f"TRUNCATE TABLE {table_name};"
            sql_lines.append(truncate_sql)
        
        # 分批生成SQL
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            # 构建VALUES部分
            values_lines = []
            for _, row in batch.iterrows():
                values = []
                for value in row:
                    if pd.isna(value):
                        values.append('NULL')
                    elif isinstance(value, str):
                        # 转义单引号
                        escaped_value = value.replace("'", "''")
                        values.append(f"'{escaped_value}'")
                    elif isinstance(value, bool):
                        values.append('TRUE' if value else 'FALSE')
                    elif isinstance(value, datetime):
                        values.append(f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'")
                    elif isinstance(value, (int, float)):
                        values.append(str(value))
                    else:
                        values.append(f"'{str(value)}'")
                
                values_lines.append(f"({', '.join(values)})")
            
            # 生成INSERT语句
            if insert_mode == 'insert':
                sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES\n"
                sql += ',\n'.join(values_lines) + ';'
            elif insert_mode == 'upsert' and dialect.lower() == 'postgresql':
                # PostgreSQL upsert
                sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES\n"
                sql += ',\n'.join(values_lines) + '\n'
                sql += f"ON CONFLICT DO NOTHING;"
            elif insert_mode == 'upsert' and dialect.lower() == 'mysql':
                # MySQL upsert
                sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES\n"
                sql += ',\n'.join(values_lines) + '\n'
                sql += "ON DUPLICATE KEY UPDATE;"
            elif insert_mode == 'replace' and dialect.lower() == 'mysql':
                # MySQL replace
                sql = f"REPLACE INTO {table_name} ({', '.join(columns)}) VALUES\n"
                sql += ',\n'.join(values_lines) + ';'
            else:
                # 默认使用普通插入
                sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES\n"
                sql += ',\n'.join(values_lines) + ';'
            
            sql_lines.append(sql)
        
        return sql_lines
    
    def _generate_create_table_sql(self, table_name: str, df: pd.DataFrame, dialect: str, quote_char: str) -> str:
        """
        生成创建表的SQL语句
        
        Args:
            table_name: 表名
            df: 数据框
            dialect: SQL方言
            quote_char: 引号字符
            
        Returns:
            创建表的SQL语句
        """
        # 映射pandas类型到SQL类型
        type_mapping = {
            'int64': 'INTEGER',
            'float64': 'FLOAT',
            'bool': 'BOOLEAN',
            'datetime64[ns]': 'TIMESTAMP',
            'object': 'VARCHAR(255)'
        }
        
        # 生成列定义
        columns_def = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            sql_type = type_mapping.get(dtype, 'VARCHAR(255)')
            # 处理NULL值
            if df[col].isna().any():
                null_constraint = 'NULL'
            else:
                null_constraint = 'NOT NULL'
            columns_def.append(f"{quote_char}{col}{quote_char} {sql_type} {null_constraint}")
        
        # 生成创建表语句
        if dialect.lower() == 'mysql':
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        else:  # postgresql
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        
        create_sql += ',\n'.join(columns_def)
        create_sql += '\n);'
        
        return create_sql
    
    def export_all(self) -> Dict[str, Any]:
        """
        导出所有启用的格式
        
        Returns:
            各格式输出文件的路径字典
        """
        outputs = {}
        outputs_config = self.config.get('outputs', {})
        
        # CSV
        if outputs_config.get('csv', {}).get('enabled', False):
            outputs['csv'] = self.to_csv()
        
        # JSON
        if outputs_config.get('json', {}).get('enabled', False):
            outputs['json'] = self.to_json()
        
        # Excel
        if outputs_config.get('excel', {}).get('enabled', False):
            outputs['excel'] = self.to_excel()
        
        # SQL
        if outputs_config.get('sql', {}).get('enabled', False):
            outputs['sql'] = self.to_sql()
        
        return outputs
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取数据生成摘要
        
        Returns:
            摘要信息字典
        """
        if self.is_multi_table:
            # 多表模式
            summary = {
                'total_tables': len(self.tables),
                'tables': {}
            }
            
            for table_name, table_data in self.table_data.items():
                if table_data:
                    df = self.to_dataframe(table_name)
                    table_summary = {
                        'total_rows': len(table_data),
                        'total_fields': len(df.columns),
                        'field_types': {},
                        'field_stats': {}
                    }
                    
                    # 统计字段类型
                    table_config = self.tables[table_name]
                    fields_config = self.tables_config[table_name].get('fields', {})
                    for field_name, field_config in fields_config.items():
                        field_type = field_config.get('type', 'unknown')
                        if field_type not in table_summary['field_types']:
                            table_summary['field_types'][field_type] = 0
                        table_summary['field_types'][field_type] += 1
                    
                    # 计算基本统计信息
                    for column in df.columns:
                        if pd.api.types.is_numeric_dtype(df[column]):
                            table_summary['field_stats'][column] = {
                                'min': float(df[column].min()),
                                'max': float(df[column].max()),
                                'mean': float(df[column].mean()),
                                'std': float(df[column].std())
                            }
                        elif pd.api.types.is_datetime64_any_dtype(df[column]):
                            table_summary['field_stats'][column] = {
                                'min': df[column].min().strftime('%Y-%m-%d'),
                                'max': df[column].max().strftime('%Y-%m-%d')
                            }
                        else:
                            # 对于字符串类型，计算唯一值数量和最频繁的值
                            unique_count = df[column].nunique()
                            most_common = df[column].value_counts().head(3).to_dict()
                            table_summary['field_stats'][column] = {
                                'unique_count': unique_count,
                                'most_common': most_common
                            }
                    
                    summary['tables'][table_name] = table_summary
            
            return summary
        else:
            # 单表模式
            if not self.data:
                raise ValueError("请先生成数据")
            
            df = self.to_dataframe()
            summary = {
                'total_rows': len(self.data),
                'total_fields': len(self.fields),
                'field_types': {},
                'field_stats': {}
            }
            
            # 统计字段类型
            fields_config = self.config.get('fields', {})
            for field_name, field_config in fields_config.items():
                field_type = field_config.get('type', 'unknown')
                if field_type not in summary['field_types']:
                    summary['field_types'][field_type] = 0
                summary['field_types'][field_type] += 1
            
            # 计算基本统计信息
            for column in df.columns:
                if pd.api.types.is_numeric_dtype(df[column]):
                    summary['field_stats'][column] = {
                        'min': float(df[column].min()),
                        'max': float(df[column].max()),
                        'mean': float(df[column].mean()),
                        'std': float(df[column].std())
                    }
                elif pd.api.types.is_datetime64_any_dtype(df[column]):
                    summary['field_stats'][column] = {
                        'min': df[column].min().strftime('%Y-%m-%d'),
                        'max': df[column].max().strftime('%Y-%m-%d')
                    }
                else:
                    # 对于字符串类型，计算唯一值数量和最频繁的值
                    unique_count = df[column].nunique()
                    most_common = df[column].value_counts().head(3).to_dict()
                    summary['field_stats'][column] = {
                        'unique_count': unique_count,
                        'most_common': most_common
                    }
            
            return summary