from Image import open as imgopen
from StringIO import StringIO
from magic import from_buffer as magic_buffer
from os import rmdir, listdir, path
from shutil import rmtree
from subprocess import call
from tempfile import NamedTemporaryFile, mkdtemp


def get_images_from_stream(stream):
    with NamedTemporaryFile() as inputfile:
        data = stream.read()
        magic = magic_buffer(data)
        if magic.startswith('JPEG') or magic.startswith('Netpbm'):
            return [data]
        elif magic.startswith('PDF'):
            tmpdir = mkdtemp()
            inputfile.write(data)
            inputfile.file.flush()
            try:
                call(["pdfimages", "-j", inputfile.name, tmpdir + '/'])
                return [file(path.join(tmpdir, x)).read() for x in
                        listdir(tmpdir)]
            finally:
                rmtree(tmpdir)
        else:
            raise ValueError("Cannot handle file format:", magic)


def get_thumbnail(img):
    with NamedTemporaryFile() as thumb:
        img = imgopen(StringIO(img))
        img.thumbnail((300, 300))
        img.save(thumb.name, "JPEG")
        thumb.file.flush()
        return thumb.read()
