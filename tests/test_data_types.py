# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

from unittest import TestCase
from pygge.data_types import _is_2d, Float2d, Positive
import numpy as np


class TestIs2d(TestCase):
    def test_stuff(self):
        for collection, truth in zip(
                (
                        ([0, 1], (0, 1), np.array((0, 1))),
                        (0, 1.0, np.array([0, 1, 2]))
                ),
                (True, False)
        ):
            for x in collection:
                with self.subTest(x.__class__.__name__):
                    self.assertEqual(truth, _is_2d(x))


class TestTwoDee(TestCase):
    def test_init(self):
        with self.subTest("Two valid inputs"):
            Float2d(1, 2)

        with self.subTest("One valid input"):
            Float2d(np.array([1, 2]))

        with self.subTest("Wrong mis-match of input"):
            with self.assertRaises(TypeError):
                Float2d([0, 1], 2)

        with self.subTest("Wrong length"):
            with self.assertRaises(TypeError):
                Float2d((1, 2, 3))

        with self.subTest("Nonsense"):
            with self.assertRaises(ValueError):
                Float2d("Threeve")

    def test_equals(self):
        td = Float2d(-1, 1)
        with self.subTest("Numerics"):
            self.assertEqual(td, (-1, 1))
            self.assertNotEqual(td, (0, 0))

        with self.subTest("Floating point"):
            self.assertEqual(td, (-1 + 1e-8, 1))

        with self.subTest("Wrong length"):
            with self.assertRaises(TypeError):
                td == (0, 1, 2)

        with self.subTest("Nonsense"):
            with self.assertRaises(TypeError):
                td == 5

    @staticmethod
    def _build_other_types(other):
        return (
            ("Float2d", Float2d(*other)),
            ("Tuple", other),
            ("List", list(other)),
            # ("Array", np.array(other)),
            # ("Floaty", np.array(other) + 1e-8),
            # I multiply numpy fine, but numpy behaves poorly when it comes first.
        )

    def test_additive(self):
        td = Float2d(-1, 1)
        other = (1, 2)
        add_result = (0, 3)
        sub_result = (-2, -1)
        rsub_result = (2, 1)

        def add(a, b):
            return a + b

        def iadd(a, b):
            a += b
            return a

        def radd(a, b):
            return b + a

        def sub(a, b):
            return a - b

        def isub(a, b):
            a -= b
            return a

        def rsub(a, b):
            return b - a

        ops = (add, iadd, radd, sub, isub, rsub)
        results = (add_result, add_result, add_result, sub_result, sub_result, rsub_result)
        others = self._build_other_types(other)

        for fnc, result in zip(ops, results):
            for name, b in others:
                with self.subTest(f"{fnc.__name__}: {name}"):
                    self.assertEqual(result, fnc(td, b))

        scalar_other = 5
        scalar_add_result = (4, 6)
        scalar_sub_result = (-6, -4)
        scalar_rsub_result = (6, 4)
        scalar_results = (
            scalar_add_result,
            scalar_add_result,
            scalar_add_result,
            scalar_sub_result,
            scalar_sub_result,
            scalar_rsub_result
        )
        for fnc, result in zip(ops, scalar_results):
            with self.subTest(f"{fnc.__name__}: Scalar"):
                self.assertEqual(result, fnc(td, scalar_other))

    def test_multiplicative(self):
        td = Float2d(-10, 7)
        other = (4, 5)
        mul_result = (-40, 35)
        div_result = (-2.5, 1.4)
        rdiv_result = (-4/10, 5/7)
        floordiv_result = (-3, 1)

        def mul(a, b):
            return a * b

        def imul(a, b):
            a *= b
            return a

        def rmul(a, b):
            return b * a

        def div(a, b):
            return a / b

        def idiv(a, b):
            a /= b
            return a

        def rdiv(a, b):
            return b / a

        def floordiv(a, b):
            return a // b

        ops = (mul, imul, rmul, div, idiv, rdiv, floordiv)
        results = (
            mul_result,
            mul_result,
            mul_result,
            div_result,
            div_result,
            rdiv_result,
            floordiv_result
        )
        others = self._build_other_types(other)

        for fnc, result in zip(ops, results):
            for name, b in others:
                with self.subTest(f"{fnc.__name__}: {name}"):
                    self.assertEqual(result, fnc(td, b))

        scalar_other = 5
        scalar_mul_result = (-50, 35)
        scalar_div_result = (-2, 1.4)
        scalar_rdiv_result = (-0.5, 5/7)
        scalar_floordiv_result = (-2, 1)
        scalar_results = (
            scalar_mul_result,
            scalar_mul_result,
            scalar_mul_result,
            scalar_div_result,
            scalar_div_result,
            scalar_rdiv_result,
            scalar_floordiv_result
        )
        for fnc, result in zip(ops, scalar_results):
            with self.subTest(f"{fnc.__name__}: Scalar"):
                self.assertEqual(result, fnc(td, scalar_other))


class TestPositive(TestCase):
    def test_init(self):
        Positive(1, 2)

        with self.assertRaises(ValueError):
            Positive(0, 1)

    def test_math(self):
        with self.subTest("Subtract"):
            with self.assertRaises(ValueError):
                Positive(1, 1) - 2

        with self.subTest("Multiply"):
            with self.assertRaises(ValueError):
                Positive(1, 1) * 0

        with self.subTest("Divide"):
            with self.assertRaises(ValueError):
                -2 / Positive(1, 1)
