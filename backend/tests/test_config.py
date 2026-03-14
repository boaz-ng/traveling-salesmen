"""Tests for application configuration (Settings)."""

from app.config import Settings


class TestSettingsDefaults:
    """Verify that all Settings fields have the expected defaults."""

    def test_llm_provider_defaults_to_qwen(self):
        s = Settings(
            _env_file=None,  # type: ignore[call-arg]
        )
        assert s.llm_provider == "qwen"

    def test_llm_model_defaults_to_empty(self):
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.llm_model == ""

    def test_anthropic_api_key_defaults_to_empty(self):
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.anthropic_api_key == ""

    def test_qwen_api_key_defaults_to_empty(self):
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.qwen_api_key == ""

    def test_qwen_base_url_defaults_to_empty(self):
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.qwen_base_url == ""

    def test_amadeus_api_key_defaults_to_empty(self):
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.amadeus_api_key == ""

    def test_amadeus_api_secret_defaults_to_empty(self):
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.amadeus_api_secret == ""

    def test_amadeus_env_defaults_to_test(self):
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.amadeus_env == "test"


class TestSettingsFromEnv:
    """Verify that Settings reads values from environment variables."""

    def test_llm_provider_from_env(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.llm_provider == "anthropic"

    def test_llm_model_from_env(self, monkeypatch):
        monkeypatch.setenv("LLM_MODEL", "qwen-turbo")
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.llm_model == "qwen-turbo"

    def test_anthropic_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.anthropic_api_key == "sk-ant-test-key"

    def test_qwen_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("QWEN_API_KEY", "sk-qwen-test-key")
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.qwen_api_key == "sk-qwen-test-key"

    def test_qwen_base_url_from_env(self, monkeypatch):
        monkeypatch.setenv("QWEN_BASE_URL", "https://custom.endpoint/v1")
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.qwen_base_url == "https://custom.endpoint/v1"

    def test_amadeus_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("AMADEUS_API_KEY", "amadeus-test-key")
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.amadeus_api_key == "amadeus-test-key"

    def test_amadeus_api_secret_from_env(self, monkeypatch):
        monkeypatch.setenv("AMADEUS_API_SECRET", "amadeus-test-secret")
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.amadeus_api_secret == "amadeus-test-secret"

    def test_amadeus_env_from_env(self, monkeypatch):
        monkeypatch.setenv("AMADEUS_ENV", "production")
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.amadeus_env == "production"


class TestSettingsMultipleEnvVars:
    """Verify that multiple environment variables can be set together."""

    def test_full_qwen_config(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "qwen")
        monkeypatch.setenv("QWEN_API_KEY", "sk-qwen-123")
        monkeypatch.setenv("QWEN_BASE_URL", "https://example.com/v1")
        monkeypatch.setenv("LLM_MODEL", "qwen-max")
        monkeypatch.setenv("AMADEUS_API_KEY", "am-key")
        monkeypatch.setenv("AMADEUS_API_SECRET", "am-secret")

        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.llm_provider == "qwen"
        assert s.qwen_api_key == "sk-qwen-123"
        assert s.qwen_base_url == "https://example.com/v1"
        assert s.llm_model == "qwen-max"
        assert s.amadeus_api_key == "am-key"
        assert s.amadeus_api_secret == "am-secret"

    def test_full_anthropic_config(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-456")
        monkeypatch.setenv("LLM_MODEL", "claude-sonnet-4-20250514")

        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.llm_provider == "anthropic"
        assert s.anthropic_api_key == "sk-ant-456"
        assert s.llm_model == "claude-sonnet-4-20250514"

    def test_env_vars_are_case_insensitive(self, monkeypatch):
        """Pydantic Settings maps env vars case-insensitively to field names."""
        monkeypatch.setenv("LLM_PROVIDER", "anthropic")
        s = Settings(_env_file=None)  # type: ignore[call-arg]
        assert s.llm_provider == "anthropic"
