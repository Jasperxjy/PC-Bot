from pathlib import Path
from ..config import settings
from ..utils.ollama_client import OllamaClient


def enhance_text(text_path: Path, output_dir: Path = settings.ENHANCED_DIR) -> Path:
    """增强文本内容并返回增强后的文件路径"""
    try:
        # 读取原始文本
        with open(text_path, 'r', encoding='utf-8') as f:
            original_text = f.read()

        # 准备提示词
        prompt = settings.ENHANCE_PROMPT.format(text=original_text)

        # 调用Ollama
        client = OllamaClient()
        enhanced_text = client.generate(prompt)

        if not enhanced_text:
            return None

        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存增强后的文本
        output_path = output_dir / text_path.name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_text)

        return output_path
    except Exception as e:
        print(f"文本增强失败: {e}")
        return None