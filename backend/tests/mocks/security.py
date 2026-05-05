from unittest.mock import MagicMock


def mock_hash_password(password: str) -> str:
    """Мок хеширования пароля"""
    return f"hashed_{password}"


def mock_hash_token(token: str) -> str:
    """Мок хеширования токена"""
    return f"hash_{token}"


def mock_verify_password(plain_password: str, hashed_password: str) -> bool:
    """Мок проверки пароля"""
    expected_hash = mock_hash_password(plain_password)
    return hashed_password == expected_hash


def create_mock_pwd_context():
    """Создание мок-контекста для passlib"""
    mock = MagicMock()
    mock.verify = MagicMock(side_effect=lambda password, hashed: hashed == f"hashed_{password}")
    mock.hash = MagicMock(side_effect=lambda password: f"hashed_{password}")
    return mock