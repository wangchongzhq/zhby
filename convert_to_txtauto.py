#!/usr/bin/env python3
"""
转换脚本：将M3U格式转换为TXT格式
"""

import os
import re
import datetime
from collections import defaultdict

def m3u_to_txt(m3u_file, txt_file):
    """将M3U文件转换为TXT格式"""
    
    if not os.path.exists(m3u_file):
        print(f"❌ 文件不存在: {m3u_file}")
        return False
    
    try:
        with open(m3u_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        channels = []
        current_channel = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('#EXTINF:'):
                # 提取频道名称
                if ',' in line:
                    current_channel = line.split(',')[-1].strip()
            elif line and not line.startswith('#') and current_channel:
                # 这是URL行
                channels.append((current_channel, line))
                current_channel = None
        
        # 写入TXT文件
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("# IPTV直播源 - 从M3U转换\n")
            f.write(f"# 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# 源文件: {m3u_file}\n")
            f.write("# 格式: 频道名称,播放URL\n\n")
            
            for channel_name, url in channels:
                f.write(f"{channel_name},{url}\n")
        
        print(f"✅ 转换完成: {m3u_file} -> {txt_file}")
        print(f"📊 转换了 {len(channels)} 个频道")
        return True
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return False

def main():
    """主函数"""
    m3u_file = "ipzy.m3u"  # 输入的M3U文件
    txt_file = "ipzyauto.txt"  # 输出的TXT文件
    
    if m3u_to_txt(m3u_file, txt_file):
        print(f"🎉 成功生成TXT文件: {txt_file}")
    else:
        print("💥 转换失败")

if __name__ == "__main__":
    main()
