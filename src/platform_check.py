"""윈도우 플랫폼 체크 모듈"""
import platform
import sys


def ensure_windows_platform():
    """
    현재 플랫폼이 Windows인지 확인합니다.
    
    Raises:
        RuntimeError: Windows가 아닌 플랫폼에서 실행될 경우
    """
    if platform.system() != 'Windows':
        raise RuntimeError("이 프로그램은 Windows에서만 실행됩니다.")
