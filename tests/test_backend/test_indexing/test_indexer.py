import pytest
from unittest.mock import MagicMock, patch

from backend.core.models import PrincipalData


@pytest.fixture
def indexer():
    with patch("backend.indexing.indexer.EmbeddingFactory") as mock_emb, \
         patch("backend.indexing.indexer.VectorDBFactory") as mock_vdb:

        mock_emb.create.return_value.health.return_value = True
        mock_vdb.create.return_value.health.return_value = True

        from backend.indexing.indexer import Indexer
        return Indexer()


def _pagina(texto):
    return PrincipalData(
        url="https://bancolombia.com/test",
        title="Artículo de prueba",
        extracted_date="2024-01-01",
        clean_text=texto,
        category="creditos",
    )
    

def test_texto_largo_genera_mas_de_un_chunk(indexer):
    texto = " ".join(["palabra"] * 800)
    chunks = indexer._generate_chunks_data([_pagina(texto)], chunk_size=400, overlap=50)
    assert len(chunks) > 1


def test_chunk_hereda_metadatos_de_la_pagina(indexer):
    pagina = _pagina("uno dos tres cuatro cinco")
    chunks = indexer._generate_chunks_data([pagina])

    assert chunks[0].url == pagina.url
    assert chunks[0].category == pagina.category
    assert chunks[0].title == pagina.title


def test_chunk_index_empieza_en_cero(indexer):
    texto = " ".join(["x"] * 500)
    chunks = indexer._generate_chunks_data([_pagina(texto)], chunk_size=200, overlap=0)
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1


def test_overlap_genera_igual_o_mas_chunks_que_sin_overlap(indexer):
    texto = " ".join(["a"] * 450)
    sin_overlap = indexer._generate_chunks_data([_pagina(texto)], chunk_size=400, overlap=0)
    con_overlap = indexer._generate_chunks_data([_pagina(texto)], chunk_size=400, overlap=50)
    assert len(con_overlap) >= len(sin_overlap)


def test_texto_vacio_no_genera_chunks(indexer):
    chunks = indexer._generate_chunks_data([_pagina("")])
    assert chunks == []


def test_multiples_paginas_acumulan_chunks(indexer):
    paginas = [_pagina(" ".join(["word"] * 100)) for _ in range(3)]
    chunks = indexer._generate_chunks_data(paginas, chunk_size=100, overlap=0)
    assert len(chunks) == 3


def test_chunk_text_no_esta_vacio(indexer):
    texto = " ".join(["token"] * 50)
    chunks = indexer._generate_chunks_data([_pagina(texto)])
    for chunk in chunks:
        assert chunk.chunk_text.strip() != ""
