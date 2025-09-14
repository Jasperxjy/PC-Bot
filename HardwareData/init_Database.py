import json
import sqlite3
import os
from glob import glob


def init_database():
    # 连接数据库（如果不存在则创建）
    conn = sqlite3.connect('../hardware.db')
    cursor = conn.cursor()

    # 创建硬件表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hardware (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        price REAL,
        specs TEXT,  -- 存储为JSON字符串
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 创建索引以提高查询性能
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON hardware(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_brand ON hardware(brand)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_price ON hardware(price)')

    # 清空现有数据（如果之前已有）
    cursor.execute('DELETE FROM hardware')

    # 获取所有JSON文件
    json_files = glob('*.json')

    # 插入数据
    for file_path in json_files:
        category = file_path.replace('.json', '')  # 从文件名获取类别
        print(f"正在处理 {category} 数据...")

        with open(file_path, 'r', encoding='utf-8') as f:
            items = json.load(f)

            for item in items:
                # 将specs字典转换为JSON字符串
                specs_json = json.dumps(item['specs'], ensure_ascii=False)

                cursor.execute('''
                INSERT INTO hardware (name, category, brand, model, price, specs)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (item['name'], item['category'], item['brand'], item['model'], item['price'], specs_json))

    # 提交更改并关闭连接
    conn.commit()
    conn.close()
    print("数据库初始化完成！")


if __name__ == "__main__":
    init_database()
