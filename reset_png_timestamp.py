#!/usr/bin/env python3
"""
PNG 图片时间戳重置工具

功能：
1. 将指定目录下所有 PNG 图片的【创建时间】、【修改时间】、【访问时间】均设置为 1970-01-01 00:00:00
2. 支持递归处理子目录
3. 提供详细的处理日志

使用方法：
    python reset_png_timestamp.py <目录路径>
    python reset_png_timestamp.py <目录路径> --recursive

示例：
    python reset_png_timestamp.py ./images
    python reset_png_timestamp.py ./output/images --recursive
"""

import os
import sys
import argparse
import platform
from pathlib import Path
from datetime import datetime
import ctypes
from ctypes import wintypes, byref

# Windows API 定义
if platform.system() == 'Windows':
    kernel32 = ctypes.windll.kernel32
    
    # 定义必要的类型和常量
    FILE_WRITE_ATTRIBUTES = 0x0100
    OPEN_EXISTING = 3
    FILE_FLAG_BACKUP_SEMANTICS = 0x02000000  # 允许打开目录
    INVALID_HANDLE_VALUE = -1
    
    def set_windows_creation_time(filepath: str, timestamp: float) -> bool:
        """
        在 Windows 上设置文件的创建时间
        """
        # 将 Unix 时间戳转换为 Windows FileTime (100-nanosecond intervals since Jan 1, 1601)
        # 1970-01-01 is 11644473600 seconds after 1601-01-01
        win_timestamp = int((timestamp * 10000000) + 116444736000000000)
        
        filetime = wintypes.FILETIME(win_timestamp & 0xFFFFFFFF, win_timestamp >> 32)
        
        handle = kernel32.CreateFileW(
            str(filepath),
            FILE_WRITE_ATTRIBUTES,
            0,
            None,
            OPEN_EXISTING,
            128,  # FILE_ATTRIBUTE_NORMAL
            None
        )
        
        if handle == INVALID_HANDLE_VALUE:
            return False
            
        # SetFileTime(handle, creation_time, access_time, write_time)
        # 我们这里只设置创建时间，其他传 None (即不改变，或者由 os.utime 处理)
        result = kernel32.SetFileTime(handle, byref(filetime), None, None)
        kernel32.CloseHandle(handle)
        
        return result != 0
else:
    def set_windows_creation_time(filepath: str, timestamp: float) -> bool:
        return True # 非 Windows 系统忽略

def reset_file_timestamp(file_path: Path, timestamp: float = 0) -> bool:
    """
    重置文件的 创建时间、访问时间 和 修改时间
    
    Args:
        file_path: 文件路径
        timestamp: Unix 时间戳，默认为 0 (1970-01-01 00:00:00)
    
    Returns:
        bool: 成功返回 True，失败返回 False
    """
    try:
        # 1. 设置 创建时间 (Windows Only)
        if platform.system() == 'Windows':
            if not set_windows_creation_time(str(file_path), timestamp):
                print(f"⚠️  警告: 无法设置创建时间 {file_path}")
        
        # 2. 设置 访问时间和修改时间 (通用)
        # os.utime(path, (atime, mtime))
        os.utime(file_path, (timestamp, timestamp))
        return True
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False


def process_directory(directory: Path, recursive: bool = False) -> tuple[int, int]:
    """
    处理目录中的所有 PNG 文件
    
    Args:
        directory: 目录路径
        recursive: 是否递归处理子目录
    
    Returns:
        tuple: (成功数量, 失败数量)
    """
    if not directory.exists():
        print(f"❌ 错误：目录不存在 - {directory}")
        return 0, 0
    
    if not directory.is_dir():
        print(f"❌ 错误：路径不是目录 - {directory}")
        return 0, 0
    
    # 查找所有 PNG 文件
    pattern = "**/*.png" if recursive else "*.png"
    png_files = list(directory.glob(pattern))
    
    if not png_files:
        print(f"⚠️  未找到任何 PNG 文件")
        return 0, 0
    
    print(f"\n📁 目录: {directory.absolute()}")
    print(f"🔍 找到 {len(png_files)} 个 PNG 文件")
    print(f"🔄 {'递归' if recursive else '非递归'}处理模式")
    print(f"⏰ 目标时间: 1970-01-01 00:00:00 UTC (创建/修改/访问)\n")
    
    success_count = 0
    fail_count = 0
    
    # Unix 纪元时间戳 (1970-01-01 00:00:00)
    epoch_timestamp = 0
    
    for i, png_file in enumerate(png_files, 1):
        # 获取原始修改时间（仅用于显示日志）
        try:
            original_mtime = os.path.getmtime(png_file)
            original_datetime = datetime.fromtimestamp(original_mtime)
        except:
            original_datetime = None
        
        # 重置时间戳
        if reset_file_timestamp(png_file, epoch_timestamp):
            success_count += 1
            relative_path = png_file.relative_to(directory)
            if original_datetime:
                print(f"✅ [{i}/{len(png_files)}] {relative_path}")
            else:
                print(f"✅ [{i}/{len(png_files)}] {relative_path}")
        else:
            fail_count += 1
    
    return success_count, fail_count


def main():
    parser = argparse.ArgumentParser(
        description="将 PNG 图片的所有时间属性（创建/修改/访问）重置为 1970-01-01",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s ./images                    # 处理 images 目录下的 PNG 文件
  %(prog)s ./output --recursive        # 递归处理 output 目录及其子目录
  %(prog)s D:\\Photos\\Export -r        # 使用短参数递归处理
        """
    )
    
    parser.add_argument(
        'directory',
        type=str,
        help='要处理的目录路径'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='递归处理子目录中的 PNG 文件'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式，只显示将要处理的文件，不实际修改'
    )
    
    args = parser.parse_args()
    
    # 转换为 Path 对象
    target_dir = Path(args.directory)
    
    print("=" * 60)
    print("PNG 图片全时间戳重置工具 (含创建时间)")
    print("=" * 60)
    
    if args.dry_run:
        print("\n⚠️  试运行模式 - 不会实际修改文件\n")
        # 在试运行模式下，只列出文件
        pattern = "**/*.png" if args.recursive else "*.png"
        png_files = list(target_dir.glob(pattern))
        print(f"将处理以下 {len(png_files)} 个文件：\n")
        for png_file in png_files:
            print(f"  - {png_file.relative_to(target_dir)}")
        print("\n提示：移除 --dry-run 参数以实际执行修改")
        return
    
    # 处理文件
    success, fail = process_directory(target_dir, args.recursive)
    
    # 输出统计
    print("\n" + "=" * 60)
    print("处理完成")
    print("=" * 60)
    print(f"✅ 成功: {success} 个文件")
    if fail > 0:
        print(f"❌ 失败: {fail} 个文件")
    print("=" * 60)
    
    # 返回适当的退出码
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
