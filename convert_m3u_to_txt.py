# convert_m3u_to_txt.py

import re
import os
import sys

def convert_m3u_to_txt(m3u_file_path, txt_file_path):
    """
    将M3U文件转换为TXT格式，正确处理多行播放源
    格式为：
    分组名称,#genre#
    频道1,URL1
    频道1,URL2
    频道1,URL3
    """
    if not os.path.exists(m3u_file_path):
        print(f"错误：找不到M3U文件 {m3u_file_path}")
        return False
    
    try:
        with open(m3u_file_path, 'r', encoding='utf-8') as m3u:
            content = m3u.read()
    except UnicodeDecodeError:
        try:
            with open(m3u_file_path, 'r', encoding='gbk') as m3u:
                content = m3u.read()
        except:
            print("错误：无法解码M3U文件")
            return False

    # 使用正则表达式匹配每个频道块
    pattern = r'#EXTINF:.*?tvg-name="([^"]*)".*?group-title="([^"]*)",([^\n]+)\n((?:http[^\n]+\n)*)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    group_channels = {}
    
    for match in matches:
        tvg_name = match[0]  # tvg-name
        group_title = match[1]  # group-title
        channel_name = match[2]  # 显示名称
        urls_text = match[3]  # 所有URL
        
        # 提取所有URL
        urls = re.findall(r'(http[^\s\n]+)', urls_text)
        
        if group_title not in group_channels:
            group_channels[group_title] = []
        
        # 为每个URL创建一行
        for url in urls:
            # 清理URL
            url = url.strip()
            if url:
                group_channels[group_title].append(f"{channel_name},{url}")
    
    # 写入TXT文件
    try:
        with open(txt_file_path, 'w', encoding='utf-8') as txt:
            for group, channels in group_channels.items():
                if channels:  # 只写入有频道的分组
                    # 写入分组标题
                    txt.write(f"{group},#genre#\n")
                    # 写入该分组下的所有频道URL
                    for channel_line in channels:
                        txt.write(f"{channel_line}\n")
                    # 分组之间空一行
                    txt.write("\n")
        
        # 统计信息
        total_sources = sum(len(channels) for channels in group_channels.values())
        total_groups = len([g for g in group_channels if group_channels[g]])
        
        print(f"转换完成！")
        print(f"共处理 {total_groups} 个分组，{total_sources} 个播放源")
        
        # 显示详细统计
        print("\n分组详细统计:")
        for group in sorted(group_channels.keys()):
            channels = group_channels[group]
            if channels:
                print(f"  {group}: {len(channels)} 个播放源")
                
        return True
        
    except Exception as e:
        print(f"写入TXT文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_m3u_structure(m3u_file_path):
    """调试M3U文件结构"""
    print(f"\n正在分析M3U文件结构: {m3u_file_path}")
    
    try:
        with open(m3u_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        try:
            with open(m3u_file_path, 'r', encoding='gbk') as f:
                lines = f.readlines()
        except:
            print("无法读取文件")
            return
    
    print(f"文件总行数: {len(lines)}")
    
    # 统计EXTINF行和URL行
    extinf_count = 0
    url_count = 0
    current_channel = ""
    
    for i, line in enumerate(lines[:50]):  # 只显示前50行进行分析
        line = line.strip()
        if line.startswith('#EXTINF:'):
            extinf_count += 1
            # 提取频道名
            name_match = re.search(r'tvg-name="([^"]*)"', line)
            if name_match:
                current_channel = name_match.group(1)
            else:
                current_channel = "未知"
            print(f"行{i+1}: EXTINF -> {current_channel}")
        elif line.startswith('http'):
            url_count += 1
            print(f"行{i+1}: URL -> {line[:50]}...")
        elif line and not line.startswith('#'):
            print(f"行{i+1}: 其他 -> {line[:50]}...")
    
    print(f"\n统计: {extinf_count} 个频道头, {url_count} 个URL")

if __name__ == "__main__":
    # 尝试不同的M3U文件名
    possible_m3u_files = ["ipvym3a", "ipzy.m3u", "iptv.m3a", "iptv.m3u", "iptv.m3u"]
    m3u_file = None
    txt_file = "ipzy.txt"
    
    for file in possible_m3u_files:
        if os.path.exists(file):
            m3u_file = file
            break
    
    if not m3u_file:
        print("错误：找不到M3U文件")
        print("当前目录文件列表:")
        for f in os.listdir('.'):
            print(f"  {f}")
        sys.exit(1)
    
    print(f"找到M3U文件: {m3u_file}")
    
    # 调试文件结构
    debug_m3u_structure(m3u_file)
    
    # 执行转换
    success = convert_m3u_to_txt(m3u_file, txt_file)
    
    if success:
        print(f"\n✅ 成功将 {m3u_file} 转换为 {txt_file}")
        
        # 显示文件预览
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            print(f"\n📊 输出文件统计:")
            print(f"总行数: {len(lines)}")
            print(f"文件大小: {len(content)} 字节")
            
            print("\n👀 文件预览 (前30行):")
            print("=" * 60)
            for i, line in enumerate(lines[:30]):
                if line.strip():
                    print(f"{i+1:2d}: {line}")
            print("=" * 60)
            
            # 检查CCTV4K的转换结果
            cctv4k_sources = [line for line in lines if 'CCTV4K' in line and line.startswith('CCTV4K,')]
            if cctv4k_sources:
                print(f"\n📺 CCTV4K 播放源数量: {len(cctv4k_sources)}")
                for source in cctv4k_sources[:3]:  # 显示前3个
                    print(f"  {source}")
                if len(cctv4k_sources) > 3:
                    print(f"  ... 还有 {len(cctv4k_sources) - 3} 个源")
                    
        except Exception as e:
            print(f"读取输出文件时出错: {e}")
    else:
        print("❌ 转换失败")
