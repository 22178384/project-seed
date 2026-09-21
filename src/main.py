"""project-seed 演示入口。

演示跨账号复用：优先使用友号 @c991china/python-utils 的 tree()，
未安装时降级为内置简单打印，保证「克隆即跑」。
"""
from __future__ import annotations

import os


def main() -> None:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        from python_utils import tree
        print("（使用 c991china/python-utils 的 tree）")
        print(tree(root))
    except ImportError:
        print("未检测到 c991china/python-utils。")
        print("安装后可获得更漂亮的目录树：")
        print("  pip install git+https://github.com/c991china/python-utils.git")
        print("\n当前目录：", root)
        for name in sorted(os.listdir(root)):
            print(" -", name)


if __name__ == "__main__":
    main()
