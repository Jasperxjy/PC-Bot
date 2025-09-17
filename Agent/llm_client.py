# -*- coding: utf-8 -*-
"""
LLM客户端模块

此模块实现了与Ollama模型进行交互的功能，提供了发送请求和获取响应的方法。
"""
import json
import requests
import logging
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OllamaClient:
    """
    Ollama模型客户端类，负责与Ollama服务进行交互
    """
    
    def __init__(self, host: str = "localhost", port: int = 11434, timeout: int = 30):
        """
        初始化Ollama客户端
        
        参数:
            host: Ollama服务主机地址
            port: Ollama服务端口
            timeout: 请求超时时间（秒）
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}/api"
        
    def generate_completion(self, model: str, prompt: str, system_prompt: Optional[str] = None, 
                           temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        向Ollama模型发送请求，获取生成的补全内容
        
        参数:
            model: 模型名称
            prompt: 用户提示词
            system_prompt: 系统提示词（可选）
            temperature: 生成文本的随机性
            max_tokens: 最大生成tokens数
        
        返回:
            str: 模型生成的响应文本
        """
        try:
            # 构建请求数据
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # 如果有系统提示词，添加到请求数据中
            if system_prompt:
                data["system"] = system_prompt
            
            # 发送请求
            url = f"{self.base_url}/generate"
            response = requests.post(url, json=data, timeout=self.timeout)
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 返回生成的文本
            return result.get("response", "")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama请求失败: {e}")
            raise Exception(f"与Ollama服务通信失败: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Ollama响应解析失败: {e}")
            raise Exception(f"解析Ollama响应失败: {str(e)}")
        except Exception as e:
            logger.error(f"Ollama客户端错误: {e}")
            raise
    
    def chat_completion(self, model: str, messages: list, 
                       temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        使用Ollama的聊天接口进行多轮对话
        
        参数:
            model: 模型名称
            messages: 消息列表，每条消息包含role和content
            temperature: 生成文本的随机性
            max_tokens: 最大生成tokens数
        
        返回:
            Dict: 包含响应内容的字典
        """
        try:
            # 构建请求数据
            data = {
                "model": model,
                "messages": messages,
                "stream": False,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # 发送请求
            url = f"{self.base_url}/chat"
            response = requests.post(url, json=data, timeout=self.timeout)
            
            # 检查响应状态
            response.raise_for_status()
            
            # 返回解析后的响应
            return response.json()
            
        except Exception as e:
            logger.error(f"Ollama聊天请求失败: {e}")
            raise Exception(f"Ollama聊天接口调用失败: {str(e)}")
    
    def check_connection(self) -> bool:
        """
        检查与Ollama服务的连接是否正常
        
        返回:
            bool: 连接是否正常
        """
        try:
            # 获取模型列表作为连接测试
            url = f"{self.base_url}/tags"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return True
        except Exception:
            logger.warning("无法连接到Ollama服务")
            return False
    
    def get_available_models(self) -> list:
        """
        获取Ollama服务中可用的模型列表
        
        返回:
            list: 可用模型列表
        """
        try:
            url = f"{self.base_url}/tags"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except Exception:
            logger.error("获取模型列表失败")
            return []

class LLMClient:
    """
    通用LLM客户端类，封装了对不同LLM服务的访问
    当前版本仅支持Ollama服务
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化LLM客户端
        
        参数:
            config: LLM配置字典
        """
        self.config = config
        self.client = None
        
        # 根据配置创建对应的客户端
        if config.get("type") == "ollama":
            self.client = OllamaClient(
                host=config.get("host", "localhost"),
                port=config.get("port", 11434),
                timeout=config.get("timeout", 30)
            )
        else:
            raise ValueError(f"不支持的LLM类型: {config.get('type')}")
        
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        生成文本响应
        
        参数:
            prompt: 用户提示词
            system_prompt: 系统提示词（可选）
        
        返回:
            str: 生成的文本响应
        """
        if not self.client:
            raise Exception("LLM客户端未初始化")
        
        return self.client.generate_completion(
            model=self.config.get("model"),
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=self.config.get("temperature", 0.7),
            max_tokens=self.config.get("max_tokens", 1000)
        )
    
    def chat(self, messages: list) -> Dict[str, Any]:
        """
        进行多轮对话
        
        参数:
            messages: 消息列表
        
        返回:
            Dict: 对话响应
        """
        if not self.client:
            raise Exception("LLM客户端未初始化")
        
        return self.client.chat_completion(
            model=self.config.get("model"),
            messages=messages,
            temperature=self.config.get("temperature", 0.7),
            max_tokens=self.config.get("max_tokens", 1000)
        )
    
    def is_available(self) -> bool:
        """
        检查LLM服务是否可用
        
        返回:
            bool: 服务是否可用
        """
        if not self.client or not hasattr(self.client, 'check_connection'):
            return False
        
        return self.client.check_connection()

# 创建一个全局的LLM客户端实例，方便在其他地方直接使用
def get_llm_client(config: Optional[Dict[str, Any]] = None) -> LLMClient:
    """
    获取LLM客户端实例
    
    参数:
        config: LLM配置字典，如果为None则使用默认配置
    
    返回:
        LLMClient: LLM客户端实例
    """
    from .config import LLM_CONFIG
    
    # 如果提供了配置则使用提供的，否则使用默认配置
    final_config = config or LLM_CONFIG
    
    # 创建并返回客户端实例
    return LLMClient(final_config)

# 测试代码
if __name__ == "__main__":
    try:
        # 从配置文件导入配置
        from config import LLM_CONFIG
        
        # 创建客户端
        client = LLMClient(LLM_CONFIG)
        
        # 检查连接
        if client.is_available():
            print("已成功连接到Ollama服务")
            
            # 获取可用模型
            models = client.client.get_available_models()
            print(f"可用模型: {[model['name'] for model in models]}")
            
            # 发送测试请求
            response = client.generate(
                prompt="请简要介绍一下电脑装机的主要配件",
                system_prompt="你是一个专业的电脑装机顾问"
            )
            print(f"模型响应: {response}")
        else:
            print("无法连接到Ollama服务，请检查服务是否已启动")
    except Exception as e:
        print(f"测试失败: {e}")