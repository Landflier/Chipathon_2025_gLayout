#!/bin/bash
python -c "import inspect; from glayout.routing.L_route import L_route; print(inspect.signature(L_route))"
# python -c "import inspect; from glayout.routing.straight_route import straight_route; print(inspect.signature(straight_route))"
# python -c "import inspect; from glayout.util.comp_utils import align_comp_to_port ; print(inspect.signature(align_comp_to_port))"
# python -c "import inspect; from glayout.util.comp_utils import prec_array ; print(inspect.signature(prec_array))"
# python -c "import inspect; from glayout import nmos; print(inspect.signature(nmos))"

