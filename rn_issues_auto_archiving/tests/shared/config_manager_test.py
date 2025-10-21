import pytest
from unittest.mock import patch, MagicMock

from shared.data_source import DataSource
from shared.config_manager import ConfigManager


class TestConfigManager:
    @pytest.fixture()
    def data_sources(self):
        data_sources_list = []
        for _ in range(2):
            data_source = MagicMock(spec=DataSource)
            data_source.load.return_value = None
            data_sources_list.append(data_source)
        return data_sources_list

    @pytest.fixture
    def config(self):
        return MagicMock()

    def test_init(self, data_sources: list[DataSource]):
        config_manager = ConfigManager(data_sources)
        assert len(getattr(config_manager, "_ConfigManager__data_sources")) == len(
            data_sources
        )

    def test_register_data_source(self, data_sources: list[DataSource]):
        config_manager = ConfigManager()
        for data_source in data_sources:
            config_manager.register_data_source(data_source)
        assert len(getattr(config_manager, "_ConfigManager__data_sources")) == len(
            data_sources
        )

    def test_load_all(self, data_sources: list[DataSource], config):
        config_manager = ConfigManager(data_sources)
        config_manager.load_all(config)
        for data_source in data_sources:
            data_source.load.assert_called_once_with(config)  # type: ignore
