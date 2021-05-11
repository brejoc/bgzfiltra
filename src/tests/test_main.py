__author__ = "Jochen Breuer"
__email__ = "jbreuer@suse.de"
__license__ = "MIT"

import pytest
from mock import MagicMock, Mock, PropertyMock

from bgzfiltra import is_l3
from bgzfiltra import group_bugs_by_component
from bgzfiltra import has_needinfo


class TestHasNeedinfo:
    def test_has_needinfo(self):
        bug = Mock()
        bug.flags = ({"name": "needinfo"}, {"something": "else"})
        assert has_needinfo(bug)

    def test_has_no_needinfo(self):
        bug = Mock()
        bug.flags = ({"name": "other"}, {"something": "else"})
        assert not has_needinfo(bug)

    def test_has_other_flags(self):
        bug = Mock()
        bug.flags = ({"foo": "bar"}, {"something": "else"})
        assert not has_needinfo(bug)

    def test_emtpy_flags(self):
        bug = Mock()
        bug.flags = ()
        assert not has_needinfo(bug)


class TestIsL3:
    def test_open_l3(self):
        openl3 = Mock()
        openl3.whiteboard = "foo:bar openL3:12359 bar:baz"
        assert is_l3(openl3)

    def test_closed_l3(self):
        wasl3 = Mock()
        wasl3.whiteboard = "foo:bar wasL3:12359 bar:baz"
        assert is_l3(wasl3)

    def test_no_l3(self):
        nol3 = Mock()
        nol3.whiteboard = "foo:bar noL3:12359 bar:baz"
        assert not is_l3(nol3)

    def test_blank_whitespace_bug(self):
        nol3 = Mock()
        nol3.whiteboard = ""
        assert not is_l3(nol3)

    def test_normal_bug(self):
        nol3 = Mock()
        nol3.whiteboard = "foo:bar nol3:no reproducer:c0"
        assert not is_l3(nol3)


class TestGroupBugsByComponent:
    def test_one_component(self):
        bug = Mock()
        bug.component = "Test Component"
        grouped_bugs = group_bugs_by_component((bug,))
        assert bug in grouped_bugs["Test Component"]

    def test_multiple_components(self):
        bug1 = Mock()
        bug1.component = "Test Component"
        bug2 = Mock()
        bug2.component = "Test Component"
        grouped_bugs = group_bugs_by_component((bug1, bug2))
        assert bug1 in grouped_bugs["Test Component"]
        assert bug2 in grouped_bugs["Test Component"]

    def test_multiple_different_components(self):
        bug1 = Mock()
        bug1.component = "Test Component"
        bug2 = Mock()
        bug2.component = "Test Component2"
        bug3 = Mock()
        bug3.component = "Test Component2"
        grouped_bugs = group_bugs_by_component((bug1, bug2, bug3))
        assert bug1 in grouped_bugs["Test Component"]
        assert bug2 not in grouped_bugs["Test Component"]
        assert bug3 not in grouped_bugs["Test Component"]
        assert bug2 in grouped_bugs["Test Component2"]
        assert bug3 in grouped_bugs["Test Component2"]
        assert bug1 not in grouped_bugs["Test Component2"]
