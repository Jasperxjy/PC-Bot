import subprocess
from pathlib import Path
from typing import Tuple, Optional
from ..config import settings


def download_audio(url: str, output_dir: Path = settings.AUDIO_DIR) -> Tuple[Optional[Path], Optional[str]]:
    """下载视频音频并返回文件路径和文件名"""
    try:
        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)

        # 设置下载命令
        cmd = [
            'yt-dlp',
            '--ffmpeg-location', settings.FFMPEG_DIR,
            '-x',
            '--audio-format', 'mp3',
            '-o', f'{output_dir}/%(title)s.%(ext)s',
            url
        ]

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
        print(f"下载失败: {e}")
        return None, None