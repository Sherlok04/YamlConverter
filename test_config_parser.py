#!/usr/bin/env python3
import unittest
from config_parser import parse_config


class TestConfigParser(unittest.TestCase):

    def test_simple_struct(self):
        """Тест простой структуры"""
        config = "struct { port = 8080 }"
        result = parse_config(config)
        self.assertEqual(result, {'port': 8080})

    def test_constants(self):
        """Тест констант"""
        config = """
        port is 8080;
        struct { server = #(port) }
        """
        result = parse_config(config)
        self.assertEqual(result, {'server': 8080})

    def test_nested_structs(self):
        """Тест вложенных структур"""
        config = """
        struct {
            server = struct {
                port = 8080
            }
        }
        """
        result = parse_config(config)
        expected = {'server': {'port': 8080}}
        self.assertEqual(result, expected)

    def test_strings(self):
        """Тест строк"""
        config = """
        struct {
            name = 'test'
        }
        """
        result = parse_config(config)
        self.assertEqual(result, {'name': 'test'})

    def test_multiple_pairs(self):
        """Тест нескольких пар"""
        config = """
        struct {
            host = 'localhost',
            port = 8080
        }
        """
        result = parse_config(config)
        expected = {'host': 'localhost', 'port': 8080}
        self.assertEqual(result, expected)

    def test_web_server_example(self):
        """Тест примера веб-сервера"""
        config = """
        max_conn is 1000;
        timeout is 30;

        struct {
            server = struct {
                host = 'localhost',
                port = 8080,
                limits = struct {
                    max = #(max_conn),
                    timeout = #(timeout)
                }
            }
        }
        """
        result = parse_config(config)
        expected = {
            'server': {
                'host': 'localhost',
                'port': 8080,
                'limits': {
                    'max': 1000,
                    'timeout': 30
                }
            }
        }
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()