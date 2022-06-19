from pdtransform.core.column import LambdaColumn
from pdtransform.core.expressions import SymbolicExpression


class LambdaColumnGetter:
    """
    An instance of this object can be used to instantiate a LambdaColumn.
    """
    def __getattr__(self, item):
        return SymbolicExpression(LambdaColumn(item))

    def __getitem__(self, item):
        return SymbolicExpression(LambdaColumn(item))


# Global instance of LambdaColumnGetter.
λ = LambdaColumnGetter()