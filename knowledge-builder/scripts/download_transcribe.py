#!/usr/bin/env python3
"""
单独的视频下载和转录脚本
仅处理视频下载和语音转录，不包含文本增强功能
"""

import argparse
import csv
import subprocess
from pathlib import Path
from typing import List, Optional
import time

# 默认配置
DEFAULT_AUDIO_DIR = Path("./audio")
DEFAULT_TRANSCRIPTS_DIR = Path("./transcripts")
DEFAULT_MODEL = "medium"
DEFAULT_LANGUAGE = "zh"
DEFAULT_DEVICE = "cpu"  # 使用CPU运行


def check_dependencies():
    """检查必要的依赖是否安装"""
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        subprocess.run(['whisper', '--help'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 请确保已安装 yt-dlp 和 whisper")
        print("安装命令:")
        print("  pip install yt-dlp whisper")
        return False


def download_audio(url: str, output_dir: Path) -> tuple[Optional[Path], Optional[str]]:
    """下载视频音频并返回文件路径和文件名"""
    try:
        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)

        # 设置下载命令
        cmd = [
            'yt-dlp',
            '-x',
            '--audio-format', 'mp3',
            '-o', f'{output_dir}/%(title)s.%(ext)s',
            url
        ]

        print(f"  下载音频: {url}")
        # 执行下载
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # 从输出中提取文件名
        lines = result.stderr.split('\n')
        for line in lines:
            if '[ExtractAudio] Destination:' in line:
                filepath = line.split('Destination:')[-1].strip()
                audio_path = Path(filepath)
                filename = audio_path.name
                return audio_path, filename

        # 如果无法从输出中提取文件名，尝试从目录中获取最新的mp3文件
        mp3_files = list(output_dir.glob('*.mp3'))
        if mp3_files:
            # 按修改时间排序，获取最新的文件
            mp3_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            filename = mp3_files[0].name
            return mp3_files[0], filename

        return None, None
    except subprocess.CalledProcessError as e:
        print(f"  下载失败: {e}")
        return None, None


def transcribe_audio(audio_path: Path, output_dir: Path, model: str, language: str, device: str) -> Optional[Path]:
    """转录音频文件并返回文本文件路径"""
    try:
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 构建转录命令
        cmd = [
            'whisper',
            str(audio_path),
            '--model', model,
            '--language', language,
            '--output_dir', str(output_dir),
            '--device', device
        ]

        print(f"  转录音频: {audio_path.name}")
        # 执行转录
        subprocess.run(cmd, check=True)

        # 确定输出的txt文件路径
        base_name = audio_path.stem
        txt_file = output_dir / f"{base_name}.txt"

        return txt_file if txt_file.exists() else None
    except subprocess.CalledProcessError as e:
        print(f"  转录失败: {e}")
        return None


def read_csv(csv_path: Path) -> List[List[str]]:
    """读取CSV文件内容"""
    rows = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:  # 跳过空行
                    rows.append(row)
        return rows
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return []


def write_csv(csv_path: Path, rows: List[List[str]]):
    """写入CSV文件"""
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
    except Exception as e:
        print(f"写入CSV文件失败: {e}")


def process_videos(csv_path: Path, audio_dir: Path, transcripts_dir: Path,
                   model: str, language: str, device: str, update_csv: bool):
    """处理CSV文件中的所有视频"""
    # 读取CSV文件
    rows = read_csv(csv_path)
    if not rows:
        # 创建带标题行的CSV
        rows = [['url', 'extracted', 'enhanced', 'filename']]
        write_csv(csv_path, rows)
        return
    elif len(rows[0]) < 4 or rows[0][3] != 'filename':
        # 更新标题行，确保包含filename列
        if len(rows[0]) < 4:
            rows[0].append('filename')
        else:
            rows[0][3] = 'filename'

    # 处理每个URL
    for i, row in enumerate(rows):
        if i == 0:  # 跳过标题行
            continue

        # 确保行有足够的列
        while len(row) < 4:
            if len(row) == 3:
                row.append('')  # 为filename添加空值
            else:
                row.append("False")

        url, extracted, enhanced, filename = row

        # 如果已经提取过，跳过
        if extracted.lower() in ['true', '1', 'yes', 'y']:
            print(f"跳过已处理的URL ({i}/{len(rows) - 1}): {url}")
            continue

        print(f"处理URL ({i}/{len(rows) - 1}): {url}")

        # 下载音频
        audio_file, filename = download_audio(url, audio_dir)
        if not audio_file:
            continue

        print(f"  音频下载成功: {filename}")

        # 转录音频
        transcript_file = transcribe_audio(audio_file, transcripts_dir, model, language, device)
        if not transcript_file:
            continue

        print(f"  转录成功: {transcript_file.name}")

        # 更新CSV行
        row[1] = 'True'  # 标记为已提取
        row[3] = filename  # 存储文件名

        # 如果选择更新CSV文件，则立即写入
        if update_csv:
            write_csv(csv_path, rows)

        # 添加短暂延迟，避免过于频繁的请求
        time.sleep(1)

    # 最终更新CSV文件
    if not update_csv:
        write_csv(csv_path, rows)

    print("所有URL处理完成")


def main():
    parser = argparse.ArgumentParser(description='批量下载视频并转录为文本（不包含增强功能）')
    parser.add_argument('csv_file', help='包含视频URL的CSV文件路径')
    parser.add_argument('--audio_dir', default='./audio', help='音频文件保存目录')
    parser.add_argument('--transcripts_dir', default='./transcripts', help='转录文本保存目录')
    parser.add_argument('--model', default='medium', choices=['tiny', 'base', 'small', 'medium', 'large'],
                        help='Whisper模型大小')
    parser.add_argument('--language', default='zh', help='音频语言代码')
    parser.add_argument('--device', default='cpu', choices=['cpu', 'cuda'],
                        help='使用CPU或GPU运行')
    parser.add_argument('--no-update-csv', action='store_false', dest='update_csv',
                        help='不实时更新CSV文件，只在最后更新')

    args = parser.parse_args()

    # 检查依赖
    if not check_dependencies():
        return

    # 处理路径
    csv_path = Path(args.csv_file)
    audio_dir = Path(args.audio_dir)
    transcripts_dir = Path(args.transcripts_dir)

    if not csv_path.exists():
        print(f"CSV文件不存在: {csv_path}")
        return

    # 处理视频
    process_videos(
        csv_path,
        audio_dir,
        transcripts_dir,
        args.model,
        args.language,
        args.device,
        args.update_csv
    )


if __name__ == '__main__':
    main()