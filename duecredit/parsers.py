import re

def extract_references_from_rst(rst):
    # for now will be very simple, just trying to separate
    # then up until the end or another section starting
    pass

def test_extract_references_from_rst():
    # some obscure examples of how people specify references
    samples = [
        """
    References
    ----------
    .. [1] line1
           line2

    .. [2] line11
           line12

        """,

        """
    References
    ----------

    - line1
      line2

        """,

        """
        References
        ----------

        .. [xyz1] line1
           line2

        .. [xyz2] line11
           line12


        Buga duga
        ---------
        """,

        """
        References
        ----------

        line1
        line2

        line11
        line12
        """
        ]
    extract_references_from_rst(samples[0])
