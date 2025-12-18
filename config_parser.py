#!/usr/bin/env python3
import sys
import yaml
import argparse
from lark import Lark, Transformer

# ГРАММАТИКА
GRAMMAR = """
start: (const_decl | struct)*

const_decl: NAME "is" value ";"

struct: "struct" "{" pairs "}"

pairs: (pair ("," pair)*)?

pair: NAME "=" value

value: NUMBER
     | STRING
     | struct
     | const_expr

const_expr: "#(" NAME ")"

STRING: "'" /[^']*/ "'"
NUMBER: SIGNED_NUMBER
NAME: /[_a-z]+/

%import common.SIGNED_NUMBER
%import common.WS
%ignore WS
"""


class SimpleTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.constants = {}

    # Трансформация токенов
    def STRING(self, token):
        return str(token)[1:-1]

    def NUMBER(self, token):
        s = str(token)
        return float(s) if '.' in s else int(s)

    def NAME(self, token):
        return str(token)

    # Трансформация правил
    def const_decl(self, items):
        name = str(items[0])
        value = items[1]
        self.constants[name] = value
        return None

    def struct(self, items):
        pairs = items[0] if items else []
        if isinstance(pairs, list):
            return dict(pairs)
        elif isinstance(pairs, dict):
            return pairs
        return {}

    def pairs(self, items):
        return items

    def pair(self, items):
        if len(items) >= 2:
            key = str(items[0])
            value = items[1]
            return (key, value)
        return None

    def const_expr(self, items):
        name = str(items[0])
        if name not in self.constants:
            raise ValueError(f"Неизвестная константа: {name}")
        return self.constants[name]

    def value(self, items):
        return items[0]

    def start(self, items):
        result = {}
        for item in items:
            if item is not None and isinstance(item, dict):
                result.update(item)
        return result


def parse_config(text):
    """Парсинг конфигурации"""
    parser = Lark(GRAMMAR, parser='lalr', transformer=SimpleTransformer())
    return parser.parse(text)


def main():
    parser = argparse.ArgumentParser(
        description='Конвертер учебного конфигурационного языка в YAML'
    )
    parser.add_argument('-o', '--output', required=True,
                        help='Выходной YAML файл')
    parser.add_argument('-i', '--input',
                        help='Входной файл (если не указан, читает из stdin)')

    args = parser.parse_args()

    try:
        # Чтение входных данных
        if args.input:
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            text = sys.stdin.read()

        # Парсинг
        result = parse_config(text)

        # Сохранение
        with open(args.output, 'w', encoding='utf-8') as f:
            yaml.dump(result, f, allow_unicode=True,
                      default_flow_style=False)

        print(f"✅ Конфигурация преобразована в {args.output}")

    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()