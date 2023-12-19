import os


class ReversedFile(object):
    def __init__(self, f, mode='r'):
        """
        Wraps a file object with methods that make it be read in reverse line-by-line

        if ``f`` is a filename opens a new file object

        """
        if mode != 'r':
            raise ValueError("ReversedFile only supports read mode (mode='r')")

        try:
            # likely a filename
            f = open(f)
        except TypeError:
            pass
            # print(type(f))

        self.file = f
        self.lines = self._reversed_lines()

    def _reversed_lines(self):
        "Generate the lines of file in reverse order."
        part = ''
        for block in self._reversed_blocks():
            for c in reversed(block):
                if c == '\n' and part:
                    yield part[::-1]
                    part = ''
                part += c
        if part: yield part[::-1]

    def _reversed_blocks(self, blocksize=4096):
        "Generate blocks of file's contents in reverse order."
        file = self.file

        file.seek(0, os.SEEK_END)
        here = file.tell()
        while 0 < here:
            delta = min(blocksize, here)
            here -= delta
            file.seek(here, os.SEEK_SET)
            yield file.read(delta)

    def __getattribute__(self, name):
        """ 
        Allows for the underlying file attributes to come through

        """
        try:
            # ReversedFile attribute
            return super(ReversedFile, self).__getattribute__(name)
        except AttributeError:
            # self.file attribute
            return getattr(self.file, name)

    def __iter__(self):
        """ 
        Creates iterator

        """
        return self

    def seek(self):
        raise NotImplementedError('ReversedFile does not support seek')

    def __next__(self):
        """
        Next item in the sequence

        """
        return self.lines.__next__()  # .strip('\n').split(',')

    def read(self):
        """
        Returns the entire contents of the file reversed line by line

        """
        contents = ''

        for line in self:
            contents += line

        return contents

    def readline(self):
        """
        Returns the next line from the bottom

        """
        return self.__next__()

    def readlines(self):
        """
        Returns all remaining lines from the bottom of the file in reverse

        """
        return [x for x in self]


def create_file(path):
    try:
        with open(path, 'x', encoding='utf-8') as infile:
            pass
    except FileExistsError:
        pass
