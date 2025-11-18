#!/usr/bin/env python3
"""Streamlit 앱 실행 스크립트

PYTHONPATH를 올바르게 설정하고 Streamlit 앱을 실행합니다.
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 환경 변수 설정
os.environ["PYTHONPATH"] = str(project_root)

# Streamlit 실행
if __name__ == "__main__":
    from streamlit.web import cli as stcli
    import sys

    app_path = project_root / "src" / "ui" / "app.py"

    sys.argv = ["streamlit", "run", str(app_path)]
    sys.exit(stcli.main())
