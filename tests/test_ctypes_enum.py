from ctypes import c_int, Structure, sizeof

from xaiepy.typed_ctypes_enum import CEnumeration


class Foo(CEnumeration):
    A = 42
    B = 1337


class Bar(CEnumeration):
    A = 5
    B = 23


assert isinstance(Foo(Foo.A), c_int)
assert isinstance(Bar(Bar.A), c_int)

assert type(Foo.A) == int
assert Foo.A == 42
assert str(Foo(Foo.A)) == "<Foo.A: 42>"
assert str(Bar(Bar.B)) == "<Bar.B: 23>"


class FooBar(Structure):
    _pack_ = 1
    _fields_ = [("foo", Foo), ("bar", Bar)]


foobar = FooBar(Foo.A, Bar.B)

assert sizeof(foobar) == 8
assert foobar.foo.value == 42
assert foobar.bar.value == 23

assert [int(x) for x in bytes(foobar)] == [42, 0, 0, 0, 23, 0, 0, 0]
