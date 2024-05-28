"""
Provides unit tests for the YamlFileReader class.
"""

from unittest.mock import mock_open, patch

import pytest

from python_stack.core.utils.yaml_reader import (
    UnableToReadYamlFileError,
    YamlFileReader,
)


class TestYamlFileReader:
    """
    Provides unit tests for the YamlFileReader class.
    """

    def test_simple_yaml_read(self):
        """
        Tests reading a simple YAML file.
        """

        yaml_test_key = "key"
        yaml_test_value = "value"
        _data = f"""
            {yaml_test_key}: {yaml_test_value}
        """
        with patch("os.path.exists", return_value=True) as _mock_exists:
            with patch(
                "builtins.open", new_callable=mock_open, read_data=_data
            ) as _mock_open:
                yaml_reader = YamlFileReader(
                    file_path="file_path",
                    yaml_base_key=None,
                    use_environment_injection=False,
                )
                _data = yaml_reader.read()

                _mock_exists.assert_called_once_with("file_path")
                _mock_open.assert_called_once_with(
                    "file_path", "r", encoding="UTF-8"
                )

                assert _data == {yaml_test_key: yaml_test_value}

    def test_yaml_read_with_base_key(self):
        """
        Tests reading a YAML file with a base key.
        """

        yaml_test_key = "key"
        yaml_test_value = "value"
        yaml_base_key = "base_key"
        _data = f"""
            {yaml_base_key}:
                {yaml_test_key}: {yaml_test_value}
        """
        with patch("os.path.exists", return_value=True) as _mock_exists:
            with patch(
                "builtins.open", new_callable=mock_open, read_data=_data
            ) as _mock_open:
                yaml_reader = YamlFileReader(
                    file_path="file_path",
                    yaml_base_key=yaml_base_key,
                    use_environment_injection=False,
                )
                _data = yaml_reader.read()

                _mock_exists.assert_called_once_with("file_path")
                _mock_open.assert_called_once_with(
                    "file_path", "r", encoding="UTF-8"
                )

                assert _data == {yaml_test_key: yaml_test_value}

    def test_yaml_read_with_base_key_multiple_levels(self):
        """
        Tests reading a YAML file with a base key with multiple levels.
        """

        yaml_test_key = "key"
        yaml_test_value = "value"
        yaml_base_key = "base.key"
        _data = f"""
            base:
                key:
                    {yaml_test_key}: {yaml_test_value}
        """
        with patch("os.path.exists", return_value=True) as _mock_exists:
            with patch(
                "builtins.open", new_callable=mock_open, read_data=_data
            ) as _mock_open:
                yaml_reader = YamlFileReader(
                    file_path="file_path",
                    yaml_base_key=yaml_base_key,
                    use_environment_injection=False,
                )
                _data = yaml_reader.read()

                _mock_exists.assert_called_once_with("file_path")
                _mock_open.assert_called_once_with(
                    "file_path", "r", encoding="UTF-8"
                )

                assert _data == {yaml_test_key: yaml_test_value}

    def test_yaml_read_with_base_key_not_present(self):
        """
        Tests reading a YAML file with a base key not present.
        """

        yaml_test_key = "key"
        yaml_test_value = "value"
        yaml_base_key = "base_key"
        _data = f"""
            {yaml_test_key}: {yaml_test_value}
        """
        with patch("os.path.exists", return_value=True) as _mock_exists:
            with patch(
                "builtins.open", new_callable=mock_open, read_data=_data
            ) as _mock_open:
                yaml_reader = YamlFileReader(
                    file_path="file_path",
                    yaml_base_key=yaml_base_key,
                    use_environment_injection=False,
                )
                with pytest.raises(UnableToReadYamlFileError) as _e:
                    yaml_reader.read()
                _mock_exists.assert_called_once_with("file_path")
                _mock_open.assert_called_once_with(
                    "file_path", "r", encoding="UTF-8"
                )

    def test_yaml_read_with_simple_env_value_to_inject(self):
        """
        Tests reading a YAML file with a simple environment value to inject.
        """

        yaml_test_key = "key"
        yaml_test_value = "value"
        _data = f"""
            {yaml_test_key}: ${{ENV_VALUE}}
        """
        with patch("os.path.exists", return_value=True) as _mock_exists:
            with patch(
                "builtins.open", new_callable=mock_open, read_data=_data
            ) as _mock_open:
                with patch.dict("os.environ", {"ENV_VALUE": yaml_test_value}):
                    yaml_reader = YamlFileReader(
                        file_path="file_path",
                        yaml_base_key=None,
                        use_environment_injection=True,
                    )
                    _data = yaml_reader.read()

                    _mock_exists.assert_called_once_with("file_path")
                    _mock_open.assert_called_once_with(
                        "file_path", "r", encoding="UTF-8"
                    )

                    assert _data == {yaml_test_key: yaml_test_value}

    def test_yaml_read_with_list(self):
        """
        Tests reading a YAML file with a list.
        """

        yaml_test_key = "key"
        yaml_test_value = ["value1", "value2"]
        _data = f"""
            {yaml_test_key}:
                - {yaml_test_value[0]}
                - {yaml_test_value[1]}
        """
        with patch("os.path.exists", return_value=True) as _mock_exists:
            with patch(
                "builtins.open", new_callable=mock_open, read_data=_data
            ) as _mock_open:
                yaml_reader = YamlFileReader(
                    file_path="file_path",
                    yaml_base_key=None,
                    use_environment_injection=False,
                )
                _data = yaml_reader.read()

                _mock_exists.assert_called_once_with("file_path")
                _mock_open.assert_called_once_with(
                    "file_path", "r", encoding="UTF-8"
                )

                assert _data == {yaml_test_key: yaml_test_value}

    @pytest.mark.parametrize(
        "data, env_mock, expected_result",
        [
            pytest.param(
                "key: ${ENV_VALUE}",
                {"ENV_VALUE": "value"},
                {"key": "value"},
                id="simple_env_value",
            ),
            pytest.param(
                "key: ${ENV_VALUE:default}",
                {"ENV_VALUE": "value"},
                {"key": "value"},
                id="simple_env_value_with_default",
            ),
            pytest.param(
                "key: ${ENV_VALUE:default}",
                {},
                {"key": "default"},
                id="simple_env_value_with_default_not_present",
            ),
            pytest.param(
                "key: ${ENV_VALUE:${ENV_VALUE2}}",
                {"ENV_VALUE": "value", "ENV_VALUE2": "value2"},
                {"key": "value"},
                id="nested_env_value",
            ),
        ],
    )
    def test_yaml_read_with_env_value_to_inject(
        self, data, env_mock, expected_result
    ):
        """
        Tests reading a YAML file with an environment value to inject.
        """

        with patch("os.path.exists", return_value=True) as _mock_exists:
            with patch(
                "builtins.open", new_callable=mock_open, read_data=data
            ) as _mock_open:
                with patch.dict("os.environ", env_mock):
                    yaml_reader = YamlFileReader(
                        file_path="file_path",
                        yaml_base_key=None,
                        use_environment_injection=True,
                    )
                    _data = yaml_reader.read()

                    _mock_exists.assert_called_once_with("file_path")
                    _mock_open.assert_called_once_with(
                        "file_path", "r", encoding="UTF-8"
                    )

                    assert _data == expected_result
