# -*- coding: utf-8 -*-
"""
Supplier Invoice Loader - Configuration Loader
"""

try:
    from config.config_customer import *
except ImportError:
    print("WARNING: config_customer.py not found, using template")
    from config.config_template import *