from PIL.Image import open as imgopen
from guess_language import guessLanguage
from os import remove
from subprocess import call
from tempfile import NamedTemporaryFile


def ocr(infile, outfile):
    return call(['cuneiform', infile, '-o', outfile])


def recognize(filedata, accepted_languages, force_detection):
    with NamedTemporaryFile() as infile:
        infile.write(filedata)
        infile.file.flush()
        with NamedTemporaryFile() as textfile:
            retval = ocr(infile.name, textfile.name)
            img = imgopen(infile.name)
            if retval:
                detected_languages = []
                lang = "UNKNOWN"
            else:
                lang = guessLanguage(textfile.read().decode('utf-8'))
                detected_languages = [lang]
            final_filename = infile.name + '-rotated'
            try:
                for rotation in (180, 90, 180, 0):
                    if lang in accepted_languages:
                        textfile.seek(0)
                        return lang, img, textfile.read().decode('utf-8')
                    img = img.rotate(rotation)
                    img.save(final_filename, "JPEG")
                    retval = ocr(final_filename, textfile.name)
                    if retval:
                        continue
                    textfile.seek(0)
                    lang = guessLanguage(textfile.read().decode('utf-8'))
                    detected_languages.append(lang)
            finally:
                try:
                    remove(final_filename)
                except OSError:
                    pass
            if force_detection:
                raise TypeError("Languages %s not in range of accepted "
                                "languages %s" %
                                (str(detected_languages),
                                 str(accepted_languages)))
            return lang, img, textfile.read().decode('utf-8')
