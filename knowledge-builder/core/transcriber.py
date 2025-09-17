import subprocess
from pathlib import Path
from ..config import settings


def transcribe_audio(audio_path: Path, output_dir: Path = settings.TRANSCRIPTS_DIR) -> Path:
    """转录音频文件并返回文本文件路径"""
    try:
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 构建转录命令
        cmd = [
            'whisper',
            str(audio_path),
            '--model', settings.WHISPER_MODEL,
            '--language', settings.WHISPER_LANGUAGE,
            '--output_dir', str(output_dir),
            '--device', settings.WHISPER_DEVICE
        ]

        # 执行转录
        subprocess.run(cmd, check=True)

        # 确定输出的txt文件路径
        base_name = audio_path.stem
        txt_file = output_dir / f"{base_name}.txt"

        return txt_file if txt_file.exists() else None
    except subprocess.CalledProcessError as e:
        print(f"转录失败: {e}")
        return None