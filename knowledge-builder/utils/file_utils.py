import csv
from pathlib import Path
from typing import List
from ..core.models import VideoTask

def read_video_tasks(csv_path: Path) -> List[VideoTask]:
    """从CSV文件读取视频任务"""
    tasks = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过标题行
        for row in reader:
            if row:  # 确保行不为空
                task = VideoTask(
                    url=row[0],
                    extracted=row[1].lower() in ('true', '1', 'yes', 'y') if len(row) > 1 else False,
                    enhanced=row[2].lower() in ('true', '1', 'yes', 'y') if len(row) > 2 else False,
                    filename=row[3] if len(row) > 3 else None
                )
                tasks.append(task)
    return tasks

def write_video_tasks(csv_path: Path, tasks: List[VideoTask]):
    """将视频任务写入CSV文件"""
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['url', 'extracted', 'enhanced', 'filename'])
        for task in tasks:
            writer.writerow([task.url, task.extracted, task.enhanced, task.filename or ''])