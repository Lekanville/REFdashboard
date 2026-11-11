import ast
from pathlib import Path


def load_register_startup_task():
    source_path = Path(__file__).resolve().parents[1] / "apis" / "v1" / "route_res_outputs.py"
    source = source_path.read_text()
    module = ast.parse(source)

    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == "register_startup_task":
            namespace = {"__builtins__": __builtins__}
            exec(ast.get_source_segment(source, node), namespace)
            return namespace["register_startup_task"], namespace

    raise AssertionError("register_startup_task was not found in route_res_outputs.py")


def test_register_startup_task_deduplicates():
    register_startup_task, namespace = load_register_startup_task()
    namespace["STARTUP_TASKS_REGISTERED"] = set()

    def sample_task():
        return None

    sample_task.__module__ = "tests.sample_task"
    sample_task.__qualname__ = "sample_task"

    task_key = f"{sample_task.__module__}:{sample_task.__qualname__}"
    assert task_key not in namespace["STARTUP_TASKS_REGISTERED"]

    first = register_startup_task(sample_task)
    second = register_startup_task(sample_task)

    assert first is sample_task
    assert second is sample_task
    assert task_key in namespace["STARTUP_TASKS_REGISTERED"]
