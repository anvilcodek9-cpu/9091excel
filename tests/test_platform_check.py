"""윈도우 플랫폼 체크 테스트"""
import unittest
from unittest.mock import patch
import platform


class TestPlatformCheck(unittest.TestCase):
    """플랫폼 체크 함수 테스트"""
    
    @patch('platform.system')
    def test_windows_platform_passes(self, mock_system):
        """윈도우 플랫폼에서는 정상 실행"""
        mock_system.return_value = 'Windows'
        
        # 모듈을 동적으로 임포트하여 __init__.py 실행 방지
        import importlib.util
        spec = importlib.util.spec_from_file_location("platform_check", "src/platform_check.py")
        platform_check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(platform_check)
        
        try:
            platform_check.ensure_windows_platform()
        except RuntimeError:
            self.fail("Windows 플랫폼에서 에러가 발생하면 안 됩니다")
    
    @patch('platform.system')
    def test_non_windows_platform_raises_error(self, mock_system):
        """윈도우가 아닌 플랫폼에서는 에러 발생"""
        mock_system.return_value = 'Linux'
        
        import importlib.util
        spec = importlib.util.spec_from_file_location("platform_check", "src/platform_check.py")
        platform_check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(platform_check)
        
        with self.assertRaises(RuntimeError) as context:
            platform_check.ensure_windows_platform()
        self.assertEqual(str(context.exception), "이 프로그램은 Windows에서만 실행됩니다.")
    
    @patch('platform.system')
    def test_macos_platform_raises_error(self, mock_system):
        """macOS 플랫폼에서도 에러 발생"""
        mock_system.return_value = 'Darwin'
        
        import importlib.util
        spec = importlib.util.spec_from_file_location("platform_check", "src/platform_check.py")
        platform_check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(platform_check)
        
        with self.assertRaises(RuntimeError) as context:
            platform_check.ensure_windows_platform()
        self.assertEqual(str(context.exception), "이 프로그램은 Windows에서만 실행됩니다.")


if __name__ == '__main__':
    unittest.main()
