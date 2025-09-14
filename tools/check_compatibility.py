import json
import re
from querytools import hardware_query  # 导入之前写的查询工具

class CompatibilityChecker:
    def __init__(self):
        # 定义一个兼容性规则字典
        # 规则可以扩展，这里是核心示例
        self.rules = {
            'cpu_motherboard': self._check_cpu_motherboard,
            'motherboard_ram': self._check_motherboard_memory,
            'motherboard_case': self._check_motherboard_case,
            'gpu_case': self._check_gpu_case,
            'gpu_power': self._check_gpu_power,
            'power_motherboard': self._check_power_motherboard
        }

    def check_compatibility(self, component_a, component_b):
        """
        检查两个部件的兼容性
        参数 component_a, component_b: 从query_hardware查询返回的部件字典
        返回: (is_compatible: bool, message: str, confidence: float)
        """
        # 确定检查的类型（例如：cpu和motherboard）
        cat_a, cat_b = component_a['category'], component_b['category']
        check_type = f"{cat_a}_{cat_b}"

        # 优先使用规则引擎
        if check_type in self.rules:
            compatible, message, confidence = self.rules[check_type](component_a, component_b)
            # 如果规则引擎有高置信度的结果，直接返回
            if confidence > 0.8:
                return compatible, message, confidence
            # 如果规则引擎置信度低（例如因为数据不规范），则降级到LLM
            else:
                print(f"规则引擎置信度低({confidence})，降级到LLM检查...")
                return self._check_with_llm(component_a, component_b)
        else:
            # 对于没有预定义规则的部件类型，直接使用LLM
            print(f"无预定义规则 {check_type}，使用LLM检查...")
            return self._check_with_llm(component_a, component_b)

    # --- 规则引擎的具体实现 ---
    def _check_cpu_motherboard(self, cpu, motherboard):
        """规则：CPU插槽必须与主板插槽匹配"""
        socket_cleaner = lambda s: re.sub(r'[^a-z0-9]', '', s.lower().replace(' ', ''))
        cpu_socket = socket_cleaner(cpu['specs'].get('socket', ''))
        mobo_socket = socket_cleaner(motherboard['specs'].get('socket', ''))

        if cpu_socket and mobo_socket:
            if cpu_socket == mobo_socket:
                return True, f"兼容: CPU插槽({cpu['specs']['socket']})与主板插槽匹配", 1.0
            return False, f"不兼容: CPU({cpu['specs']['socket']})与主板({motherboard['specs']['socket']})插槽不匹配", 1.0
        return None, "无法确定: 插槽信息缺失", 0.5

    def _check_motherboard_memory(self, motherboard, memory):
        # 适配JSON中的memory_support格式 (如 "DDR4, DDR5")
        supported_types = re.findall(r'ddr[345]', motherboard['specs'].get('memory_support', '').lower())
        mem_type = re.search(r'ddr[345]', memory['specs'].get('memory_type', '').lower())

        if not supported_types or not mem_type:
            return None, "内存类型信息缺失", 0.5

        mem_type = mem_type.group()
        if mem_type in supported_types:
            return True, f"兼容: 主板支持{mem_type.upper()}内存", 1.0
        return False, f"不兼容: 主板支持{supported_types}，内存是{mem_type.upper()}", 0.9


    def _check_motherboard_case(self, motherboard, case):
        """规则：主板尺寸必须被机箱支持"""
        mobo_form_factor = motherboard['specs'].get('form_factor', '').lower()  # 如 'atx', 'microatx', 'mini-itx'
        case_support = case['specs'].get('supported_form_factors', '').lower()  # 如 'atx, microatx, mini-itx'

        if not mobo_form_factor or not case_support:
            return None, f"无法确定: 主板版型或机箱支持信息缺失。", 0.5

        if mobo_form_factor in case_support:
            return True, f"兼容: {mobo_form_factor.upper()}主板可安装于此机箱。", 1.0
        else:
            return False, f"不兼容: 机箱不支持{mobo_form_factor.upper()}主板。", 0.9

    def _check_gpu_case(self, gpu, case):
        """检查显卡尺寸与机箱兼容性"""
        try:
            gpu_length = float(re.search(r'\d+', gpu['specs'].get('length', '')).group())
            case_max_gpu = float(re.search(r'\d+', case['specs'].get('max_gpu_length', '')).group())
        except:
            return None, "尺寸信息不完整", 0.5

        if gpu_length <= case_max_gpu:
            return True, f"兼容: 显卡长度({gpu_length}mm)在机箱支持范围内", 1.0
        return False, f"不兼容: 显卡过长({gpu_length}mm > {case_max_gpu}mm)", 0.9

    def _check_gpu_power(self, gpu, power):
        """检查显卡电源接口和功率"""
        required_power = gpu['specs'].get('recommended_psu', 0)
        psu_power = power['specs'].get('output_power', 0)

        # 接口检查（示例：8-pin接口）
        psu_connectors = power['specs'].get('pcie_connectors', 0)
        gpu_required = gpu['specs'].get('power_connectors', 0)

        if not all([required_power, psu_power, psu_connectors, gpu_required]):
            return None, "电源规格信息不完整", 0.6

        messages = []
        if psu_power < required_power:
            messages.append(f"电源功率不足({psu_power}W < {required_power}W)")
        if psu_connectors < gpu_required:
            messages.append(f"电源接口不足({psu_connectors}个 < 需要{gpu_required}个)")

        if messages:
            return False, "；".join(messages), 0.9
        return True, "电源满足需求", 0.9

    def _check_power_motherboard(self, power, motherboard):
        """检查电源主板供电接口"""
        required_connector = motherboard['specs'].get('power_connector', '')
        psu_connector = power['specs'].get('motherboard_connector', '')

        if not required_connector or not psu_connector:
            return None, "接口信息缺失", 0.5

        if psu_connector.lower() == required_connector.lower():
            return True, f"主板{required_connector}供电接口匹配", 1.0
        return False, f"接口不匹配({psu_connector} vs {required_connector})", 0.9
    # --- LLM 后备方案 ---
    def _check_with_llm(self, component_a, component_b):
        """
        使用LLM作为后备方案进行兼容性检查
        注意: 这里需要你自行替换为真实的LLM API调用
        """
        # 构建一个清晰的Prompt
        prompt = f"""
请严格扮演一个电脑硬件专家，只根据提供的硬件信息判断以下两个部件是否兼容。

部件A ( {component_a['category']} ):
- 名称: {component_a['name']}
- 品牌: {component_a['brand']}
- 型号: {component_a['model']}
- 关键规格: {json.dumps(component_a['specs'], ensure_ascii=False)}

部件B ( {component_b['category']} ):
- 名称: {component_b['name']}
- 品牌: {component_b['brand']}
- 型号: {component_b['model']}
- 关键规格: {json.dumps(component_b['specs'], ensure_ascii=False)}

请只输出一个JSON对象，格式如下：
{{"compatible": <true|false>, "reason": "一句话解释原因", "confidence": <0.0到1.0之间的数字>}}
"""
        # TODO: 这里替换成你调用 DeepSeek/QWen 等LLM API的代码
        # simulated_llm_output = call_llm_api(prompt)
        simulated_llm_output = '{"compatible": true, "reason": "基于LLM分析的兼容性原因", "confidence": 0.7}'

        try:
            result = json.loads(simulated_llm_output)
            return result['compatible'], result['reason'], result['confidence']
        except json.JSONDecodeError:
            # 如果LLM没有返回标准JSON，说明可能出错
            return False, "LLM兼容性检查失败，请手动确认。", 0.0

# 创建全局检查器实例
compatibility_checker = CompatibilityChecker()

# 示例使用
if __name__ == "__main__":

    # 测试：获取一个CPU和一个主板
    cpus = hardware_query.query_hardware(category="cpu", filters={"brand": "AMD"})
    mobos = hardware_query.query_hardware(category="motherboard", filters={"brand": "MSI"})

    if cpus and mobos:
        cpu = cpus[0]
        mobo = mobos[0]

        is_ok, message, confidence = compatibility_checker.check_compatibility(cpu, mobo)
        print(cpu['name'])
        print(mobo['name'])
        print(f"兼容性: {is_ok}")
        print(f"原因: {message}")
        print(f"置信度: {confidence}")