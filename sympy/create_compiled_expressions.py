"""
The implementation in this script is unorthodox, to maintain compatibility and performance while reducing the
dependencies of the package. This script is not part of the production code of ``evt``.

In order to calculate the observed Fisher information, it is necessary to differentiate a PDF, yielding
an expression of a size that is unwieldy to work with manually. Therefore, ``sympy`` is used to perform the
analytical calculations. In order to prevent the ``evt`` package from depending on ``sympy``, the following approach
was taken.

This file creates a Python script ``evt/src/_compiled_expressions/compiled_expressions.py``, containing the expression
to calculate the observed Fisher information in ``numpy`` style. The production code can then use the compiled
expression to calculate the observed Fisher information.
"""

import os

from evt.utils import repo_root
from sympy import symbols, exp, log, diff

x, g, a, s = symbols('x g a s')
variables = [g, a, s]

log_f = log(
    exp(-((1 + (x - a) * g / s) ** (-1 / g)))
    * (1 + (x - a) * g / s) ** (-1 - 1 / g)
    / s
)

fisher_information = []
for row_variable in variables:
    row = []
    for column_variable in variables:
        row.append(str(
            -diff(
                diff(
                    log_f,
                    column_variable
                ),
                row_variable
            )
        ).replace(
            'log', 'np.log'
        ).replace(
            'exp', 'np.exp'
        ))
    fisher_information.append(row)

output_lines = [
    '"""',
    'This file is not intended to be human-readable. It is generated by ``sympy/create_compiled_expressions.py``:',
    'see the generation file for further details.',
    '"""',
    'from numbers import Real'
    '',
    'import numpy as np',
    '',
    '',
    'def gevmle_fisher_information(',
    '        x: np.ndarray,',
    '        g: Real,',
    '        a: Real,',
    '        s: Real,',
    '):',
    '    return np.array(['
]
for row in fisher_information:
    output_lines.append('        [')
    for column in row:
        output_lines.append(f'            np.sum({column}),')
    output_lines.append('        ],')
output_lines.extend([
    '    ]) / len(x)',
    ''
])

with open(os.path.join(repo_root(), 'src', 'evt', '_compiled_expressions', 'compiled_expressions.py'), 'w') as f:
    f.write('\n'.join(output_lines))
