import sqlite3
import json
import os

class HardwareQueryTool:
    def __init__(self, db_path='../hardware.db'):
        self.db_path = db_path

    def query_hardware(self, category=None, filters=None):
        """
        查询硬件信息

        参数:
        category (str): 硬件类别 (cpu, gpu, motherboard, 等)
        filters (dict): 过滤条件，例如:
            {
                "brand": "Intel",
                "max_price": 1500,
                "min_core_count": 6,
                "socket": "LGA 1700"
            }

        返回:
        list: 匹配的硬件列表
        """
        if filters is None:
            filters = {}

        # 构建基础查询
        query = "SELECT name, category, brand, model, price, specs FROM hardware WHERE 1=1"
        params = []

        # 添加类别过滤
        if category:
            query += " AND category = ?"
            params.append(category)

        # 添加基础过滤条件 (品牌、价格范围)
        if "brand" in filters:
            query += " AND brand = ?"
            params.append(filters["brand"])

        if "min_price" in filters:
            query += " AND price >= ?"
            params.append(filters["min_price"])

        if "max_price" in filters:
            query += " AND price <= ?"
            params.append(filters["max_price"])

        # 执行查询
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 使返回的行可像字典一样访问
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()

        # 转换为字典列表
        items = []
        for row in results:
            item = dict(row)
            item['specs'] = json.loads(item['specs'])  # 解析JSON字符串
            items.append(item)

        conn.close()

        # 应用高级过滤条件 (基于specs字段)
        if filters:
            items = self._apply_spec_filters(items, filters)

        return items

    def _apply_spec_filters(self, items, filters):
        """应用基于specs字段的高级过滤"""
        filtered_items = []

        for item in items:
            match = True

            # 检查每个过滤条件
            for key, value in filters.items():
                if key in ["brand", "min_price", "max_price"]:
                    continue  # 这些已经在SQL查询中处理

                # 特殊处理嵌套属性
                if "." in key:
                    # 例如: "benchmarks.cinebench_r23_single"
                    parts = key.split(".")
                    current_value = item['specs']
                    for part in parts:
                        if part in current_value:
                            current_value = current_value[part]
                        else:
                            current_value = None
                            break

                    if current_value is None or not self._value_matches(current_value, value):
                        match = False
                        break
                else:
                    # 检查一级属性
                    if key in item['specs']:
                        if not self._value_matches(item['specs'][key], value):
                            match = False
                            break
                    else:
                        # 如果过滤条件不存在于specs中，跳过此项
                        match = False
                        break

            if match:
                filtered_items.append(item)

        return filtered_items

    def _value_matches(self, actual_value, filter_value):
        """检查实际值是否匹配过滤值"""
        if isinstance(filter_value, str) and filter_value.startswith(">="):
            try:
                threshold = float(filter_value[2:])
                return float(actual_value) >= threshold
            except (ValueError, TypeError):
                return False
        elif isinstance(filter_value, str) and filter_value.startswith("<="):
            try:
                threshold = float(filter_value[2:])
                return float(actual_value) <= threshold
            except (ValueError, TypeError):
                return False
        elif isinstance(filter_value, str) and filter_value.startswith(">"):
            try:
                threshold = float(filter_value[1:])
                return float(actual_value) > threshold
            except (ValueError, TypeError):
                return False
        elif isinstance(filter_value, str) and filter_value.startswith("<"):
            try:
                threshold = float(filter_value[1:])
                return float(actual_value) < threshold
            except (ValueError, TypeError):
                return False
        else:
            # 直接相等比较
            return str(actual_value) == str(filter_value)

    def get_categories(self):
        """获取所有可用的硬件类别"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM hardware")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories

    def get_brands_by_category(self, category):
        """获取指定类别下的所有品牌"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT brand FROM hardware WHERE category = ?", (category,))
        brands = [row[0] for row in cursor.fetchall()]
        conn.close()
        return brands


# 创建全局查询工具实例
hardware_query = HardwareQueryTool()

# 示例使用
if __name__ == "__main__":
    # 初始化数据库（如果尚未初始化）
    if not os.path.exists('../hardware.db'):
        from HardwareData.init_Database import init_Database

        init_Database()

    # 示例查询1: 查找所有Intel CPU
    print("所有Intel CPU:")
    intel_cpus = hardware_query.query_hardware(
        category="cpu",
        filters={"brand": "Intel"}
    )
    for cpu in intel_cpus:
        print(f"- {cpu['name']}: ¥{cpu['price']}")

    # 示例查询2: 查找价格在1000-1500元之间的CPU，且核心数>=6
    print("\n价格在1000-1500元之间，核心数>=6的CPU:")
    mid_range_cpus = hardware_query.query_hardware(
        category="CPUs",
        filters={
            "min_price": 1000,
            "max_price": 1500,
            "core_count": ">=6"
        }
    )
    for cpu in mid_range_cpus:
        print(f"- {cpu['name']}: ¥{cpu['price']}, {cpu['specs']['core_count']}核")

    # 示例查询3: 查找支持PCIe 5.0的CPU
    print("\n支持PCIe 5.0的CPU:")
    pcie5_cpus = hardware_query.query_hardware(
        category="CPUs",
        filters={"pcie_support": "PCIe 5.0 & 4.0"}
    )
    for cpu in pcie5_cpus:
        print(f"- {cpu['name']}: {cpu['specs']['pcie_support']}")