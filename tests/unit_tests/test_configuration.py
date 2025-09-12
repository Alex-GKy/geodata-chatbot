from typing import Any

def test_graph_imports() -> None:
    # Import here to rely on sys.path injection from conftest
    from agent import graph  # type: ignore

    # Minimal sanity checks without invoking external services
    assert graph is not None
    # The compiled graph should expose common methods
    assert hasattr(graph, "invoke")
    assert hasattr(graph, "ainvoke")
    assert hasattr(graph, "stream")
