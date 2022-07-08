from .core import Window, Nullary


__all__ = [
    'Shift',
    'RowNumber',
]


class Shift(Window):
    name = 'shift'
    signatures = [
        'T, int -> T',
        'T, int, T -> T',
    ]


class RowNumber(Window, Nullary):
    name = 'row_number'
    signatures = [
        '-> int',
    ]
