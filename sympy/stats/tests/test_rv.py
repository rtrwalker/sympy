from __future__ import with_statement
from sympy import (EmptySet, FiniteSet, S, Symbol, Interval, exp, erf, sqrt,
        symbols, simplify, Eq, cos, And, Tuple, integrate, oo, sin, Sum, Basic,
        DiracDelta)
from sympy.stats import (Die, Normal, Exponential, P, E, variance, covariance,
        skewness, density, given, independent, dependent, where, pspace,
        random_symbols, sample)
from sympy.stats.rv import ProductPSpace, rs_swap, Density, NamedArgsMixin
from sympy.utilities.pytest import raises, XFAIL


def test_where():
    X, Y = Die('X'), Die('Y')
    Z = Normal('Z', 0, 1)

    assert where(Z**2 <= 1).set == Interval(-1, 1)
    assert where(
        Z**2 <= 1).as_boolean() == Interval(-1, 1).as_relational(Z.symbol)
    assert where(And(X > Y, Y > 4)).as_boolean() == And(
        Eq(X.symbol, 6), Eq(Y.symbol, 5))

    assert len(where(X < 3).set) == 2
    assert 1 in where(X < 3).set

    X, Y = Normal('X', 0, 1), Normal('Y', 0, 1)
    assert where(And(X**2 <= 1, X >= 0)).set == Interval(0, 1)
    XX = given(X, And(X**2 <= 1, X >= 0))
    assert XX.pspace.domain.set == Interval(0, 1)
    assert XX.pspace.domain.as_boolean() == \
        And(0 <= X.symbol, X.symbol**2 <= 1)

    with raises(TypeError):
        XX = given(X, X + 3)


def test_random_symbols():
    X, Y = Normal('X', 0, 1), Normal('Y', 0, 1)

    assert set(random_symbols(2*X + 1)) == set((X,))
    assert set(random_symbols(2*X + Y)) == set((X, Y))
    assert set(random_symbols(2*X + Y.symbol)) == set((X,))
    assert set(random_symbols(2)) == set()


def test_pspace():
    X, Y = Normal('X', 0, 1), Normal('Y', 0, 1)

    assert not pspace(5 + 3)
    assert pspace(X) == X.pspace
    assert pspace(2*X + 1) == X.pspace
    assert pspace(2*X + Y) == ProductPSpace(Y.pspace, X.pspace)


def test_rs_swap():
    X = Normal('x', 0, 1)
    Y = Exponential('y', 1)

    XX = Normal('x', 0, 2)
    YY = Normal('y', 0, 3)

    expr = 2*X + Y
    assert expr.subs(rs_swap((X, Y), (YY, XX))) == 2*XX + YY


def test_RandomSymbol():

    X = Normal('x', 0, 1)
    Y = Normal('x', 0, 2)
    assert X.symbol == Y.symbol
    assert X != Y

    assert X.name == X.symbol.name

    X = Normal('lambda', 0, 1) # make sure we can use protected terms
    X = Normal('Lambda', 0, 1) # make sure we can use SymPy terms


def test_RandomSymbol_diff():
    X = Normal('x', 0, 1)
    assert (2*X).diff(X)


def test_overlap():
    X = Normal('x', 0, 1)
    Y = Normal('x', 0, 2)

    raises(ValueError, lambda: P(X > Y))


def test_ProductPSpace():
    X = Normal('X', 0, 1)
    Y = Normal('Y', 0, 1)
    px = X.pspace
    py = Y.pspace
    assert pspace(X + Y) == ProductPSpace(px, py)
    assert pspace(X + Y) == ProductPSpace(py, px)


def test_E():
    assert E(5) == 5


def test_Sample():
    X = Die('X', 6)
    Y = Normal('Y', 0, 1)
    z = Symbol('z')

    assert sample(X) in [1, 2, 3, 4, 5, 6]
    assert sample(X + Y).is_Float

    P(X + Y > 0, Y < 0, numsamples=10).is_number
    assert E(X + Y, numsamples=10).is_number
    assert variance(X + Y, numsamples=10).is_number

    raises(ValueError, lambda: P(Y > z, numsamples=5))

    assert P(sin(Y) <= 1, numsamples=10) == 1
    assert P(sin(Y) <= 1, cos(Y) < 1, numsamples=10) == 1

    # Make sure this doesn't raise an error
    E(Sum(1/z**Y, (z, 1, oo)), Y > 2, numsamples=3)


def test_given():
    X = Normal('X', 0, 1)
    Y = Normal('Y', 0, 1)
    A = given(X, True)
    B = given(X, Y > 2)

    assert X == A == B


def test_dependence():
    X, Y = Die('X'), Die('Y')
    assert independent(X, 2*Y)
    assert not dependent(X, 2*Y)

    X, Y = Normal('X', 0, 1), Normal('Y', 0, 1)
    assert independent(X, Y)
    assert dependent(X, 2*X)

    # Create a dependency
    XX, YY = given(Tuple(X, Y), Eq(X + Y, 3))
    assert dependent(XX, YY)


@XFAIL
def test_dependent_finite():
    X, Y = Die('X'), Die('Y')
    # Dependence testing requires symbolic conditions which currently break
    # finite random variables
    assert dependent(X, Y + X)

    XX, YY = given(Tuple(X, Y), X + Y > 5)  # Create a dependency
    assert dependent(XX, YY)


def test_normality():
    X, Y = Normal('X', 0, 1), Normal('Y', 0, 1)
    x, z = symbols('x, z', real=True)
    dens = density(X - Y, Eq(X + Y, z))

    assert integrate(dens(x), (x, -oo, oo)) == 1

def test_Density():
    X = Die('X', 6)
    d = Density(X)
    assert d.doit() == density(X)

def test_NamedArgsMixin():
    class Foo(Basic, NamedArgsMixin):
        _argnames = 'foo', 'bar'

    a = Foo(1, 2)

    assert a.foo == 1
    assert a.bar == 2

    raises(AttributeError, lambda: a.baz)

    class Bar(Basic, NamedArgsMixin):
        pass

    raises(AttributeError, lambda: Bar(1, 2).foo)

def test_density_constant():
    assert density(3)(2) == 0
    assert density(3)(3) == DiracDelta(0)
