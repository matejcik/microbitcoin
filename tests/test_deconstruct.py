import pytest

import bitcoinformats.digistruct as d


class Example(d.Struct):
    x: d.little.int16
    y: "d.little.int32"
    z: d.little.int64 = d.field()

    def hello(self) -> None:
        print("hello", self.x)


def test_example():
    e = Example(x=1, y=2, z=3)
    assert e.build() == b"\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00"

    ep = Example.parse(b"\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00")
    assert ep.x == 1
    assert ep.y == 2
    assert ep.z == 3

    assert e.sizeof() == 2 + 4 + 8


class TwoByteSum(d.Adapter[int]):
    x: d.little.int8
    y: d.little.int8

    @classmethod
    def encode(cls, value: int):
        x = value // 2
        if x + x != value:
            y = x + 1
        else:
            y = x
        return cls(x=x, y=y)

    def decode(self) -> int:
        return self.x + self.y


class Adapted(d.Struct):
    x: TwoByteSum


def test_adapter():
    a = TwoByteSum(x=1, y=2)
    assert a.build() == b"\x01\x02"
    assert TwoByteSum.parse(b"\x01\x02") == a

    ad = Adapted(x=3)
    assert ad.build() == b"\x01\x02"
    assert Adapted.parse(b"\x05\x04").x == 9


# class Arrays(d.Struct):
#     fixed: list[d.be.int8] = d.array(3)
#     prefixed: list[d.be.int8] = d.array(prefix=d.be.int8)
#     count: d.be.int8 = d.auto()
#     variable: list[d.be.int8] = d.array(count)


def test_arrays():
    a = Arrays(fixed=[1, 2, 3], prefixed=[4, 5, 6], variable=[7, 8])
    assert a.build() == b"\x01\x02\x03\x03\x04\x05\x06\x02\x07\x08"

    ap = Arrays.parse(b"\x01\x02\x03\x03\x04\x05\x06\x02\x07\x08")
    assert ap.fixed == [1, 2, 3]
    assert ap.prefixed == [4, 5, 6]
    assert ap.count == 2
    assert ap.variable == [7, 8]


def test_array_variable_zero():
    a = Arrays(fixed=[1, 2, 3], prefixed=[], variable=[])
    assert a.build() == b"\x01\x02\x03\x00\x00"

    ap = Arrays.parse(b"\x01\x02\x03\x00\x00")
    assert ap.fixed == [1, 2, 3]
    assert ap.prefixed == []
    assert ap.count == 0
    assert ap.variable == []


def test_array_wrong_count():
    with pytest.raises(ValueError):
        Arrays(fixed=[1, 2, 3, 4], prefixed=[], variable=[])
