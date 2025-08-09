from collections.abc import Iterator

from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from .utils import SecretManagerCofig


class DBSettings(BaseSettings):
	"""Custom class that retrieve the necesary data
	from AWS secret manager to connect to any db
	define.

	Args:
		BaseSettings
	"""

	password: str = Field(...)
	username: str = Field(...)
	host: str = Field(...)
	database: str = Field(...)
	drivername: str = Field(...)
	port: int = Field(...)

	@classmethod
	def settings_customise_sources(
		cls,
		settings_cls: type[BaseSettings],
		init_settings: PydanticBaseSettingsSource,
		env_settings: PydanticBaseSettingsSource,
		dotenv_settings: PydanticBaseSettingsSource,
		file_secret_settings: PydanticBaseSettingsSource,
	) -> tuple[
		PydanticBaseSettingsSource,
		SecretManagerCofig,
		PydanticBaseSettingsSource,
		PydanticBaseSettingsSource,
	]:
		return (
			init_settings,
			SecretManagerCofig(settings_cls),
			env_settings,
			file_secret_settings,
		)


def db_setting() -> Iterator[DBSettings]:
	try:
		yield DBSettings()  # type: ignore
	except Exception:
		raise
