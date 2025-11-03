#!/bin/bash
python3 postgre/cn.py
flask run --host=0.0.0.0 --port 2048
