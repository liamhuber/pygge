# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

from unittest import TestCase
from pygge.data_types import TwoDee
import numpy as np


class TestTwoDee(TestCase):
    def test_init(self):
        with self.subTest("Two valid inputs"):
            TwoDee(1, 2)

        with self.subTest("One valid input"):
            TwoDee(np.array([1, 2]))

        with self.subTest("Wrong mis-match of input"):
            with self.assertRaises(TypeError):
                TwoDee([0, 1], 2)

        with self.subTest("Wrong length"):
            with self.assertRaises(TypeError):
                TwoDee((1, 2, 3))

        with self.subTest("Nonsense"):
            with self.assertRaises(ValueError):
                TwoDee("Threeve")

    def test_equals(self):
        td = TwoDee(-1, 1)
        with self.subTest("Numerics"):
            self.assertEqual(td, (-1, 1))
            self.assertNotEqual(td, (0, 0))

        with self.subTest("Floating point"):
            self.assertEqual(td, (-1 + 1e-8, 1 ))

        with self.subTest("Wrong length"):
            with self.assertRaises(TypeError):
                td == (0, 1, 2)

        with self.subTest("Nonsense"):
            with self.assertRaises(TypeError):
                td == 5

    def test_additive(self):
        td = TwoDee(-1, 1)
        other = (1, 2)
        add_result = (0, 3)
        sub_result = (-2, -1)

        def add(a, b):
            return a + b

        def iadd(a, b):
            a += b
            return a

        def sub(a, b):
            return a - b

        def isub(a, b):
            a -= b
            return a

        for fnc, result in zip(
                (add, iadd, sub, isub),
                (add_result, add_result, sub_result, sub_result)
        ):
            for name, b in zip(
                ["TwoDee", "Tuple", "List", "Array", "Floaty"],
                [TwoDee(*other), other, list(other), np.array(other), np.array(other) + 1e-8]
            ):
                with self.subTest(f"{fnc.__name__}: {name}"):
                    self.assertEqual(result, fnc(td, b))

    def test_multiplicative(self):
        td = TwoDee(-10, 7)
        other = (4, 5)
        mul_result = (-40, 35)
        div_result = (-2.5, 1.4)
        floordiv_result = (-3, 1)

        def mul(a, b):
            return a * b

        def imul(a, b):
            a *= b
            return a

        def div(a, b):
            return a / b

        def idiv(a, b):
            a /= b
            return a

        def floordiv(a, b):
            return a // b

        ops = (mul, imul, div, idiv, floordiv)
        results = (mul_result, mul_result, div_result, div_result, floordiv_result)
        others = (
            ("TwoDee", TwoDee(*other)),
            ("Tuple", other),
            ("List", list(other)),
            ("Array", np.array(other)),
            ("Floaty", np.array(other) + 1e-8),
        )

        for fnc, result in zip(ops, results):
            for name, b in others:
                with self.subTest(f"{fnc.__name__}: {name}"):
                    self.assertEqual(result, fnc(td, b))

        scalar_other = 5
        scalar_mul_result = (-50, 35)
        scalar_div_result = (-2, 1.4)
        scalar_floordiv_result = (-2, 1)
        scalar_results = (
            scalar_mul_result, scalar_mul_result, scalar_div_result, scalar_div_result, scalar_floordiv_result
        )
        for fnc, result in zip(ops, scalar_results):
            with self.subTest(f"{fnc.__name__}: Scalar"):
                self.assertEqual(result, fnc(td, scalar_other))



