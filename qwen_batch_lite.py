#!/usr/bin/env python3
"""Qwen API 批量对话测试工具 - 轻量版，直接调用 API"""

import os
import json
import argparse
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("QWEN_API_KEY")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen-plus"
TIMEOUT = 60


def chat(message: str, history: Optional[List[Dict]] = None) -> str:
    """直接调用 Qwen API"""
    if not API_KEY:
        raise Exception("API_KEY 未配置")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if history:
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})
    
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }
    
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=TIMEOUT
    )
    response.raise_for_status()
    result = response.json()
    
    if "error" in result:
        raise Exception(f"API 错误：{result['error'].get('message', '未知错误')}")
    
    return result["choices"][0]["message"]["content"]


def load_questions(file_path: str) -> List[str]:
    """从文件加载问题"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        if path.suffix == '.json':
            data = json.load(f)
            if isinstance(data, list):
                return [item.get('question', str(item)) if isinstance(item, dict) else str(item) for item in data]
            elif isinstance(data, dict) and 'questions' in data:
                return data['questions']
        else:
            return [line.strip() for line in f if line.strip()]
    return []


def save_results(results: List[Dict], output_file: str) -> None:
    """保存结果"""
    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if path.suffix == '.json':
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    elif path.suffix == '.md':
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# Qwen API 批量对话测试结果\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**总计**: {len(results)} | **成功**: {sum(1 for r in results if r['success'])} | **失败**: {sum(1 for r in results if not r['success'])}\n\n")
            f.write("---\n\n")
            
            for result in results:
                status = "✅" if result['success'] else "❌"
                f.write(f"## {status} 问题 {result['index']}\n\n")
                f.write(f"**问题**: {result['question']}\n\n")
                if result['success']:
                    f.write(f"**回答**:\n\n{result['answer']}\n\n")
                else:
                    f.write(f"**错误**: {result['error']}\n\n")
                f.write("---\n\n")
    else:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"批量测试结果 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            for result in results:
                status = "OK" if result['success'] else "XX"
                f.write(f"[{result['index']}] {status}\n")
                f.write(f"问题：{result['question']}\n")
                if result['success']:
                    f.write(f"回答：{result['answer']}\n")
                else:
                    f.write(f"错误：{result['error']}\n")
                f.write("-" * 40 + "\n\n")
    
    print(f"\n结果已保存到：{output_file}")


def run_test(questions: List[str], output_file: Optional[str] = None, delay: float = 0.5) -> None:
    """运行批量测试"""
    results = []
    history = []
    
    print(f"\n开始测试，共 {len(questions)} 个问题，模型：{MODEL}")
    print("=" * 60)
    
    for i, q in enumerate(questions, 1):
        preview = q[:40] + '...' if len(q) > 40 else q
        print(f"[{i}/{len(questions)}] {preview}", end=" ... ", flush=True)
        
        result = {
            'index': i,
            'question': q,
            'answer': None,
            'success': False,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        start = time.time()
        try:
            answer = chat(q, history if '--history' in [] else None)
            elapsed = time.time() - start
            result['answer'] = answer
            result['success'] = True
            result['elapsed'] = round(elapsed, 1)
            print(f"OK ({elapsed:.1f}s)")
        except Exception as e:
            elapsed = time.time() - start
            result['error'] = str(e)
            result['elapsed'] = round(elapsed, 1)
            print(f"FAILED ({elapsed:.1f}s): {e}")
        
        results.append(result)
        
        if delay > 0 and i < len(questions):
            time.sleep(delay)
    
    print("=" * 60)
    ok = sum(1 for r in results if r['success'])
    total_time = sum(r.get('elapsed', 0) for r in results)
    print(f"完成：{ok}/{len(questions)} 成功 | 总耗时 {total_time:.1f}s")
    
    if output_file:
        save_results(results, output_file)


def main():
    parser = argparse.ArgumentParser(description='Qwen API 批量测试工具（轻量版）')
    parser.add_argument('-q', '--questions', nargs='+', required=True)
    parser.add_argument('-o', '--output', default=None)
    parser.add_argument('--delay', type=float, default=0.5)
    
    args = parser.parse_args()
    
    if len(args.questions) == 1 and Path(args.questions[0]).exists():
        questions = load_questions(args.questions[0])
        print(f"从文件加载：{args.questions[0]} ({len(questions)} 个问题)")
    else:
        questions = args.questions
    
    run_test(questions, args.output, args.delay)


if __name__ == '__main__':
    main()
