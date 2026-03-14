#!/usr/bin/env python3
"""Qwen API 批量对话测试工具 - 从列表读取问题批量调用 API"""

import os
import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from qwen_api import chat_with_qwen, QwenAPIError


def load_questions_from_file(file_path: str) -> List[str]:
    """从文件加载问题列表"""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"问题文件不存在：{file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        if path.suffix == '.json':
            data = json.load(f)
            if isinstance(data, list):
                return [item.get('question', str(item)) if isinstance(item, dict) else str(item) for item in data]
            elif isinstance(data, dict) and 'questions' in data:
                return data['questions']
        else:
            questions = [line.strip() for line in f if line.strip()]
            return questions
    
    return []


def load_questions_from_list(questions: List[str]) -> List[str]:
    """从列表加载问题"""
    return [q.strip() for q in questions if q.strip()]


def run_batch_test(
    questions: List[str],
    output_file: Optional[str] = None,
    save_history: bool = False,
    delay_between_requests: float = 0,
) -> List[Dict]:
    """运行批量测试"""
    import time
    
    results = []
    history: List[Dict[str, str]] = []
    
    print(f"\n开始批量测试，共 {len(questions)} 个问题")
    print("=" * 60)
    
    for index, question in enumerate(questions, 1):
        q_preview = question[:50] + '...' if len(question) > 50 else question
        print(f"\n[{index}/{len(questions)}] 问题：{q_preview}")
        
        result = {
            'index': index,
            'question': question,
            'answer': None,
            'success': False,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            print("  正在调用 API...", end="", flush=True)
            
            if save_history:
                answer = chat_with_qwen(question, history)
                history.extend([
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer}
                ])
            else:
                answer = chat_with_qwen(question)
            
            result['answer'] = answer
            result['success'] = True
            
            print("\r  OK 完成          ")
            ans_preview = answer[:80] + '...' if len(answer) > 80 else answer
            print(f"  回答：{ans_preview}")
            
        except QwenAPIError as e:
            result['error'] = str(e)
            print(f"\r  XX 失败：{e}            ")
        except Exception as e:
            result['error'] = f"未知错误：{e}"
            print(f"\r  XX 异常：{e}            ")
        
        results.append(result)
        
        if delay_between_requests > 0 and index < len(questions):
            time.sleep(delay_between_requests)
    
    print("\n" + "=" * 60)
    success_count = sum(1 for r in results if r['success'])
    print(f"批量测试完成：成功 {success_count}/{len(questions)}")
    
    if output_file:
        save_results(results, output_file)
    
    return results


def save_results(results: List[Dict], output_file: str) -> None:
    """保存结果到文件"""
    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if path.suffix == '.json':
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    elif path.suffix == '.md':
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# Qwen API 批量对话测试结果\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**总计**: {len(results)} 个问题 | ")
            f.write(f"**成功**: {sum(1 for r in results if r['success'])} | ")
            f.write(f"**失败**: {sum(1 for r in results if not r['success'])}\n\n")
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
    
    print(f"结果已保存到：{output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Qwen API 批量对话测试工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python qwen_batch_test.py -q questions.txt -o results.json
  python qwen_batch_test.py -q questions.txt -o results.md
  python qwen_batch_test.py -q "问题 1" "问题 2" -o results.txt
  python qwen_batch_test.py -q questions.txt --history
  python qwen_batch_test.py -q questions.txt --delay 1
        """
    )
    
    parser.add_argument('-q', '--questions', nargs='+', required=True,
                        help='问题文件路径 或 直接指定问题列表')
    parser.add_argument('-o', '--output', default=None,
                        help='输出文件路径（支持 .json / .md / .txt 格式）')
    parser.add_argument('--history', action='store_true',
                        help='保存对话历史，启用多轮对话模式')
    parser.add_argument('--delay', type=float, default=0,
                        help='请求间隔时间（秒），默认 0')
    
    args = parser.parse_args()
    
    if len(args.questions) == 1 and Path(args.questions[0]).exists():
        questions = load_questions_from_file(args.questions[0])
        print(f"从文件加载了 {len(questions)} 个问题：{args.questions[0]}")
    else:
        questions = load_questions_from_list(args.questions)
        print(f"从命令行加载了 {len(questions)} 个问题")
    
    if not questions:
        print("错误：没有有效问题")
        return
    
    run_batch_test(
        questions=questions,
        output_file=args.output,
        save_history=args.history,
        delay_between_requests=args.delay
    )


if __name__ == '__main__':
    main()
