# tests/conftest.py

import sys
import os

# Adiciona o diretório 'src' ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

pytest_plugins = ["tests.helper.integration_fixtures"]
