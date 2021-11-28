# coding: utf-8
# Copyright (c) Liam Huber
# Distributed under the terms of "New BSD License", see the LICENSE file.

from unittest import TestCase
from pygge.config import Config, config
from os import getcwd
from pathlib import Path


class TestConfig(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.here = Path(getcwd()).resolve().absolute()
        cls.default_out = cls.here.joinpath('out')

    @classmethod
    def tearDownClass(cls) -> None:
        cls.default_out.rmdir()

    def test_singularity(self):
        a_new_config = Config()
        self.assertIs(config, a_new_config)

    def test_ensure_directory(self):
        self.assertTrue(self.default_out.is_dir(), msg="Default location should be created at first instance")

        with self.subTest("None is valid"):
            config.out = None

        with self.subTest("Ensure new directories get created, and can be re-set"):
            config.out = './foo'
            self.assertTrue(self.here.joinpath('foo').is_dir(), msg="New location should have been created")
            config.out = './foo'
            config.out.rmdir()

        with self.subTest("Ensure paths cannot be set to a file"):
            some_file = self.here.joinpath('foo.txt')
            some_file.write_text("foobar")
            with self.assertRaises(ValueError):
                config.out = some_file
            some_file.unlink()

    def test_defaults(self):
        self.assertEqual(self.here.joinpath('out'), config.out, "Output default should be based on python instance.")
        self.assertIs(None, config.assets, "Docstrings specify None as default -- did you update the docstrings too?")



