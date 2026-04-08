import pytest
from unittest.mock import patch, MagicMock

with patch("backend.core.config_loader.ConfigLoader.__new__", return_value=MagicMock()):
    from backend.scraping.cleaner import Cleaner


@pytest.fixture
def cleaner():
    return Cleaner()


def test_normalize_colapsa_espacios_multiples(cleaner):
    result = cleaner._normalize_data("hola   mundo  que  tal")
    assert "  " not in result


def test_normalize_colapsa_saltos_excesivos(cleaner):
    texto = "línea1\n\n\n\nlínea2"
    result = cleaner._normalize_data(texto)
    assert "\n\n\n" not in result


def test_normalize_hace_strip(cleaner):
    result = cleaner._normalize_data("   texto con espacios al inicio y al final   ")
    assert result == result.strip()


def test_normalize_preserva_acentos_y_enies(cleaner):
    result = cleaner._normalize_data("crédito vivienda Bogotá niño")
    assert "crédito" in result
    assert "Bogotá" in result
    assert "niño" in result


def test_clean_page_elimina_nav(cleaner):
    html = "<html><nav>Inicio | Productos | Contacto</nav><p>Contenido real</p></html>"
    result = cleaner.clean_page("http://test.com", html)
    assert "Inicio | Productos" not in result
    assert "Contenido real" in result


def test_clean_page_elimina_footer(cleaner):
    html = "<html><footer>© 2024 Bancolombia</footer><p>Texto válido</p></html>"
    result = cleaner.clean_page("http://test.com", html)
    assert "© 2024" not in result


def test_clean_page_elimina_scripts(cleaner):
    html = "<html><script>window.dataLayer = [];</script><p>Párrafo válido</p></html>"
    result = cleaner.clean_page("http://test.com", html)
    assert "dataLayer" not in result
    assert "Párrafo válido" in result


def test_clean_page_preserva_h1_y_parrafos(cleaner):
    html = "<html><h1>Crédito de Vivienda</h1><p>Conozca las condiciones.</p></html>"
    result = cleaner.clean_page("http://test.com", html)
    assert "Crédito de Vivienda" in result
    assert "Conozca las condiciones" in result


def test_clean_page_elimina_clases_tipo_banner(cleaner):
    html = '<html><div class="banner-principal">Oferta especial</div><p>Info real</p></html>'
    result = cleaner.clean_page("http://test.com", html)
    assert "Oferta especial" not in result
    assert "Info real" in result


def test_clean_page_html_vacio_retorna_string(cleaner):
    result = cleaner.clean_page("http://test.com", "<html></html>")
    assert isinstance(result, str)


def test_clean_page_elimina_aside(cleaner):
    html = "<html><aside>Publicidad lateral</aside><p>Contenido principal</p></html>"
    result = cleaner.clean_page("http://test.com", html)
    assert "Publicidad lateral" not in result
