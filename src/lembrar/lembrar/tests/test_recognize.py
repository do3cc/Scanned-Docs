from nose.tools import raises
from pkg_resources import resource_stream
from PIL.Image import Image


def test_extract_data():
    from lembrar.recognize import recognize
    filedata = resource_stream(__name__, 'test.jpg')
    lang, img, text = recognize(filedata.read(), ['en'], True)
    assert lang == 'en'
    assert isinstance(img, Image)
    assert text == u'This is a test\n\nMore text\n\n'


@raises(TypeError)
def test_extract_data_failed_ocr():
    from lembrar import recognize
    orig_ocr = recognize.ocr
    recognize.ocr = lambda a, b: 1
    try:
        filedata = resource_stream(__name__, 'test.jpg')
        recognize.recognize(filedata.read(), ['en'], True)
    finally:
        recognize.ocr = orig_ocr


@raises(TypeError)
def test_extract_data_failed_ocr2():
    from lembrar import recognize
    filedata = resource_stream(__name__, 'test.jpg')

    def count(a, b):
        if a.endswith('jpg'):
            return 0
        else:
            return 1
    orig_ocr = recognize.ocr
    recognize.ocr = count
    try:
        recognize.recognize(filedata.read(), ['en'], True)
    finally:
        recognize.ocr = orig_ocr


def test_extract_data_ignore_failure():
    from lembrar import recognize
    orig_ocr = recognize.ocr

    def count(a, b):
        if a.endswith('jpg'):
            return 0
        else:
            return 1
    orig_ocr = recognize.ocr
    recognize.ocr = count
    try:
        filedata = resource_stream(__name__, 'test.jpg')
        lang, img, text = recognize.recognize(filedata.read(), ['en'], False)
        assert lang == 'UNKNOWN'
        assert isinstance(img, Image)
        assert text == u''

    finally:
        recognize.ocr = orig_ocr
