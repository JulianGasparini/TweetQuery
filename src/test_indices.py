import unittest
import json
import inverted_index
ii = inverted_index.II_BSBI("./tweets_test", "./salida_test")


def test_remover_emojis_links():
    texto_limpio = inverted_index.normalize(
        "@Pontifex_es Sigue con sus giras ecuménicas y fortaleciendo el nuevo orden mundial!  https://t.co/k0Mgok41u2  👏 😃")

    assert texto_limpio == "@Pontifex_es Sigue con sus giras ecuménicas y fortaleciendo el nuevo orden mundial!     "


def test_normalizar_fecha_devuelve_formato_epoch():
    fecha_epoch = inverted_index.normalize_date("2022-11-02 20:07:36+00:00")

    assert fecha_epoch == "1667430456"


def test_crear_doc_to_docID():
    assert ii._doc_to_docID == {"tweet1": 0, "tweet2": 1}


def test_crear_docID_to_doc():
    assert ii._docID_to_doc == {0: "tweet1", 1: "tweet2"}


def test_diccionario_terminos():
    with open("./salida_test/terminos.json", "r") as f:
        dic_term = json.load(f)
    # correr gatos mundiales selecciones argentina porque dej\u00f3 tamales ratas jugaran
    assert dic_term == {"corr": 0, "gat": 1, "mundial": 2, \
        "seleccion": 3, "argentin": 4, "dej": 5, "tamal": 6, "rat": 7, "jug": 8}


def test_lematizar_palabra():
    # Las palabras utilizadas se encuentran en los json de pruebas
    pal = ii.lematizar("correr")
    assert pal == "corr"


def test_lematizar_palabra2():
    pal = ii.lematizar("corre-?!")
    assert pal == "corr"
