#!/bin/bash
cd test
python -m test_parser
python -m test_speak_action
python -m test_update_action
python -m test_user_state
python -m test_state
python -m test_app
#   python -m test_pressure