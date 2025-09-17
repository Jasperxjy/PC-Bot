#!/usr/bin/env python3
import argparse
from pathlib import Path

from ..core.enhancer import enhance_text
from ..config import settings


def enhance_existing_texts(texts_dir: Path, output_dir: Path = settings.ENHANCED_DIR):
    """增强指定目录中的所有文本文件"""
    text_files = list(texts_dir.glob('*.txt'))

    for i, text_file in enumerate(text_files):
        print(f"处理文件 {i + 1}/{len(text_files)}: {text_file.name}")

        # 检查是否已存在增强版本
        enhanced_file = output_dir / text_file.name
        if enhanced_file.exists():
            print("  已存在增强版本，跳过")
            continue

        # 增强文本
        enhanced_path = enhance_text(text_file)
        if enhanced_path:
            print(f"  增强成功: {enhanced_path.name}")
        else:
            print("  增强失败")


def main():
    parser = argparse.ArgumentParser(description='增强已转录的文本')
    parser.add_argument('texts_dir', help='包含原始转录文本的目录')

    args = parser.parse_args()

    texts_dir = Path(args.texts_dir)
    if not texts_dir.exists():
        print(f"目录不存在: {texts_dir}")
        return

    enhance_existing_texts(texts_dir)


if __name__ == '__main__':
    main()