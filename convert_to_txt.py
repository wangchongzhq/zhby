# convert_to_txt.py

import re
import os

def convert_m3u_to_txt(m3u_file_path, txt_file_path):
    """
    将M3U文件转换为TXT格式，格式为：
    分组名称,#genre#
    频道名称,URL1
    频道名称,URL2
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
        
        # 提取所有URL（每行一个URL）
        urls = re.findall(r'(http[^\s\n]+)', urls_text)
        
        if group_title not in group_channels:
            group_channels[group_title] = []
        
        # 为每个URL创建一行
        for url in urls:
            # 清理URL
            url = url.strip()
            if url:
                # 格式：频道名称,URL
                group_channels[group_title].append(f"{channel_name},{url}")
    
    # 写入TXT文件
    try:
        with open(txt_file_path, 'w', encoding='utf-8') as txt:
            # 按分组名称排序，让输出更整齐
            for group in sorted(group_channels.keys()):
                channels = group_channels[group]
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
        
        print(f"✅ 转换完成！")
        print(f"📊 共处理 {total_groups} 个分组，{total_sources} 个播放源")
        
        # 显示详细统计
        print("\n📺 分组详细统计:")
        for group in sorted(group_channels.keys()):
            channels = group_channels[group]
            if channels:
                print(f"  {group}: {len(channels)} 个播放源")
                
        return True
        
    except Exception as e:
        print(f"❌ 写入TXT文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    m3u_file = "ipzy.m3u"
    txt_file = "ipzyauto.txt"  # 修改为ipzyauto.txt
    
    print("🎬 开始转换M3U文件为TXT格式...")
    print(f"📁 输入文件: {m3u_file}")
    print(f"📁 输出文件: {txt_file}")
    
    if not os.path.exists(m3u_file):
        print(f"❌ 错误：找不到M3U文件 {m3u_file}")
        print("当前目录文件列表:")
        for f in os.listdir('.'):
            print(f"  {f}")
        return
    
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
            
            # 显示每个分组的前几个频道作为预览
            print("\n👀 文件结构预览:")
            print("=" * 60)
            current_group = ""
            preview_count = 0
            for line in lines[:50]:  # 预览前50行
                if line.endswith(',#genre#'):
                    current_group = line.replace(',#genre#', '')
                    print(f"\n📁 {current_group}:")
                    preview_count = 0
                elif line and ',' in line and not line.endswith(',#genre#'):
                    if preview_count < 3:  # 每个分组显示前3个频道
                        channel, url = line.split(',', 1)
                        print(f"  📺 {channel} -> {url[:50]}...")
                        preview_count += 1
                elif not line:
                    preview_count = 0  # 重置计数器
            print("=" * 60)
                    
        except Exception as e:
            print(f"读取输出文件时出错: {e}")
    else:
        print("❌ 转换失败")

if __name__ == "__main__":
    main()
