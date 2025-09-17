#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import List

from ..core.models import VideoTask
from ..utils.file_utils import read_video_tasks, write_video_tasks
from ..core.downloader import download_audio
from ..core.transcriber import transcribe_audio
from ..core.enhancer import enhance_text
from ..config import settings


def process_videos(csv_path: Path, skip_enhanced: bool = True):
    """处理CSV文件中的所有视频"""
    # 读取任务
    tasks = read_video_tasks(csv_path)

    # 处理每个任务
    for i, task in enumerate(tasks):
        print(f"处理任务 {i + 1}/{len(tasks)}: {task.url}")

        # 如果已经增强过且选择跳过，则跳过
        if skip_enhanced and task.enhanced:
            print("  已增强，跳过")
            continue

        # 如果尚未提取音频
        if not task.extracted:
            # 下载音频
            audio_path, filename = download_audio(task.url)
            if not audio_path:
                print("  下载失败")
                continue
            task.audio_path = audio_path
            task.filename = filename
            print(f"  下载成功: {filename}")

            # 转录音频
            transcript_path = transcribe_audio(audio_path)
            if not transcript_path:
                print("  转录失败")
                continue
            task.transcript_path = transcript_path
            task.extracted = True
            print(f"  转录成功: {transcript_path.name}")

            # 更新CSV，包括文件名
            write_video_tasks(csv_path, tasks)

        # 如果已提取但未增强
        if task.extracted and not task.enhanced:
            # 增强文本
            enhanced_path = enhance_text(task.transcript_path)
            if not enhanced_path:
                print("  增强失败")
                continue
            task.enhanced_path = enhanced_path
            task.enhanced = True
            print(f"  增强成功: {enhanced_path.name}")

            # 更新CSV
            write_video_tasks(csv_path, tasks)

    print("所有任务处理完成")


def main():
    parser = argparse.ArgumentParser(description='处理视频并增强转录文本')
    parser.add_argument('csv_file', help='包含视频URL的CSV文件')
    parser.add_argument('--skip-enhanced', action='store_true', default=True,
                        help='跳过已增强的视频')

    args = parser.parse_args()

    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"CSV文件不存在: {csv_path}")
        return

    process_videos(csv_path, args.skip_enhanced)


if __name__ == '__main__':
    main()