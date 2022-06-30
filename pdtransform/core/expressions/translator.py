from dataclasses import dataclass
from typing import Generic, TYPE_CHECKING, TypeVar

from pdtransform.core import column
from pdtransform.core.expressions import expressions, operator_registry

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from pdtransform.core.table_impl import AbstractTableImpl

ImplT = TypeVar('ImplT', bound = 'AbstractTableImpl')
T = TypeVar('T')

# Basic container to store value and associated type metadata
@dataclass(slots = True)
class TypedValue(Generic[T]):
    value: T
    dtype: str
    ftype: str = 's'  # One of 's', 'a' or 'w'

    def __iter__(self):
        return iter((self.value, self.dtype))


class Translator(Generic[T]):
    def translate(self, expr, **kwargs) -> T:
        """ Translate an expression recursively. """
        try:
            return bottom_up_replace(expr, lambda e: self._translate(e, **kwargs))
        except Exception as e:
            raise ValueError(f"An exception occured while trying to translate the expression '{expr}':\n"
                            f"{e}") from e

    def _translate(self, expr, **kwargs) -> T:
        """ Translate an expression non recursively. """
        raise NotImplementedError


class DelegatingTranslator(Generic[T], Translator[T]):
    """
    Translator that dispatches to different translate functions based on
    the type of the expression.
    """

    def __init__(self, operator_registry: operator_registry.OperatorRegistry):
        self.operator_registry = operator_registry

    def _translate(self, expr, **kwargs):
        if isinstance(expr, column.Column):
            return self._translate_col(expr, **kwargs)

        if isinstance(expr, expressions.FunctionCall):
            arguments = [arg.value for arg in expr.args]
            signature = tuple(arg.dtype for arg in expr.args)
            implementation = self.operator_registry.get_implementation(expr.operator, signature)
            return self._translate_function(expr, arguments, implementation, **kwargs)

        if literal_result := self._translate_literal(expr, **kwargs):
            return literal_result

        raise NotImplementedError(f"Couldn't find a way to translate object of type {type(expr)} with value {expr}.")

    def _translate_col(self, expr: 'column.Column', **kwargs) -> T:
        raise NotImplementedError

    def _translate_function(
            self, expr: 'expressions.FunctionCall',
            arguments: list, implementation: operator_registry.TypedOperatorImpl,
            **kwargs) -> T:
        raise NotImplementedError

    def _translate_literal(self, expr, **kwargs) -> T:
        raise NotImplementedError


def bottom_up_replace(expr, replace):
    # TODO: This is bad... At some point this should be refactored
    #       and replaced with something less hacky.

    def clone(expr):
        if isinstance(expr, expressions.FunctionCall):
            f = expressions.FunctionCall(
                expr.operator,
                *(clone(arg) for arg in expr.args),
                **{k: clone(v) for k, v in expr.kwargs.items()}
            )
            return replace(f)
        else:
            return replace(expr)

    return clone(expr)
