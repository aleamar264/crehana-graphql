import json
from typing import Any

from boto3 import Session
from pydantic import Field
from pydantic_settings import (
	BaseSettings,
	PydanticBaseSettingsSource,
	SettingsConfigDict,
)


class AWSSettings(BaseSettings):
	"""Class that define and get the AWS secrets from .env, this
	is used in the following classes:

	- SecretManagerCofig

	Args:
		BaseSettings
	"""

	aws_access_key_id: str = Field(...)
	aws_secret_access_key: str = Field(...)
	region_name: str = Field(default="us-east-2")
	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
	)


aws_settings = AWSSettings()  # type: ignore


class SecretManagerCofig(PydanticBaseSettingsSource):
	"""Class that retrieve all the data from AWS Secret Manager.

	This class is used in the class :class:`BaseSettings` with custom way
	to obtain data.

	Args:
		PydanticBaseSettingsSource

	.. code-block:: python
	        class DBSettings(
	            BaseSettings
	        ):
	            @classmethod
	            def settings_customise_sources(
	                cls,
	                settings_cls: type[
	                    BaseSettings
	                ],
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
	                    SecretManagerCofig(
	                        settings_cls
	                    ),
	                    env_settings,
	                    file_secret_settings,
	                )
	"""  # noqa: E101

	def get_field_value(  # type: ignore
		self, secret_name: str = "backend_vars"
	) -> str | dict[str, Any]:
		"""
		Args:
			secret_name (str, optional): Name of the vault in AWS secret manager. Defaults to "backend_vars".

		Returns:
			str | dict[str, Any]: Return a dict with the values finded in the vault.
		"""
		session = Session(
			aws_access_key_id=aws_settings.aws_access_key_id,
			aws_secret_access_key=aws_settings.aws_secret_access_key,
			region_name=aws_settings.region_name,
		)
		client = session.client("secretsmanager")
		secret_string: str = client.get_secret_value(SecretId=secret_name)[
			"SecretString"
		]
		try:
			return json.loads(secret_string)  # type: ignore
		except json.decoder.JSONDecodeError:
			return secret_string

	def __call__(self) -> dict[str, Any]:
		return {
			name: self.get_field_value()[name]  # type: ignore
			for name, _ in self.settings_cls.model_fields.items()
		}
