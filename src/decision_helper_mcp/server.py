"""由 MCP Hub 自动托管 HTTP 的无状态随机决策工具。"""

from random import SystemRandom

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "decision-helper-mcp",
    host="0.0.0.0",
    port=9000,
    stateless_http=True,
    json_response=True,
)

_random = SystemRandom()


def _bounded_integer(value: int, name: str, minimum: int, maximum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} 必须是整数")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} 必须在 {minimum} 到 {maximum} 之间")


def _validate_options(options: list[str]) -> None:
    if not 1 <= len(options) <= 1000:
        raise ValueError("options 必须包含 1 到 1000 个选项")
    for option in options:
        if not isinstance(option, str) or not option.strip() or len(option) > 200:
            raise ValueError("每个选项必须是非空字符串，长度不超过 200 个字符")


@mcp.tool()
def roll_dice(count: int = 1, sides: int = 6) -> dict:
    """掷 count 个 sides 面骰子。count 范围 1–20，sides 范围 2–1000。

    返回每枚骰子的点数 rolls、点数之和 total 及骰子参数。没有外部副作用。
    """
    _bounded_integer(count, "count", 1, 20)
    _bounded_integer(sides, "sides", 2, 1000)
    rolls = [_random.randint(1, sides) for _ in range(count)]
    return {"rolls": rolls, "total": sum(rolls), "count": count, "sides": sides}


@mcp.tool()
def draw_options(options: list[str], count: int = 1) -> dict:
    """从 options 中按位置不放回抽取 count 项，按抽取顺序返回结果。

    options 包含 1–1000 个非空字符串，每项最多 200 字符；count 为 1 到选项数。
    返回 selected（index 从 0 开始、value 为原始文本）和 population_size。
    重复文本保留为不同位置，不修改输入；没有外部副作用。
    """
    _validate_options(options)
    _bounded_integer(count, "count", 1, len(options))
    indices = _random.sample(range(len(options)), count)
    return {
        "selected": [{"index": index, "value": options[index]} for index in indices],
        "population_size": len(options),
    }


@mcp.tool()
def shuffle_options(options: list[str]) -> dict:
    """随机排列全部选项，返回 shuffled（原始 index、value）和 count。

    options 包含 1–1000 个非空字符串，每项最多 200 字符。
    重复文本保留为不同位置，不修改输入；没有外部副作用。
    """
    _validate_options(options)
    indices = list(range(len(options)))
    _random.shuffle(indices)
    return {
        "shuffled": [{"index": index, "value": options[index]} for index in indices],
        "count": len(options),
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
