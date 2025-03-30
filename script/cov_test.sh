#! /bin/bash
coverage erase
coverage run -m pytest tests
coverage report -m