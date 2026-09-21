# project-seed

> 一个最小可运行的 Python 项目骨架。克隆即跑，适合作为新项目的起点。

## 特性
- 标准 `src/` 布局
- 依赖声明见 `pyproject.toml`
- 示例里**直接复用友号 [@c991china/python-utils](https://github.com/c991china/python-utils)** 的 `tree()`，演示跨账号协作

## 快速开始
    git clone https://github.com/22178384/project-seed.git
    cd project-seed
    pip install -e .
    python -m project_seed

## 依赖说明（跨账号联动）
`src/main.py` 优先 `from python_utils import tree`，即使用友号仓库
[@c991china/python-utils](https://github.com/c991china/python-utils) 的函数。
未安装时自动降级为内置打印，保证「克隆即跑」。要启用完整能力：

    pip install git+https://github.com/c991china/python-utils.git

这就是两个账号「互相提供支持」的实例：c991china 提供工具库，22178384 的项目消费它。

## 生态联动
- 工具库本体 → [@c991china/python-utils](https://github.com/c991china/python-utils)
- 通用片段 → [@22178384/snippet-box](https://github.com/22178384/snippet-box)
