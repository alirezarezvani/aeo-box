"""
Configuration Management for Agentic AEO System

Handles environment variables, settings validation, and data directory setup.
Uses Pydantic for type-safe configuration with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class ClaudeConfig(BaseModel):
    """Claude API configuration"""

    api_key: str = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""),
        description="Anthropic API key (required)"
    )
    enable_prompt_caching: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_PROMPT_CACHING", "true").lower() == "true",
        description="Enable 90% cost savings with prompt caching"
    )
    enable_extended_context: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_EXTENDED_CONTEXT", "true").lower() == "true",
        description="Enable 200K token extended context"
    )
    enable_request_batching: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_REQUEST_BATCHING", "true").lower() == "true",
        description="Combine multiple agent calls into single requests"
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key is not empty"""
        if not v or v.strip() == "":
            raise ValueError(
                "ANTHROPIC_API_KEY is required. Set it in .env file or environment variable."
            )
        return v.strip()


class AgentConfig(BaseModel):
    """Agent execution configuration"""

    max_parallel_agents: int = Field(
        default_factory=lambda: int(os.getenv("MAX_PARALLEL_AGENTS", "6")),
        ge=1,
        le=6,
        description="Maximum number of agents to run in parallel"
    )
    timeout_seconds: int = Field(
        default_factory=lambda: int(os.getenv("AGENT_TIMEOUT_SECONDS", "300")),
        ge=30,
        le=3600,
        description="Agent timeout in seconds (30s - 1h)"
    )
    max_retries: int = Field(
        default_factory=lambda: int(os.getenv("AGENT_MAX_RETRIES", "3")),
        ge=0,
        le=10,
        description="Maximum retry attempts on agent failure"
    )
    retry_delay_seconds: int = Field(
        default_factory=lambda: int(os.getenv("AGENT_RETRY_DELAY_SECONDS", "2")),
        ge=1,
        le=60,
        description="Initial retry delay in seconds (exponential backoff)"
    )


class DataConfig(BaseModel):
    """Data persistence configuration"""

    data_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("DATA_DIR", ".aeo-agent-data")),
        description="Local directory for campaign data storage"
    )
    enable_compression: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_DATA_COMPRESSION", "false").lower() == "true",
        description="Enable JSON data compression"
    )
    campaign_retention_days: int = Field(
        default_factory=lambda: int(os.getenv("CAMPAIGN_RETENTION_DAYS", "90")),
        ge=0,
        description="Auto-delete campaigns older than N days (0 = never delete)"
    )

    def ensure_data_dir(self) -> None:
        """Create data directory structure if it doesn't exist"""
        directories = [
            self.data_dir,
            self.data_dir / "campaigns",
            self.data_dir / "tracking",
            self.data_dir / "learning",
            self.data_dir / "cache",
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


class LoggingConfig(BaseModel):
    """Logging configuration"""

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper(),
        description="Logging level"
    )
    log_format: Literal["json", "text"] = Field(
        default_factory=lambda: os.getenv("LOG_FORMAT", "json").lower(),
        description="Log output format"
    )
    log_file: Optional[str] = Field(
        default_factory=lambda: os.getenv("LOG_FILE", None),
        description="Log file path (None = stdout only)"
    )
    verbose_agent_logs: bool = Field(
        default_factory=lambda: os.getenv("VERBOSE_AGENT_LOGS", "false").lower() == "true",
        description="Enable verbose agent communication logging"
    )


class APIConfig(BaseModel):
    """FastAPI server configuration"""

    host: str = Field(
        default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"),
        description="API server host"
    )
    port: int = Field(
        default_factory=lambda: int(os.getenv("API_PORT", "8000")),
        ge=1024,
        le=65535,
        description="API server port"
    )
    debug: bool = Field(
        default_factory=lambda: os.getenv("API_DEBUG", "false").lower() == "true",
        description="Enable debug mode"
    )
    rate_limit: int = Field(
        default_factory=lambda: int(os.getenv("API_RATE_LIMIT", "60")),
        ge=1,
        description="API rate limit (requests per minute)"
    )


class LLMProvidersConfig(BaseModel):
    """Configuration for additional LLM providers (citation tracking)"""

    openai_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", None),
        description="OpenAI API key for ChatGPT citation tracking"
    )
    google_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("GOOGLE_API_KEY", None),
        description="Google API key for Gemini citation tracking"
    )
    mistral_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("MISTRAL_API_KEY", None),
        description="Mistral API key for Mistral citation tracking"
    )
    perplexity_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("PERPLEXITY_API_KEY", None),
        description="Perplexity API key for Perplexity citation tracking"
    )


class AdvancedConfig(BaseModel):
    """Advanced system configuration"""

    privacy_mode: bool = Field(
        default_factory=lambda: os.getenv("PRIVACY_MODE", "false").lower() == "true",
        description="Disable telemetry and external requests"
    )
    enable_experimental_features: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_EXPERIMENTAL_FEATURES", "false").lower() == "true",
        description="Enable experimental features"
    )


class Config(BaseModel):
    """Main configuration container for Agentic AEO system"""

    claude: ClaudeConfig = Field(default_factory=ClaudeConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    data: DataConfig = Field(default_factory=DataConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    llm_providers: LLMProvidersConfig = Field(default_factory=LLMProvidersConfig)
    advanced: AdvancedConfig = Field(default_factory=AdvancedConfig)

    def __init__(self, **kwargs):
        """Initialize config and create data directory"""
        super().__init__(**kwargs)
        self.data.ensure_data_dir()

    def to_dict(self) -> dict:
        """Export configuration as dictionary"""
        return self.model_dump()

    def summary(self) -> str:
        """Return human-readable configuration summary"""
        lines = [
            "=== Agentic AEO Configuration ===",
            "",
            "Claude API:",
            f"  - API Key: {'✓ Set' if self.claude.api_key else '✗ Missing'}",
            f"  - Prompt Caching: {'✓ Enabled' if self.claude.enable_prompt_caching else '✗ Disabled'}",
            f"  - Extended Context: {'✓ Enabled' if self.claude.enable_extended_context else '✗ Disabled'}",
            f"  - Request Batching: {'✓ Enabled' if self.claude.enable_request_batching else '✗ Disabled'}",
            "",
            "Agent Execution:",
            f"  - Max Parallel: {self.agent.max_parallel_agents} agents",
            f"  - Timeout: {self.agent.timeout_seconds}s",
            f"  - Max Retries: {self.agent.max_retries}",
            f"  - Retry Delay: {self.agent.retry_delay_seconds}s",
            "",
            "Data Persistence:",
            f"  - Data Directory: {self.data.data_dir}",
            f"  - Compression: {'✓ Enabled' if self.data.enable_compression else '✗ Disabled'}",
            f"  - Retention: {self.data.campaign_retention_days} days",
            "",
            "Logging:",
            f"  - Level: {self.logging.log_level}",
            f"  - Format: {self.logging.log_format}",
            f"  - File: {self.logging.log_file or 'stdout only'}",
            f"  - Verbose: {'✓ Enabled' if self.logging.verbose_agent_logs else '✗ Disabled'}",
            "",
            "API Server:",
            f"  - Host: {self.api.host}",
            f"  - Port: {self.api.port}",
            f"  - Debug: {'✓ Enabled' if self.api.debug else '✗ Disabled'}",
            f"  - Rate Limit: {self.api.rate_limit} req/min",
            "",
            "LLM Providers (Citation Tracking):",
            f"  - OpenAI: {'✓ Configured' if self.llm_providers.openai_api_key else '✗ Not configured'}",
            f"  - Google: {'✓ Configured' if self.llm_providers.google_api_key else '✗ Not configured'}",
            f"  - Mistral: {'✓ Configured' if self.llm_providers.mistral_api_key else '✗ Not configured'}",
            f"  - Perplexity: {'✓ Configured' if self.llm_providers.perplexity_api_key else '✗ Not configured'}",
            "",
            "Advanced:",
            f"  - Privacy Mode: {'✓ Enabled' if self.advanced.privacy_mode else '✗ Disabled'}",
            f"  - Experimental: {'✓ Enabled' if self.advanced.enable_experimental_features else '✗ Disabled'}",
            "",
            "===================================",
        ]
        return "\n".join(lines)


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance (singleton pattern).

    Returns:
        Config: Global configuration object

    Example:
        >>> from agentic_aeo.utils.config import get_config
        >>> config = get_config()
        >>> print(config.claude.api_key)
        >>> print(config.summary())
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """
    Force reload configuration from environment.

    Returns:
        Config: Newly loaded configuration object

    Example:
        >>> from agentic_aeo.utils.config import reload_config
        >>> config = reload_config()  # Reload from .env
    """
    global _config
    load_dotenv(override=True)  # Reload .env file
    _config = Config()
    return _config


# Example usage
if __name__ == "__main__":
    config = get_config()
    print(config.summary())
