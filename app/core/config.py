from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OpenStack VM Lifecycle API"
    app_version: str = "0.1.0"
    environment: str = "dev"
    log_level: str = "INFO"
    use_mock_openstack: bool = True
    allowed_origins: str = ""

    openstack_auth_url: str = ""
    openstack_username: str = ""
    openstack_password: str = ""
    openstack_project_name: str = ""
    openstack_user_domain_name: str = "Default"
    openstack_project_domain_name: str = "Default"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        if not self.allowed_origins:
            return []
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
