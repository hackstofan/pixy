import itertools


class SimplePXDataIterable(object):
    """
    An iterable implementation for working with px data (through a list of
    PXPair tuple instances). It basically just collates values and data into
    an iterable of px data dictionaries (keys are taken from values and a data
    key is added representing the data, a value key called data will be
    overwritten).
    """
    
    def __init__(self, pxpairs, *args, **kwargs):
        """
        Create a data iterable out of an px pair iterable. The pxpair
        argument should be an iterable of PXPair tuple instances
        """
        self.pxdata = self.get_pxdatadict(pxpairs)

    @staticmethod
    def get_pxdatadict(pxpairs):
        """
        Parse the the px key value pairs into an internal dictionary where
        each key is a dictionary key and its value is the px pair value.

        We ignore most of the px pairs but the VALUES("something"). Something
        like that is what we have to collate and then later on mix in with the
        data. It is likely that there are multiple VALUES("something") and
        they determine the structure of the data points in the DATA px key.

        We therefore keep them in order (and keep their title), so the
        internal data structure looks something like this:

        {
          "data": [1, 2],
          "values": [{"title": "year", "values": ["1988", "1989"]},
                     {"title": "month", "values": ["January", "February"]}]
        }

        The lists in the example above are itertool chains (iterables)
        """
        # Instantiate the dict we'll return
        pxdata = {"values": []}

        # Iterate over and parse all px key/value pairs
        for (key, values) in pxpairs:
            if key.startswith('VALUES('):
                # We remove preceeding VALUES(" and trailing ") by
                # slicing the string and grabbing values between
                # 8 (length of 'VALUES("') and -2 (last two chars)
                pxdata["values"].append({"title":key[8:-2], "values": values})
            elif key == 'DATA':
                # Lowercase the data key and use the value directly
                pxdata['data'] = values
            else:
                # We ignore all the other variables (at least in this simple
                # version)
                pass
            
        return pxdata

    def __iter__(self):
        # Grab all value titles because we need them as keys in the resulting
        value_titles = map(lambda c: c['title'], self.pxdata['values'])

        # Combine the values into an iterator by doing a product of the
        # px values in our internal px data dictionary
        combined_values = itertools.product(*itertools.imap(
            lambda c: c['values'], self.pxdata['values']))

        for value in combined_values:
            # Zip the titles and values into a dictionary and add the data
            # point then yield that
            output_dict = dict(zip(value_titles, value))
            output_dict['data'] = self.pxdata['data'].next()
            yield output_dict
