"""
扩展字段类型
包含常用数据类型的字段类
"""
import random
import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import hashlib

from .base import Field, StringField, ChoiceField


class NameField(StringField):
    """姓名字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config, metadata)
        self.gender = config.get('gender', 'both')  # male, female, both
        self.locale = config.get('locale', 'zh_CN')  # 地区设置
        
    def generate(self, row_data: Optional[Dict[str, Any]] = None) -> str:
        # 这里可以集成Faker库来生成真实姓名
        # 暂时使用简单的方法
        first_names_male = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴']
        first_names_female = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴']
        
        last_names = [
            '伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
            '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞',
            '平', '刚', '桂英', '建华', '宇', '红', '林', '阳', '建平', '文'
        ]
        
        if self.gender == 'male':
            first_name = random.choice(first_names_male)
        elif self.gender == 'female':
            first_name = random.choice(first_names_female)
        else:
            first_name = random.choice(first_names_male + first_names_female)
        
        last_name = random.choice(last_names)
        
        # 随机决定是否使用2字名
        if random.random() > 0.5:
            last_name2 = random.choice(last_names)
            while last_name2 == last_name:
                last_name2 = random.choice(last_names)
            last_name = last_name + last_name2
        
        return f"{first_name}{last_name}"
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        
        # 简单的中文姓名验证
        if not re.match(r'^[\u4e00-\u9fa5]{2,4}$', value):
            return False
        
        return 2 <= len(value) <= 4


class AddressField(StringField):
    """地址字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config, metadata)
        self.include_detail = config.get('include_detail', True)
        self.locale = config.get('locale', 'zh_CN')
        
    def generate(self, row_data: Optional[Dict[str, Any]] = None) -> str:
        # 省份
        provinces = [
            '北京市', '上海市', '天津市', '重庆市', '河北省', '山西省', '辽宁省',
            '吉林省', '黑龙江省', '江苏省', '浙江省', '安徽省', '福建省', '江西省',
            '山东省', '河南省', '湖北省', '湖南省', '广东省', '海南省', '四川省',
            '贵州省', '云南省', '陕西省', '甘肃省', '青海省', '台湾省', '内蒙古自治区',
            '广西壮族自治区', '西藏自治区', '宁夏回族自治区', '新疆维吾尔自治区'
        ]
        
        # 城市
        cities = {
            '北京市': ['北京市'],
            '上海市': ['上海市'],
            '天津市': ['天津市'],
            '重庆市': ['重庆市'],
            '河北省': ['石家庄市', '唐山市', '秦皇岛市', '邯郸市', '邢台市', '保定市', '张家口市', '承德市', '沧州市', '廊坊市', '衡水市'],
            '江苏省': ['南京市', '无锡市', '徐州市', '常州市', '苏州市', '南通市', '连云港市', '淮安市', '盐城市', '扬州市', '镇江市', '泰州市', '宿迁市']
        }
        
        # 街道
        streets = ['中山路', '解放路', '人民路', '建设路', '新华路', '文化路', '和平路', '胜利路', '前进路', '光明路']
        
        province = random.choice(provinces)
        city = random.choice(cities.get(province, ['未知市']))
        district = f"{random.randint(1, 10)}区"
        street = random.choice(streets)
        building_number = random.randint(1, 999)
        
        address = f"{province}{city}{district}"
        
        if self.include_detail:
            address += f"{street}{building_number}号"
        
        return address
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        
        return len(value) >= 6


class PhoneField(StringField):
    """手机号码字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config, metadata)
        self.prefix = config.get('prefix', '1')
        self.operator = config.get('operator')  # 运营商：移动、联通、电信
        
    def generate(self, row_data: Optional[Dict[str, Any]] = None) -> str:
        # 中国手机号前缀
        prefixes = {
            '移动': ['134', '135', '136', '137', '138', '139', '147', '150', '151', '152', '157', '158', '159', '172', '178', '182', '183', '184', '187', '188', '198'],
            '联通': ['130', '131', '132', '145', '155', '156', '166', '171', '175', '176', '185', '186'],
            '电信': ['133', '149', '153', '173', '177', '180', '181', '189', '199']
        }
        
        if self.operator and self.operator in prefixes:
            prefix = random.choice(prefixes[self.operator])
        else:
            # 随机选择运营商前缀
            all_prefixes = []
            for op_prefixes in prefixes.values():
                all_prefixes.extend(op_prefixes)
            prefix = random.choice(all_prefixes)
        
        # 生成后8位
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        
        return f"{prefix}{suffix}"
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        
        # 简单的手机号验证
        return bool(re.match(r'^1[3-9]\d{9}$', value))


class IDCardField(StringField):
    """身份证号码字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config, metadata)
        self.gender = config.get('gender')  # 性别：M或F
        self.birth_date_range = config.get('birth_date_range', ['1960-01-01', '2005-12-31'])
        
    def generate(self, row_data: Optional[Dict[str, Any]] = None) -> str:
        # 地区码（前6位）
        area_codes = [
            '110101', '110102', '110105', '110106',  # 北京
            '310101', '310104', '310105', '310106',  # 上海
            '440101', '440103', '440104', '440105',  # 广州
            '510104', '510105', '510106', '510107',  # 成都
        ]
        area_code = random.choice(area_codes)
        
        # 出生日期（8位）
        start_date = datetime.strptime(self.birth_date_range[0], '%Y-%m-%d')
        end_date = datetime.strptime(self.birth_date_range[1], '%Y-%m-%d')
        days_diff = (end_date - start_date).days
        random_days = random.randint(0, days_diff)
        birth_date = start_date + timedelta(days=random_days)
        birth_date_str = birth_date.strftime('%Y%m%d')
        
        # 顺序码（3位）
        sequence_code = str(random.randint(1, 999)).zfill(3)
        
        # 根据性别调整顺序码
        if self.gender == 'M':
            # 男性为奇数
            sequence_code = str(int(sequence_code) | 1).zfill(3)
        elif self.gender == 'F':
            # 女性为偶数
            sequence_code = str(int(sequence_code) & ~1).zfill(3)
        
        # 前17位
        first_17 = f"{area_code}{birth_date_str}{sequence_code}"
        
        # 计算校验码（第18位）
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        total = sum(int(first_17[i]) * weights[i] for i in range(17))
        check_code = check_codes[total % 11]
        
        return f"{first_17}{check_code}"
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, str) or len(value) != 18:
            return False
        
        # 验证校验码
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10,25489, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        try:
            first_17 = value[:17]
            check_code = value[17]
            
            total = sum(int(first_17[i]) * weights[i] for i in range(17))
            expected_check_code = check_codes[total % 11]
            
            return check_code == expected_check_code
        except:
            return False


class TimestampField(Field):
    """时间戳字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config, metadata)
        self.start_timestamp = config.get('start_timestamp', 1577836800)  # 2020-01-01
        self.end_timestamp = config.get('end_timestamp', 1704067200)  # 2024-01-01
        self.format = config.get('format')  # timestamp, datetime_string, date_string
        
    def generate(self, row_data: Optional[Dict[str, Any]] = None) -> Any:
        timestamp = random.randint(self.start_timestamp, self.end_timestamp)
        
        if self.format == 'datetime_string':
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        elif self.format == 'date_string':
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        else:
            return timestamp
    
    def validate(self, value: Any) -> bool:
        try:
            if isinstance(value, (int, float)):
                return self.start_timestamp <= value <= self.end_timestamp
            elif isinstance(value, str):
                # 尝试解析字符串
                if ':' in value:
                    dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                else:
                    dt = datetime.strptime(value, '%Y-%m-%d')
                timestamp = dt.timestamp()
                return self.start_timestamp <= timestamp <= self.end_timestamp
            return False
        except:
            return False


class IPAddressField(StringField):
    """IP地址字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config, metadata)
        self.ip_version = config.get('version', 4)  # 4或6
        self.network = config.get('network')  # 如: 192.168.0.0/24
        
    def generate(self, row_data: Optional[Dict[str, Any]] = None) -> str:
        if self.ip_version == 6:
            # 生成IPv6地址
            segments = []
            for _ in range(8):
                segment = ''.join(random.choice('0123456789abcdef') for _ in range(4))
                segments.append(segment)
            return ':'.join(segments)
        else:
            # 生成IPv4地址
            if self.network:
                # 根据网络生成IP
                network_parts = self.network.split('/')
                base_ip = network_parts[0]
                mask = int(network_parts[1]) if len(network_parts) > 1 else 24
                
                # 生成网络内的随机IP
                base_parts = list(map(int, base_ip.split('.')))
                # 这里简化处理，实际应该更精确
                base_parts[3] = random.randint(1, 254)
                return '.'.join(map(str, base_parts))
            else:
                # 生成随机公网IP
                return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        
        if self.ip_version == 6:
            # 简单的IPv6验证
            return bool(re.match(r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$', value))
        else:
            # IPv4验证
            parts = value.split('.')
            if len(parts) != 4:
                return False
            
            try:
                for part in parts:
                    num = int(part)
                    if num < 0 or num > 255:
                        return False
                return True
            except:
                return False


class MoneyField(Field):
    """金额字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config, metadata)
        self.min_value = config.get('min', 0.0)
        self.max_value = config.get('max', 10000.0)
        self.precision = config.get('precision', 2)
        self.currency = config.get('currency', 'CNY')
        self.distribution = config.get('distribution', 'uniform')
        self.mean = config.get('mean', 5000.0)
        self.std_dev = config.get('std_dev', 1000.0)
        
    def generate(self, row_data: Optional[Dict[str, Any]] = None) -> float:
        if self.distribution == 'normal':
            value = random.normalvariate(self.mean, self.std_dev)
        else:  # uniform
            value = random.uniform(self.min_value, self.max_value)
        
        # 确保在范围内
        value = max(self.min_value, min(self.max_value, value))
        
        # 四舍五入到指定精度
        return round(value, self.precision)
    
    def validate(self, value: Any) -> bool:
        try:
            float_value = float(value)
            return self.min_value <= float_value <= self.max_value
        except:
            return False


class URLField(StringField):
    """URL字段"""
    
    def __init__(self, name: str, config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        super().__init__(name, config, metadata)
        self.protocols = config.get('protocols', ['http', 'https'])
        self.domains = config.get('domains', ['example.com', 'test.com', 'demo.org'])
        self.path_depth = config.get('path_depth', 3)
        
    def generate(self, row_data: Optional[Dict[str, Any]] = None) -> str:
        protocol = random.choice(self.protocols)
        domain = random.choice(self.domains)
        
        # 生成路径
        path_parts = []
        path_words = ['api', 'users', 'products', 'orders', 'categories', 'admin', 'dashboard', 'settings']
        
        for i in range(random.randint(1, self.path_depth)):
            part = random.choice(path_words)
            if part not in path_parts:
                path_parts.append(part)
        
        path = '/' + '/'.join(path_parts)
        
        # 随机添加查询参数
        query_params = []
        if random.random() > 0.5:
            params = ['id', 'page', 'limit', 'sort', 'filter', 'search']
            for _ in range(random.randint(1, 3)):
                param = random.choice(params)
                value = str(random.randint(1, 100))
                query_params.append(f"{param}={value}")
            
            if query_params:
                path += '?' + '&'.join(query_params)
        
        return f"{protocol}://{domain}{path}"
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        
        # 简单的URL验证
        url_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?$'
        return bool(re.match(url_pattern, value))


# 扩展字段类型映射
EXTENDED_FIELD_MAPPING = {
    'name': NameField,
    'address': AddressField,
    'phone': PhoneField,
    'id_card': IDCardField,
    'timestamp': TimestampField,
    'ip_address': IPAddressField,
    'money': MoneyField,
    'url': URLField,
}