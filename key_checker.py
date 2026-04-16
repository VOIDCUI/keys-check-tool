#!/usr/bin/env python3
"""
API Key 批量检测工具
支持批量检测 OpenAI 兼容 API 的 Key 是否可用
"""

import requests
import concurrent.futures
import argparse
from typing import List, Tuple
import time
import os
from dotenv import load_dotenv
from tqdm import tqdm
import sys


class KeyChecker:
    def __init__(self, base_url: str, model: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.valid_keys = []
        self.invalid_keys = []
        self.stop_checking = False

    def check_single_key(self, api_key: str) -> Tuple[str, bool, str]:
        """检测单个 API Key 是否可用"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return api_key, True, "成功"
            else:
                return api_key, False, f"错误码: {response.status_code}"
        except requests.exceptions.Timeout:
            return api_key, False, "超时"
        except Exception as e:
            return api_key, False, f"异常: {str(e)[:50]}"

    def check_keys(self, keys: List[str], max_workers: int = 10):
        """批量检测 API Keys"""
        print(f"[*] 共 {len(keys)} 个 API Key")
        print(f"[*] 目标验证节点: {self.base_url}")
        print(f"[*] 检测模型: {self.model}")
        print(f"[*] 开始多线程并发检测...\n")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.check_single_key, key): key for key in keys}

            # 使用 tqdm 创建进度条
            with tqdm(total=len(keys), desc="检测进度", unit="key") as pbar:
                for future in concurrent.futures.as_completed(futures):
                    if self.stop_checking:
                        # 取消剩余的任务
                        for f in futures:
                            f.cancel()
                        break

                    api_key, is_valid, message = future.result()

                    if is_valid:
                        self.valid_keys.append(api_key)
                        # 不脱敏,显示完整 Key
                        tqdm.write(f"\n[+] 成功! 找到有效的 API Key: {api_key}")

                        # 询问是否继续检测
                        pbar.close()
                        user_input = input("\n是否继续检测剩余的 Keys? (y/n): ").strip().lower()
                        if user_input != 'y':
                            self.stop_checking = True
                            print("[*] 停止检测...")
                            break
                        else:
                            # 重新创建进度条
                            remaining = len(keys) - pbar.n
                            pbar = tqdm(total=len(keys), desc="检测进度", unit="key", initial=pbar.n)
                    else:
                        self.invalid_keys.append((api_key, message))

                    pbar.update(1)

        self.print_summary()

    def mask_key(self, key: str) -> str:
        """脱敏显示 Key"""
        if len(key) <= 12:
            return key[:4] + "..." + key[-4:]
        return key[:8] + "..." + key[-8:]

    def print_summary(self):
        """打印检测结果摘要"""
        print("\n" + "="*60)
        print(f"检测完成!")
        print(f"有效 Key 数量: {len(self.valid_keys)}")
        print(f"无效 Key 数量: {len(self.invalid_keys)}")
        print("="*60)

        if self.valid_keys:
            print("\n有效的 Keys:")
            for key in self.valid_keys:
                print(f"  {key}")

        if self.invalid_keys:
            print("\n无效的 Keys (前10个):")
            for key, reason in self.invalid_keys[:10]:
                print(f"  {self.mask_key(key)} - {reason}")

    def save_results(self, output_file: str):
        """保存有效的 Keys 到文件"""
        with open(output_file, 'w') as f:
            for key in self.valid_keys:
                f.write(f"{key}\n")
        print(f"\n[*] 有效的 Keys 已保存到: {output_file}")


def load_keys_from_file(file_path: str) -> List[str]:
    """从文件加载 Keys"""
    with open(file_path, 'r') as f:
        keys = [line.strip() for line in f if line.strip()]
    return keys


def main():
    # 加载 .env 文件
    load_dotenv()

    parser = argparse.ArgumentParser(description='API Key 批量检测工具')
    parser.add_argument('-f', '--file', required=True, help='包含 API Keys 的文件路径 (每行一个)')
    parser.add_argument('-u', '--url', help='API Base URL (例如: https://api.openai.com/v1)')
    parser.add_argument('-m', '--model', help='要检测的模型名称')
    parser.add_argument('-w', '--workers', type=int, default=10, help='并发线程数 (默认: 10)')
    parser.add_argument('-o', '--output', default='valid_keys.txt', help='输出文件路径 (默认: valid_keys.txt)')
    parser.add_argument('-t', '--timeout', type=int, default=10, help='请求超时时间/秒 (默认: 10)')

    args = parser.parse_args()

    # 优先使用 .env 配置,其次使用命令行参数
    base_url = os.getenv('BASE_URL') or args.url
    model = os.getenv('MODEL') or args.model or 'gpt-3.5-turbo'

    if not base_url:
        print("[!] 错误: 必须通过 .env 文件的 BASE_URL 或 -u/--url 参数指定 API Base URL")
        return

    # 加载 Keys
    try:
        keys = load_keys_from_file(args.file)
    except FileNotFoundError:
        print(f"[!] 错误: 文件 '{args.file}' 不存在")
        return

    if not keys:
        print("[!] 错误: 文件中没有找到任何 Key")
        return

    # 开始检测
    checker = KeyChecker(base_url, model, args.timeout)
    checker.check_keys(keys, args.workers)

    # 保存结果
    if checker.valid_keys:
        checker.save_results(args.output)


if __name__ == "__main__":
    main()
