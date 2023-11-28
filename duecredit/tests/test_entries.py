# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##

from ..entries import Doi, Text, Url


def test_comparison() -> None:
    assert Text("123") == Text("123")
    assert Text("123") != Text("124")
    assert Text("123", "key") == Text("123", "key")
    assert Text("123", "key") != Text("123", "key1")
    assert Text("123", "key") != Text("124", "key")

    assert Doi("123/1", "key") == Doi("123/1", "key")
    assert Url("http://123/1", "key") == Url("http://123/1", "key")


def test_sugaring_api() -> None:
    assert Url("http://1.com").url == "http://1.com"
    assert Doi("1.com").doi == "1.com"
