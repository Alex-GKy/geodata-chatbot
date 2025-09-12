from typing import Any


def test_graph_has_minimal_interface() -> None:
    from agent import graph  # provided by src/agent

    # Verify key interface methods exist without making API calls
    for attr in ("invoke", "ainvoke", "stream"):
        assert hasattr(graph, attr), f"graph missing {attr}"


def test_langgraph_mapping_points_to_graph() -> None:
    import json
    from importlib import import_module
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    cfg_path = root / "langgraph.json"
    assert cfg_path.exists(), "langgraph.json not found"

    data = json.loads(cfg_path.read_text())
    target = data["graphs"]["agent"]
    # Expect format: "./src/agent/graph.py:graph"; ensure attribute exists
    module_path, attr = target.split(":", 1)
    # Import via package instead of path to avoid filesystem deps in test
    mod = import_module("agent")
    assert hasattr(mod, attr)
