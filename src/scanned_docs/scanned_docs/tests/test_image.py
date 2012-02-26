from nose.tools import raises
from pkg_resources import resource_stream, resource_filename


def test_get_images_from_image():
    from scanned_docs import image
    test_file_stream = resource_stream(__name__, 'test.jpg')

    images = image.get_images_from_stream(test_file_stream)
    test_file_stream.seek(0)

    assert len(images) == 1
    assert images[0] == test_file_stream.read()


def test_get_images_from_pdf():
    from scanned_docs import image
    from StringIO import StringIO
    test_file_stream = resource_stream(__name__, 'test.pdf')

    images = image.get_images_from_stream(test_file_stream)

    assert len(images) == 2

    # abuse the fact that get_images_from_stream would fail
    # if it's own returned images aren't jpeg
    assert len(image.get_images_from_stream(StringIO(images[0]))) == 1
    assert len(image.get_images_from_stream(StringIO(images[1]))) == 1


@raises(ValueError)
def test_get_images_from_bad():
    from scanned_docs import image
    test_file_stream = resource_stream(__name__, 'test_image.py')

    images = image.get_images_from_stream(test_file_stream)
