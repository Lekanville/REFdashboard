import ast
from pathlib import Path


def load_uoa_config():
    source_path = Path(__file__).resolve().parents[1] / "code" / "dashboard.py"
    source = source_path.read_text()
    module = ast.parse(source)

    namespace = {"__builtins__": __builtins__}
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "UOA_CONFIG":
                    exec(compile(ast.Module(body=[node], type_ignores=[]), filename=str(source_path), mode="exec"), namespace)
                    return namespace["UOA_CONFIG"]

    raise AssertionError("UOA_CONFIG was not found in dashboard.py")


def test_uoa_config_is_explicit_and_complete():
    uoa_config = load_uoa_config()

    expected_uoas = {"UoA1", "UoA2", "UoA4", "UoA5", "UoA6"}
    assert set(uoa_config.keys()) == expected_uoas

    assert uoa_config["UoA1"]["prediction_column"] == "predictions_for_uoa_1"
    assert uoa_config["UoA2"]["distance_column"] == "distance_to_median_of_uoa_2"
    assert uoa_config["UoA6"]["prediction_column"] == "predictions_for_uoa_6"
