# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

#!/bin/bash

# Convenience script for running the pipeline linting checks etc. locally

python -m black --diff --check os2mo_fastapi_utils tests
python -m isort --profile black --diff --check-only os2mo_fastapi_utils tests
python -m mypy --ignore-missing-imports --strict-optional --no-implicit-optional --namespace-packages os2mo_fastapi_utils tests
