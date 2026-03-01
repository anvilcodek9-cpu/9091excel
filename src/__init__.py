"""Naver Smart Store to Logen Delivery Integration Package."""

from src.platform_check import ensure_windows_platform

# 패키지 임포트 시 윈도우 플랫폼 체크
ensure_windows_platform()

# Export main function
from src.main import generate_logen_shipping_file

__all__ = ['generate_logen_shipping_file']
