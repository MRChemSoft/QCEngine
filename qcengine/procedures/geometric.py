from .procedure_model import BaseProcedure

from typing import Any, Dict, Union
from qcelemental.models import ComputeError, FailedOperation, Optimization, OptimizationInput


class GeometricProcedure(BaseProcedure):

    _defaults = {"name": "geomeTRIC", "procedure": "optimization"}

    class Config(BaseProcedure.Config):
        pass

    def __init__(self, **kwargs):
        super().__init__(**{**self._defaults, **kwargs})

    def build_input_model(self, data: Union[Dict[str, Any], 'OptimizationInput'],
                          raise_error: bool=True) -> 'OptimizationInput':
        return _build_model(data, raise_error, OptimizationInput)

    def compute(self, input_data: 'OptimizationInput', config: 'JobConfig') -> 'Optimization':
        try:
            import geometric
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Could not find geomeTRIC in the Python path.")

        geometric_input = input_data.dict()

        # Older QCElemental compat, can be removed in v0.6
        if "extras" not in geometric_input["input_specification"]:
            geometric_input["input_specification"]["extras"] = {}

        geometric_input["input_specification"]["extras"]["_qcengine_local_config"] = config.dict()

        # Run the program
        output_data = geometric.run_json.geometric_run_json(geometric_input)

        output_data["provenance"] = {
            "creator": "geomeTRIC",
            "routine": "geometric.run_json.geometric_run_json",
            "version": geometric.__version__
        }

        output_data["schema_name"] = "qcschema_optimization_output"
        output_data["input_specification"]["extras"].pop("_qcengine_local_config", None)
        if output_data["success"]:
            output_data = Optimization(**output_data)

        return output_data

    def found(self) -> bool:
        try:
            import geometric
            return True
        except ModuleNotFoundError:
            return False