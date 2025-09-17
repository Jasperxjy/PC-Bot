import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).resolve().parent.parent
FFMPEG_DIR = "D:\\ffmpeg\\ffmpeg-master-latest-win64-gpl-shared\\bin\\ffmpeg.exe"

# 数据路径
DATA_DIR = BASE_DIR / "data"
AUDIO_DIR = DATA_DIR / "audio"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
ENHANCED_DIR = DATA_DIR / "enhanced"

# 模型设置
WHISPER_MODEL = "medium"
WHISPER_LANGUAGE = "zh"
WHISPER_DEVICE = "cpu"  # 使用CPU运行

# Ollama设置
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "qwen3:14b-q4_K_M"  # 或其他你使用的模型

# 提示词模板
ENHANCE_PROMPT = """
请对以下文本进行总结和增强，使其更适合作为知识库内容：

{text}

要求：
1. 保持核心信息不变
2. 组织结构清晰，分段合理
3. 去除口语化表达和冗余内容
4. 增加相关背景知识（如果适用）
5. 使用专业但易懂的语言

请直接返回增强后的文本内容，不要添加额外说明。
"""