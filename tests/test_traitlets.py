# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

from unittest import TestCase
from pygge.traitlets import Int2d, Float2d, PositiveInt
from pygge.data_types import TwoTuple
import numpy as np
from traitlets import HasTraits, TraitError


class TestTwoTuppleTraits(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.other_2d = {
            "tuple": (1, 2),
            "list":  [1, 2],
            "array": np.array([1, 2])
        }
        cls.other_wrong = {
            "type": "threeve",
            "shape": np.array([[1, 2], [3, 4]]),
            "length": (1, 2, 3)
        }

    def setUp(self):
        class HasTestable(HasTraits):
            int2d = Int2d()
            float2d = Float2d(default_value=(0, 1.5))
            pos2d = PositiveInt()

        self.ht = HasTestable()
        self.other_ht = HasTestable()

    def test_default(self):
        self.assertEqual(self.ht.int2d, Int2d.default_value)

    def test_len(self):
        self.assertEqual(2, len(self.ht.int2d))

    def test_set(self):
        for k, v in self.other_2d.items():
            with self.subTest(f"Set to {k}"):
                self.ht.int2d = v
        with self.subTest("Set to self-like"):
            self.ht.int2d = self.other_ht.float2d

        for k, v in self.other_wrong.items():
            with self.subTest(f"Fail to set to {k}"):
                with self.assertRaises(TraitError):
                    self.ht.int2d = v

        with self.subTest("Set by index"):
            with self.assertRaises(TypeError):
                self.ht.int2d[0] = 1
        with self.subTest("Set by attribute"):
            with self.assertRaises(TypeError):
                self.ht.int2d.x = 1

    def test_get(self):
        self.ht.int2d = (1, 2)
        self.assertEqual((1, 2), self.ht.int2d)
        self.assertEqual(1, self.ht.int2d.x)
        self.assertEqual(2, self.ht.int2d.y)
        self.assertEqual(1, self.ht.int2d[0])
        self.assertEqual(2, self.ht.int2d[1])

    def test_casting(self):
        self.assertIsInstance(self.ht.int2d, TwoTuple)
        self.assertIsInstance(self.ht.int2d.astuple(), tuple)
        self.assertIsInstance(self.ht.int2d.aslist(), list)
        self.assertIsInstance(self.ht.int2d.asarray(), np.ndarray)

    def test_type_preservation(self):
        raise NotImplementedError

    def test_equality(self):
        td = self.ht.int2d

        with self.subTest("Numerics"):
            self.assertEqual(td, (0, 0))
            self.assertNotEqual(td, (1, 0))

        with self.subTest("Floating point"):
            self.assertEqual(td, (0, 1e-8))

        with self.subTest("Wrong length"):
            with self.assertRaises(TypeError):
                td == (0, 1, 2)

        with self.subTest("Nonsense"):
            with self.assertRaises(TypeError):
                td == 5

    def test_inequality(self):
        raise NotImplementedError

    def _build_other_types(self, other):
        self.other_ht.int2d = other
        self.other_ht.float2d = other
        return (
            ("int2d", self.other_ht.int2d),
            ("float2d", self.other_ht.float2d),
            ("tuple", other),
            ("list", list(other)),
            # ("Array", np.array(other)),
            # ("Floaty", np.array(other) + 1e-8),
            # I multiply numpy fine, but numpy behaves poorly when it comes first.
        )

    def test_additive(self):
        self.ht.int2d = (-1, 1)
        td = self.ht.int2d
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
        self.ht.float2d = (-10, 7)
        td = self.ht.float2d
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

    def test_clamp(self):
        self.ht.float2d = (1, 3)
        td = self.ht.float2d
        with self.subTest("Min only"):
            self.assertEqual(td.clamp(min_=(2, 2)), (2, 3))

        with self.subTest("Max only"):
            self.assertEqual(td.clamp(max_=(2, 2)), (1, 2))

        with self.subTest("Min and max"):
            self.assertEqual(td.clamp(max_=(2, 2), min_=(2, 2)), (2, 2))

        with self.subTest("No limits"):
            with self.assertRaises(ValueError):
                td.clamp()

    def test_positive_math(self):
        print(self.ht.__dir__())
        print(self.ht.int2d)
        # with self.subTest("Subtract"):
        #     with self.assertRaises(ValueError):
        #         self.ht.positive - 2
        #
        # with self.subTest("Multiply"):
        #     with self.assertRaises(ValueError):
        #         self.ht.positive * 0
        #
        # with self.subTest("Divide"):
        #     with self.assertRaises(ValueError):
        #         -2 / self.ht.positive
