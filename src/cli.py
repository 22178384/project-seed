"""project-seed 的命令行入口骨架。"""

from __future__ import annotations

import argparse


def main() -> None:
    p = argparse.ArgumentParser(description="最小可运行 Python 骨架")
    p.add_argument("--name", default="world", help="问候对象")
    args = p.parse_args()
    print(f"hello, {args.name}!")


if __name__ == "__main__":
    main()
