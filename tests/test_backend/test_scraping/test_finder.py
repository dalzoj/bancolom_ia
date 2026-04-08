import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def finder():
    with patch("backend.scraping.finder.config") as mock_cfg, \
         patch("backend.scraping.finder.sync_playwright"), \
         patch("backend.scraping.finder.RobotFileParser"):

        mock_cfg.scraping_base_url = "https://www.bancolombia.com/personas"
        mock_cfg.scraping_max_pages = 50
        mock_cfg.scraping_max_depth = 3
        mock_cfg.scraping_delay = 0
        mock_cfg.scraping_respect_robots = False
        mock_cfg.scraping_output_path = "/tmp/test_output"

        with patch("backend.core.config_loader.ConfigLoader.__new__", return_value=MagicMock()):
            from backend.scraping.finder import Finder

        f = Finder()
        f._domain = "www.bancolombia.com"
        f._robot_parser = None
        return f


def test_normalize_url_path_relativo(finder):
    result = finder._normalize_url(
        "https://www.bancolombia.com/personas",
        "/personas/creditos"
    )
    assert result == "https://www.bancolombia.com/personas/creditos"


def test_normalize_url_elimina_fragmento(finder):
    result = finder._normalize_url(
        "https://www.bancolombia.com/personas",
        "/personas/ahorro#seccion-tasas"
    )
    assert "#" not in result


def test_normalize_url_elimina_query_params(finder):
    result = finder._normalize_url(
        "https://www.bancolombia.com/personas",
        "/personas?utm_source=google&utm_medium=cpc"
    )
    assert "utm_source" not in result
    assert "?" not in result


def test_normalize_url_absoluta_sin_cambios(finder):
    base = "https://www.bancolombia.com/personas"
    href = "https://www.bancolombia.com/personas/creditos/libre-inversion"
    result = finder._normalize_url(base, href)
    assert result == "https://www.bancolombia.com/personas/creditos/libre-inversion"


def test_is_internal_url_mismo_dominio(finder):
    assert finder._is_internal("https://www.bancolombia.com/personas/creditos") is True


def test_is_internal_dominio_externo(finder):
    assert finder._is_internal("https://www.davivienda.com/productos") is False


def test_is_internal_path_relativo_cuenta_como_interno(finder):
    assert finder._is_internal("/personas/ahorro/cdt") is True


def test_is_internal_google_es_externo(finder):
    assert finder._is_internal("https://www.google.com") is False


def test_extract_category_toma_segundo_segmento(finder):
    url = "https://www.bancolombia.com/personas/creditos/vivienda"
    assert finder._extract_category(url) == "creditos"


def test_extract_category_path_corto_retorna_general(finder):
    assert finder._extract_category("https://www.bancolombia.com/personas") == "general"


def test_extract_category_multiples_niveles_toma_segundo(finder):
    url = "https://www.bancolombia.com/personas/seguros/vida/termino"
    assert finder._extract_category(url) == "seguros"


def test_is_allowed_sin_robot_parser_permite_todo(finder):
    finder._robot_parser = None
    assert finder._is_allowed("https://www.bancolombia.com/personas") is True


def test_is_allowed_robot_parser_bloquea_url(finder):
    mock_parser = MagicMock()
    mock_parser.can_fetch.return_value = False
    finder._robot_parser = mock_parser
    assert finder._is_allowed("https://www.bancolombia.com/admin") is False


def test_is_allowed_robot_parser_permite_url(finder):
    mock_parser = MagicMock()
    mock_parser.can_fetch.return_value = True
    finder._robot_parser = mock_parser
    assert finder._is_allowed("https://www.bancolombia.com/personas") is True
