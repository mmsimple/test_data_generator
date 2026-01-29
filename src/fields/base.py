"""
字段基础类
"""

import random
import uuid
from datetime import datetime, date, timedelta
from typing import Any, Dict, Optional, List, Callable
from abc import ABC, abstractmethod
import math


class Field(ABC):
    """字段基类"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """
        初始化字段
        
        Args:
            name: 字段名称
            config: 字段配置
            metadata: 字段元数据
        """
        self.name = name
        self.config = config or {}
        self.metadata = metadata or {}
        self.dependencies = self.config.get('dependencies', [])
        
    @abstractmethod
    def generate(self, row_data: Optional[Dict[str, Any]] = None) -> Any:
        """
        生成字段值
        
        Args:
            row_data: 当前行的其他字段数据（用于依赖字段）
            
        Returns:
            生成的字段值
        """
        pass
    
    def validate(self, value: Any) -> bool:
        """
        验证字段值
        
        Args:
            value: 要验证的值
            
        Returns:
            是否有效
        """
        return True
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取字段元数据"""
        return self.metadata.copy()
    
    def __str__(self) -> str:
        return f"Field(name={self.name}, type={self.__class__.__name__})"


class StringField(Field):
    """字符串字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config or {}, metadata)
        self.generator = self.config.get('generator', 'random_string')
        self.min_length = self.config.get('min_length', 5)
        self.max_length = self.config.get('max_length', 20)
        self.prefix = self.config.get('prefix', '')
        self.suffix = self.config.get('suffix', '')
        
    def generate(self, row_data: Dict[str, Any] = None) -> str:
        import string
        
        if self.generator == 'uuid':
            return str(uuid.uuid4())
        
        length = random.randint(self.min_length, self.max_length)
        chars = string.ascii_letters + string.digits
        
        if self.generator == 'alpha':
            chars = string.ascii_letters
        elif self.generator == 'numeric':
            chars = string.digits
        elif self.generator == 'alphanumeric':
            chars = string.ascii_letters + string.digits
        
        random_string = ''.join(random.choice(chars) for _ in range(length))
        return f"{self.prefix}{random_string}{self.suffix}"
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        
        length = len(value)
        if length < self.min_length or length > self.max_length:
            return False
        
        return True


class IntegerField(Field):
    """整数字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config, metadata)
        self.min_value = self.config.get('min', 0)
        self.max_value = self.config.get('max', 100)
        self.distribution = self.config.get('distribution', 'uniform')
        self.start = self.config.get('start', 1)
        self.increment = self.config.get('increment', 1)
        self.mean = self.config.get('mean', 50)
        self.std_dev = self.config.get('std_dev', 10)
        self._current_value = self.start - self.increment
        
    def generate(self, row_data: Dict[str, Any] = None) -> int:
        if self.distribution == 'sequential':
            self._current_value += self.increment
            return self._current_value
        
        elif self.distribution == 'normal':
            # 生成正态分布的随机数
            value = random.normalvariate(self.mean, self.std_dev)
            # 限制在最小最大值之间
            value = max(self.min_value, min(self.max_value, int(value)))
            return int(value)
        
        else:  # uniform
            return random.randint(self.min_value, self.max_value)
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, int):
            return False
        
        return self.min_value <= value <= self.max_value


class FloatField(Field):
    """浮点数字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config, metadata)
        self.min_value = self.config.get('min', 0.0)
        self.max_value = self.config.get('max', 100.0)
        self.precision = self.config.get('precision', 2)
        self.distribution = self.config.get('distribution', 'uniform')
        self.mean = self.config.get('mean', 50.0)
        self.std_dev = self.config.get('std_dev', 10.0)
        
    def generate(self, row_data: Dict[str, Any] = None) -> float:
        if self.distribution == 'normal':
            value = random.normalvariate(self.mean, self.std_dev)
        else:  # uniform
            value = random.uniform(self.min_value, self.max_value)
        
        # 四舍五入到指定精度
        return round(value, self.precision)
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, (int, float)):
            return False
        
        return self.min_value <= float(value) <= self.max_value


class BooleanField(Field):
    """布尔字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config, metadata)
        self.true_probability = self.config.get('true_probability', 0.5)
        
    def generate(self, row_data: Dict[str, Any] = None) -> bool:
        return random.random() < self.true_probability
    
    def validate(self, value: Any) -> bool:
        return isinstance(value, bool)


class DateField(Field):
    """日期字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config, metadata)
        
        start_date_str = self.config.get('start_date', '2000-01-01')
        end_date_str = self.config.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        self.date_format = self.config.get('format', '%Y-%m-%d')
        
        self.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        self.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        self.distribution = self.config.get('distribution', 'uniform')
        
    def generate(self, row_data: Dict[str, Any] = None) -> date:
        days_diff = (self.end_date - self.start_date).days
        
        if days_diff <= 0:
            return self.start_date
        
        random_days = random.randint(0, days_diff)
        random_date = self.start_date + timedelta(days=random_days)
        
        return random_date
    
    def generate_formatted(self, row_data: Dict[str, Any] = None) -> str:
        """生成格式化后的日期字符串"""
        date_value = self.generate(row_data)
        return date_value.strftime(self.date_format)
    
    def validate(self, value: Any) -> bool:
        if isinstance(value, str):
            try:
                datetime.strptime(value, self.date_format).date()
                return True
            except ValueError:
                return False
        elif isinstance(value, date):
            return self.start_date <= value <= self.end_date
        return False


class ChoiceField(Field):
    """选择字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config, metadata)
        self.choices = self.config.get('choices', [])
        self.weights = self.config.get('weights', [])
        
        # 如果权重数量不匹配，使用均匀权重
        if len(self.weights) != len(self.choices):
            self.weights = [1.0 / len(self.choices)] * len(self.choices)
        
    def generate(self, row_data: Optional[Dict[str, Any]] = None) -> Any:
        if not self.choices:
            return None
        
        return random.choices(self.choices, weights=self.weights, k=1)[0]
    
    def validate(self, value: Any) -> bool:
        return value in self.choices


class EmailField(StringField):
    """邮箱字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        config['generator'] = 'email'
        super().__init__(name, config, metadata)
        self.domain = self.config.get('domain', 'example.com')
        
    def generate(self, row_data: Dict[str, Any] = None) -> str:
        import string
        
        # 生成用户名部分
        username_length = random.randint(5, 15)
        chars = string.ascii_lowercase + string.digits
        username = ''.join(random.choice(chars) for _ in range(username_length))
        
        return f"{username}@{self.domain}"
    
    def validate(self, value: Any) -> bool:
        import re
        if not isinstance(value, str):
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, value))


class UUIDField(Field):
    """UUID字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config, metadata)
        self.version = self.config.get('version', 4)
        
    def generate(self, row_data: Dict[str, Any] = None) -> str:
        if self.version == 1:
            return str(uuid.uuid1())
        elif self.version == 3:
            namespace = uuid.NAMESPACE_DNS
            name = self.config.get('name', 'example.com')
            return str(uuid.uuid3(namespace, name))
        elif self.version == 5:
            namespace = uuid.NAMESPACE_DNS
            name = self.config.get('name', 'example.com')
            return str(uuid.uuid5(namespace, name))
        else:  # version 4
            return str(uuid.uuid4())
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        
        try:
            uuid_obj = uuid.UUID(value)
            return True
        except ValueError:
            return False


# 基础字段类型映射
BASE_FIELD_TYPE_MAPPING = {
    'string': StringField,
    'integer': IntegerField,
    'float': FloatField,
    'boolean': BooleanField,
    'date': DateField,
    'datetime': DateField,  # 暂时使用DateField
    'choice': ChoiceField,
    'uuid': UUIDField,
    'email': EmailField
}

# 扩展字段类型映射
try:
    from .extended import EXTENDED_FIELD_MAPPING
    FIELD_TYPE_MAPPING = {**BASE_FIELD_TYPE_MAPPING, **EXTENDED_FIELD_MAPPING}
except ImportError:
    FIELD_TYPE_MAPPING = BASE_FIELD_TYPE_MAPPING


def create_field(field_name: str, field_config: Dict[str, Any]) -> Field:
    """
    根据配置创建字段实例
    
    Args:
        field_name: 字段名称
        field_config: 字段配置
        
    Returns:
        字段实例
    """
    field_type = field_config.get('type')
    
    if field_type not in FIELD_TYPE_MAPPING:
        raise ValueError(f"不支持的字段类型: {field_type}")
    
    field_class = FIELD_TYPE_MAPPING[field_type]
    config = field_config.get('config', {})
    metadata = field_config.get('metadata', {})
    
    # 确保config不为None
    if config is None:
        config = {}
    
    return field_class(field_name, config, metadata)