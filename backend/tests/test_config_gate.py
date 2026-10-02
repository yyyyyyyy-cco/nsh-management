"""生产弱密钥启动门禁回归（W2-2 / F-04）。

权威源：`backend/app/core/config.py`（判定与校验函数）+ `DEPLOY.md` §六（门禁说明）。

F-04 覆盖点：门禁已由「导入配置即终止进程」改为「应用启动时显式校验」——
含一条**子进程回归**断言「仅导入 config 不会退出」+「真正调用门禁仍拒绝启动」，
以及应用到启动钩子的接线用例。
"""
import io
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from app.core.config import (
    InsecureSecretKeyError,
    _is_production,
    _secret_key_is_weak,
    api_docs_enabled,
    enforce_secret_key,
    settings,
    validate_secret_key,
)

BACKEND_ROOT = Path(__file__).resolve().parents[1]

# 构造一个「32 字符、不含可猜片段、不含 20xx 年份」的强密钥用例
STRONG_MIXED_KEY = "Kj7#mQ2!vX9@bN4$wZ8%tR6^yU1&pL5*"


class SecretKeyStrengthTests(unittest.TestCase):
    """弱密钥判定：明显弱值一律拦截，强值不误杀。"""

    def test_dev_default_and_placeholders_are_weak(self):
        for key in (
            "dev-secret-key-change-in-production",
            "your-secret-key-change-this",
            "please-change-me-with-openssl-rand-hex-32",
        ):
            with self.subTest(key=key):
                self.assertTrue(_secret_key_is_weak(key))

    def test_empty_and_short_keys_are_weak(self):
        for key in ("", "a", "a" * 31):
            with self.subTest(length=len(key)):
                self.assertTrue(_secret_key_is_weak(key))

    def test_guessable_fragment_is_weak_even_if_long(self):
        # 长而可猜：长度足够但含 fragment（password）→ 仍判弱
        self.assertTrue(_secret_key_is_weak("Zq7!" + "x" * 24 + "password" + "y" * 8))

    def test_year_like_substring_is_weak(self):
        self.assertTrue(_secret_key_is_weak("Ab3!Cd5&" + "y" * 24 + "2019"))

    def test_strong_mixed_key_is_accepted(self):
        self.assertEqual(len(STRONG_MIXED_KEY), 32)
        self.assertFalse(_secret_key_is_weak(STRONG_MIXED_KEY))

    def test_64_hex_is_exempt_from_year_and_fragment_scan(self):
        # 豁免通道：≥64 位纯十六进制恒判强（避免随机 hex 偶含 20xx 被误杀）
        hex64 = "2012" + "abcdef" * 10          # 64 位十六进制，且含「2012」年份样式
        self.assertEqual(len(hex64), 64)
        self.assertFalse(_secret_key_is_weak(hex64))


class ProductionDetectionTests(unittest.TestCase):
    """生产环境判定：只断言显式 APP_ENV 的确定行为。"""

    def test_explicit_production_env(self):
        for value in ("production", "prod", " PRODUCTION "):
            with self.subTest(app_env=value), mock.patch.dict(os.environ, {"APP_ENV": value}):
                self.assertTrue(_is_production())

    def test_explicit_development_env(self):
        for value in ("development", "dev", "test"):
            with self.subTest(app_env=value), mock.patch.dict(os.environ, {"APP_ENV": value}):
                self.assertFalse(_is_production())

    def test_unset_env_result_is_environment_dependent(self):
        # 未声明 APP_ENV 时按容器特征兜底（/.dockerenv、/proc/1/cgroup），
        # 本地 Windows 与 CI 容器结果不同 —— 故只断言「返回布尔值、不抛异常」，不锁定具体值。
        environ = {k: v for k, v in os.environ.items() if k != "APP_ENV"}
        with mock.patch.dict(os.environ, environ, clear=True):
            self.assertIsInstance(_is_production(), bool)


def _production_env(**overrides: str) -> dict:
    """构造「生产环境」子进程环境：清掉 APP_ENV/SECRET_KEY 后按需覆盖；固定 UTF-8 输出。"""
    env = {k: v for k, v in os.environ.items() if k not in {"APP_ENV", "SECRET_KEY"}}
    env["APP_ENV"] = "production"
    env["PYTHONIOENCODING"] = "utf-8"
    env.update(overrides)
    return env


class ImportSideEffectTests(unittest.TestCase):
    """F-04 回归：**导入**配置不应终止进程；真正调用门禁的入口仍必须拒绝启动。"""

    def _run(self, code: str, env: dict) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-c", code],
            cwd=BACKEND_ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
        )

    def test_importing_config_does_not_exit_with_weak_production_key(self):
        code = "import app.core.config as c; print(c.settings.SECRET_KEY)"
        proc = self._run(code, _production_env(SECRET_KEY="dev-secret-key-change-in-production"))
        self.assertEqual(proc.returncode, 0, f"仅导入配置不应退出，stderr={proc.stderr}")
        self.assertNotIn("FATAL", proc.stderr)

    def test_enforce_in_subprocess_exits_nonzero_and_prints_fatal(self):
        code = "from app.core.config import enforce_secret_key; enforce_secret_key()"
        proc = self._run(code, _production_env(SECRET_KEY="dev-secret-key-change-in-production"))
        self.assertNotEqual(proc.returncode, 0, "生产环境弱密钥必须拒绝启动")
        self.assertIn("FATAL", proc.stderr)


class SecretKeyValidationTests(unittest.TestCase):
    """校验函数行为：生产弱密钥拒绝、强密钥放行、开发仅告警。"""

    def test_validate_raises_insecure_error_in_production_when_weak(self):
        with mock.patch.dict(os.environ, {"APP_ENV": "production"}), mock.patch.object(
            settings, "SECRET_KEY", "dev-secret-key-change-in-production"
        ):
            with self.assertRaises(InsecureSecretKeyError) as ctx:
                validate_secret_key()
        self.assertIn("FATAL", str(ctx.exception))

    def test_validate_passes_in_production_with_strong_key(self):
        with mock.patch.dict(os.environ, {"APP_ENV": "production"}), mock.patch.object(
            settings, "SECRET_KEY", STRONG_MIXED_KEY
        ):
            self.assertIsNone(validate_secret_key())

    def test_validate_warns_in_development_with_weak_key(self):
        buf = io.StringIO()
        with mock.patch.dict(os.environ, {"APP_ENV": "development"}), mock.patch.object(
            settings, "SECRET_KEY", "short"
        ), mock.patch("sys.stderr", buf):
            self.assertIsNone(validate_secret_key())
        self.assertIn("WARNING", buf.getvalue())

    def test_enforce_exits_with_code_one(self):
        buf = io.StringIO()
        with mock.patch.dict(os.environ, {"APP_ENV": "production"}), mock.patch.object(
            settings, "SECRET_KEY", "short"
        ), mock.patch("sys.stderr", buf):
            with self.assertRaises(SystemExit) as ctx:
                enforce_secret_key()
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("FATAL", buf.getvalue())


class StartupGateWiringTests(unittest.TestCase):
    """启动接线：`app.main.startup_checks` 必须调用门禁（需运行依赖，缺失时跳过）。"""

    def setUp(self):
        try:
            import app.main  # noqa: F401
        except ImportError as exc:
            self.skipTest(f"缺少运行依赖（如 FastAPI），跳过启动接线用例：{exc}")

    def test_startup_checks_enforces_gate(self):
        from app.main import startup_checks

        buf = io.StringIO()
        with mock.patch.dict(os.environ, {"APP_ENV": "production"}), mock.patch.object(
            settings, "SECRET_KEY", "short"
        ), mock.patch("sys.stderr", buf):
            with self.assertRaises(SystemExit):
                startup_checks()
        self.assertIn("FATAL", buf.getvalue())

    def test_startup_checks_passes_with_strong_development_key(self):
        from app.main import startup_checks

        with mock.patch.dict(os.environ, {"APP_ENV": "development"}), mock.patch.object(
            settings, "SECRET_KEY", STRONG_MIXED_KEY
        ):
            self.assertIsNone(startup_checks())


class ApiDocsVisibilityTests(unittest.TestCase):
    """在线 API 文档开关（W4-1）：仅生产环境关闭，本地开发保留。"""

    def test_disabled_in_production(self):
        for app_env in ("production", "prod", " PRODUCTION "):
            with self.subTest(app_env=app_env), mock.patch.dict(os.environ, {"APP_ENV": app_env}):
                self.assertFalse(api_docs_enabled())

    def test_enabled_in_development(self):
        for app_env in ("development", "dev", "test"):
            with self.subTest(app_env=app_env), mock.patch.dict(os.environ, {"APP_ENV": app_env}):
                self.assertTrue(api_docs_enabled())