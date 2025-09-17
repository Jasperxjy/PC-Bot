# -*- coding: utf-8 -*-
"""
装机助手Agent配置文件

此文件包含装机助手Agent的配置信息，特别是LLM服务的配置。
"""

# LLM服务配置
LLM_CONFIG = {
    "type": "ollama",  # LLM服务类型
    "host": "localhost",  # ollama服务主机
    "port": 11434,  # ollama服务端口
    "model": "qwen3:14b-q4_K_M",  # 使用的模型名称
    "timeout": 30,  # 请求超时时间（秒）
    "temperature": 0.7,  # 生成文本的随机性
    "max_tokens": 1000  # 最大生成 tokens 数
}

# 其他Agent配置
AGENT_CONFIG = {
    "debug": True,  # 是否开启调试模式
    "max_discussion_turns": 10,  # 最大讨论轮数
    "configurations_to_generate": 3  # 默认生成的配置方案数量
}

# 系统提示词配置
SYSTEM_PROMPTS = {
    "demand_analysis": """
    你是一个电脑装机助手，需要分析用户输入，提取关键需求信息。
    请从用户输入中提取以下信息：
    1. 预算（如果有）
    2. 主要用途（游戏、办公、设计等）
    3. 品牌偏好（如果有）
    4. 其他特殊要求（如果有）
    
    请以JSON格式返回提取的信息，格式如下：
    {
        "budget": 预算金额（整数，单位元），如果没有则为null,
        "scenarios": [主要用途列表]，如果没有则为空列表,
        "preferred_brands": {"cpu": "品牌", "gpu": "品牌"}，如果没有则为空对象,
        "other_requirements": "其他要求"，如果没有则为空字符串
    }
    """,
    
    "response_generation": """
    你是一个电脑装机助手，需要根据当前收集的用户需求生成自然语言响应。
    当前已收集的需求信息：{user_demand}
    讨论历史：{history}
    
    请根据以下规则生成响应：
    1. 如果尚未收集到预算信息，请询问用户预算
    2. 如果尚未收集到主要用途，请询问用户主要用途
    3. 如果已收集到足够信息，请确认用户需求并表示可以开始生成配置
    4. 保持语言友好、专业，符合装机助手的角色
    """,
    
    "feedback_analysis": """
    你是一个电脑装机助手，需要分析用户对配置方案的反馈。
    当前配置方案：{current_config}
    用户反馈：{user_feedback}
    
    请分析用户反馈并确定如何处理：
    1. 如果用户表示满意，请确认配置
    2. 如果用户有修改意见，请明确用户希望修改的部分
    3. 请以JSON格式返回分析结果，格式如下：
    {
        "is_satisfied": true/false,
        "modification_points": [需要修改的部分列表]，如果不需要修改则为空列表,
        "modification_details": "修改细节描述"，如果不需要修改则为空字符串
    }
    """
}

# 兼容性检查配置
COMPATIBILITY_CONFIG = {
    "strict_mode": False,  # 是否使用严格的兼容性检查模式
    "warning_threshold": 0.7  # 兼容性警告阈值
}

# 配置生成策略
CONFIG_GENERATION_STRATEGIES = {
    "balanced": {"cpu": 0.25, "gpu": 0.35, "motherboard": 0.15, "ram": 0.08, "storage": 0.10, "psu": 0.05, "case": 0.02},
    "cpu_focused": {"cpu": 0.30, "gpu": 0.30, "motherboard": 0.17, "ram": 0.10, "storage": 0.10, "psu": 0.05, "case": 0.02},
    "gpu_focused": {"cpu": 0.20, "gpu": 0.40, "motherboard": 0.15, "ram": 0.08, "storage": 0.10, "psu": 0.07, "case": 0.02}
}