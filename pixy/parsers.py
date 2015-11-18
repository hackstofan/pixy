import csv
import StringIO
import itertools
from collections import namedtuple
from .iterables import SimplePXDataIterable


# Named tuple to make px pairs more workable
PXPair = namedtuple('PXPair', ['key', 'value'])


class SimplePXParser(object):
    """
    Very basic iterator of PX files, does not parse the file based on its
    contents, e.g. it doesn't look at the charset first etc. It basically just
    finds all keys and values and just goes with it.
    """

    def __init__(self, pxcontent=None, *args, **kwargs):
        """
        Construct a basic PX file content parser. Passing in content is
        optional but if passed in it will be parsed and ready for consumption
        """
        if pxcontent is not None:
            self.parse(pxcontent)

    @staticmethod
    def iterate_pxpairs(pxcontent):
        """
        Split the px file content into key/value lines (each key/value data
        line is split on ';') and yields each data line (a data line can
        therefore be more than one line
        """
        # Just split it and generate stripped data lines
        return (dataline.strip() for dataline in pxcontent.split(';')
                if dataline.strip() != '')

    @staticmethod
    def split_pxpair(pxpair):
        """
        PX values have the form KEY=VALUE. Value can be multiline, split by
        commas, contain commas, and/or include equal signs. This function
        parses the the PX value into a key, value tuple.
        """

        # Split into key and value on the first '=' (value can contain '=')
        (key, value) = pxpair.split('=',1)

        # The value is a valid csv row so we can just parse the value as if
        # it were a csv row (StringIO converts the string to a file handle
        valuereader = csv.reader(StringIO.StringIO(value))

        # Each value will be an itertools chain, even if it is a single value
        # Metadata extractor will have to work based on that (after all this
        # is a simple PX file content parser
        values = itertools.chain.from_iterable(valuereader)

        # Return a PXPair named tuple with the key and the values
        return PXPair(key, values)

    def parse(self, content):
        """
        Parse px file content into an iterator of PXPair tuples and assign
        them to an instance variable (for future use) as well as returning it
        for immediate use
        """
        # We just use the itertools imap to call split_pxpairs on each
        # pxpair from the pxpairs iterator
        self.pxpairs = itertools.imap(
            self.split_pxpair, self.iterate_pxpairs(content))
        return self.pxpairs

    @property
    def data(self):
        """
        A helper property on the parser to get instant access to iterated
        data output so one can do:

        pxparser = SimplePXParser(content)
        for datapoint in pxparser.data:
            # work with datapoint

        This is just a nice thing to do.
        """
        return SimplePXDataIterable(self.pxpairs)
