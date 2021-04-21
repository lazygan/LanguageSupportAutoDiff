from IR import Pair,nil
import re
from collections import namedtuple, OrderedDict

iteritems = lambda d: iter(d.items())

class AbrvalgSyntaxError(Exception):

    def __init__(self, message, line, column):
        super(AbrvalgSyntaxError, self).__init__(message)
        self.message = message
        self.line = line
        self.column = column


def report_syntax_error(lexer, error):
    line = error.line
    column = error.column
    source_line = lexer.source_lines[line - 1]
    print('Syntax error: {} at line {}, column {}'.format(error.message, line, column))
    print('{}\n{}^'.format(source_line, ' ' * (column - 1)))


class Token(namedtuple('Token', ['name', 'value', 'line', 'column'])):

    def __repr__(self):
        return str(tuple(self))


def decode_str(s):
    regex = re.compile(r'\\(r|n|t|\\|\'|")')
    chars = {
        'r': '\r',
        'n': '\n',
        't': '\t',
        '\\': '\\',
        '"': '"',
        "'": "'",
    }

    def replace(matches):
        char = matches.group(1)[0]
        if char not in chars:
            raise Exception('Unknown escape character {}'.format(char))
        return chars[char]
    return regex.sub(replace, s[1:-1])


def decode_num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


class Lexer(object):

    rules = [
        ('COMMENT', r'#.*'),
        ('STRING', r'"(\\"|[^"])*"'),
        ('STRING', r"'(\\'|[^'])*'"),
        ('NUMBER', r'\d+\.\d+'),
        ('NUMBER', r'\d+'),
        ('NAME', r'[a-zA-Z_]\w*'),
        ('WHITESPACE', '[ \t]+'),
        ('NEWLINE', r'\n+'),
        ('OPERATOR', r'[\+\*\-\/%]'),       # arithmetic operators
        ('OPERATOR', r'<=|>=|==|!=|<|>'),   # comparison operators
        ('OPERATOR', r'\|\||&&'),           # boolean operators
        ('OPERATOR', r'\.\.\.|\.\.'),       # range operators
        ('OPERATOR', '!'),                  # unary operator
        ('ASSIGN', '='),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACK', r'\['),
        ('RBRACK', r'\]'),
        ('LCBRACK', '{'),
        ('RCBRACK', '}'),
        ('COLON', ':'),
        ('COMMA', ','),
    ]

    keywords = {
        'func': 'FUNCTION',
        'if': 'IF',
    }

    ignore_tokens = [
        'WHITESPACE',
        'COMMENT',
    ]

    decoders = {
        'STRING': decode_str,
        'NUMBER': decode_num,
    }

    def __init__(self):
        self.source_lines = []
        self._regex = self._compile_rules(self.rules)

    def _convert_rules(self, rules):
        grouped_rules = OrderedDict()
        for name, pattern in rules:
            grouped_rules.setdefault(name, [])
            grouped_rules[name].append(pattern)

        for name, patterns in iteritems(grouped_rules):
            joined_patterns = '|'.join(['({})'.format(p) for p in patterns])
            yield '(?P<{}>{})'.format(name, joined_patterns)

    def _compile_rules(self, rules):
        return re.compile('|'.join(self._convert_rules(rules)))

    def _tokenize_line(self, line, line_num):
        pos = 0
        while pos < len(line):
            matches = self._regex.match(line, pos)
            if matches is not None:
                name = matches.lastgroup
                pos = matches.end(name)
                if name not in self.ignore_tokens:
                    value = matches.group(name)
                    if name in self.decoders:
                        value = self.decoders[name](value)
                    elif name == 'NAME' and value in self.keywords:
                        name = self.keywords[value]
                        value = None
                    yield Token(name, value, line_num, matches.start() + 1)
            else:
                raise AbrvalgSyntaxError('Unexpected character {}'.format(line[pos]), line_num, pos + 1)

    def _count_leading_characters(self, line, char):
        count = 0
        for c in line:
            if c != char:
                break
            count += 1
        return count

    def _detect_indent(self, line):
        if line[0] in (' ', '\t'):
            return line[0] * self._count_leading_characters(line, line[0])

    def tokenize(self, s):
        indent_symbol = None
        tokens = []
        last_indent_level = 0
        line_num = 0
        for line_num, line in enumerate(s.splitlines(), 1):
            line = line.rstrip()

            if not line:
                self.source_lines.append('')
                continue

            if indent_symbol is None:
                indent_symbol = self._detect_indent(line)

            #这个地方需要排除注释,写法上注意下
            if indent_symbol is not None and line[0]!="#":
                indent_level = line.count(indent_symbol)
                line = line[indent_level*len(indent_symbol):]
            else:
                indent_level = 0

            self.source_lines.append(line)

            line_tokens = list(self._tokenize_line(line, line_num))
            if line_tokens:
                if indent_level != last_indent_level:
                    if indent_level > last_indent_level:
                        tokens.extend([Token('INDENT', None, line_num, 0)] * (indent_level - last_indent_level))
                    elif indent_level < last_indent_level:
                        tokens.extend([Token('DEDENT', None, line_num, 0)] * (last_indent_level - indent_level))
                    last_indent_level = indent_level

                tokens.extend(line_tokens)
                tokens.append(Token('NEWLINE', None, line_num, len(line) + 1))

        if last_indent_level > 0:
            tokens.extend([Token('DEDENT', None, line_num, 0)] * last_indent_level)

        return tokens


class TokenStream(object):

    def __init__(self, tokens):
        self._tokens = tokens
        self._pos = 0

    def consume_expected(self, *args):
        token = None
        for expected_name in args:
            token = self.consume()
            if token.name != expected_name:
                raise AbrvalgSyntaxError('Expected {}, got {}'.format(expected_name, token.name), token.line, token.column)
        return token

    def consume(self):
        token = self.current()
        self._pos += 1
        return token

    def current(self):
        try:
            #print(self._tokens[self._pos])
            return self._tokens[self._pos]
        except IndexError:
            last_token = self._tokens[-1]
            raise AbrvalgSyntaxError('Unexpected end of input', last_token.line, last_token.column)

    def expect_end(self):
        if not self.is_end():
            token = self.current()
            raise AbrvalgSyntaxError('End expected', token.line, token.column)

    def is_end(self):
        return self._pos == len(self._tokens)


class Subparser(object):
    PRECEDENCE = {
        'call': 10,
        'unary': 9,
        '*': 7,
        '/': 7,
        '%': 7,
        '+': 6,
        '-': 6,
    }
    def get_subparser(self, token, subparsers, default=None):
        cls = subparsers.get(token.name, default)
        if cls is not None:
            return cls()


class PrefixSubparser(Subparser):

    def parse(self, parser, tokens):
        raise NotImplementedError()


class InfixSubparser(Subparser):

    def parse(self, parser, tokens, left):
        raise NotImplementedError()

    def get_precedence(self, token):
        raise NotImplementedError()


# number_expr: NUMBER
class NumberExpression(PrefixSubparser):
    def parse(self, parser, tokens):
        token = tokens.consume_expected('NUMBER')
        return token.value




# name_expr: NAME
class NameExpression(PrefixSubparser):
    def parse(self, parser, tokens):
        token:Token = tokens.consume_expected('NAME')
        return token.value



# prefix_expr: OPERATOR expr
class UnaryOperatorExpression(PrefixSubparser):
    SUPPORTED_OPERATORS = ['-', '!']
    def parse(self, parser, tokens):
        token = tokens.consume_expected('OPERATOR')
        if token.value not in self.SUPPORTED_OPERATORS:
            raise AbrvalgSyntaxError('Unary operator {} is not supported'.format(token.value), token)
        right = Expression().parse(parser, tokens, self.get_precedence(token))
        if right is None:
            raise AbrvalgSyntaxError('Expected expression'.format(token.value), tokens.consume())
        return right

    def get_precedence(self, token):
        return self.PRECEDENCE['unary']


# group_expr: LPAREN expr RPAREN
class GroupExpression(PrefixSubparser):
    def parse(self, parser, tokens):
        tokens.consume_expected('LPAREN')
        right = Expression().parse(parser, tokens)
        tokens.consume_expected('RPAREN')
        return right


# infix_expr: expr OPERATOR expr
class BinaryOperatorExpression(InfixSubparser):
    def parse(self, parser, tokens, left):
        token = tokens.consume_expected('OPERATOR')
        right = Expression().parse(parser, tokens, self.get_precedence(token))
        if right is None:
            raise AbrvalgSyntaxError('Expected expression'.format(token.value), tokens.consume())
        return Pair(token.value,Pair(left,Pair(right,nil)))

    def get_precedence(self, token):
        return self.PRECEDENCE[token.value]


# call_expr: NAME LPAREN list_of_expr? RPAREN
class CallExpression(InfixSubparser):
    def parse(self, parser, tokens, left):
        tokens.consume_expected('LPAREN')
        arguments = ListOfExpressions().parse(parser, tokens)
        tokens.consume_expected('RPAREN')
        return Pair(left,arguments)


    def get_precedence(self, token):
        return self.PRECEDENCE['call']


# expr: number_expr | str_expr | name_expr | group_expr | array_expr | dict_expr | prefix_expr | infix_expr | call_expr
#     | subscript_expr
class Expression(Subparser):
    def get_prefix_subparser(self, token):
        return self.get_subparser(token, {
            'NUMBER': NumberExpression,
            'NAME': NameExpression,
            'LPAREN': GroupExpression,
            'OPERATOR': UnaryOperatorExpression,
        })

    def get_infix_subparser(self, token):
        return self.get_subparser(token, {
            'OPERATOR': BinaryOperatorExpression,
            'LPAREN': CallExpression,
        })

    def get_next_precedence(self, tokens):
        if not tokens.is_end():
            token = tokens.current()
            parser = self.get_infix_subparser(token)
            if parser is not None:
                return parser.get_precedence(token)
        return 0

    def parse(self, parser, tokens, precedence=0):
        subparser = self.get_prefix_subparser(tokens.current())
        if subparser is not None:
            left = subparser.parse(parser, tokens)
            if left is not None:
                while precedence < self.get_next_precedence(tokens):
                    op = self.get_infix_subparser(tokens.current()).parse(parser, tokens, left)
                    if op is not None:
                        left = op
                return left


## list_of_expr: (expr COMMA)*
class ListOfExpressions(Subparser):
    def parse(self, parser, tokens):
        head = None
        p = None
        while not tokens.is_end():
            exp = Expression().parse(parser, tokens)
            if exp is not None:
                if head==None:
                    head=Pair(exp,nil)
                    p=head
                else:
                    p.second=Pair(exp,nil)
                    p=p.second
            else:
                return head
            if tokens.current().name == 'COMMA':
                tokens.consume_expected('COMMA')
            else:
                return head
        return nil


# block: NEWLINE INDENT stmnts DEDENT
class Block(Subparser):
    def parse(self, parser, tokens):
        tokens.consume_expected('NEWLINE', 'INDENT')
        statements = Statements().parse(parser, tokens)
        tokens.consume_expected('DEDENT')
        return statements




# assing_stmnt: expr ASSIGN expr NEWLINE
class AssignmentStatement(Subparser):
    def parse(self, parser, tokens, left):
        tokens.consume_expected('ASSIGN')
        right = Expression().parse(parser, tokens)
        tokens.consume_expected('NEWLINE')
        return Pair("define",Pair(left,Pair(right,nil)))


# expr_stmnt: assing_stmnt
#           | expr NEWLINE
class ExpressionStatement(Subparser):
    def parse(self, parser, tokens):
        exp = Expression().parse(parser, tokens)
        if exp is not None:
            if tokens.current().name == 'ASSIGN':
                return AssignmentStatement().parse(parser, tokens, exp)
            else:
                tokens.consume_expected('NEWLINE')
                return exp



# func_stmnt: FUNCTION NAME LPAREN func_params? RPAREN COLON block
class FunctionStatement(Subparser):
    # func_params: (NAME COMMA)*
    def _parse_params(self, tokens):
        head=None
        p=None
        if tokens.current().name == 'NAME':
            while not tokens.is_end():
                id_token = tokens.consume_expected('NAME')
                if head==None:
                    head = Pair(id_token.value,nil)
                    p=head
                else:
                    p.second=Pair(id_token.value,nil)
                    p = p.second
                if tokens.current().name == 'COMMA':
                    tokens.consume_expected('COMMA')
                else:
                    return head
        return nil
    def parse(self, parser, tokens):
        tokens.consume_expected('FUNCTION')
        id_token = tokens.consume_expected('NAME')
        tokens.consume_expected('LPAREN')
        arguments = self._parse_params(tokens)
        tokens.consume_expected('RPAREN', 'COLON')
        block = Block().parse(parser, tokens)
        return Pair("define",Pair(Pair(id_token.value,arguments),block))




# stmnts: stmnt*
class Statements(Subparser):
    def get_statement_subparser(self, token):
            return self.get_subparser(token, {'FUNCTION': FunctionStatement }, ExpressionStatement)

    def parse(self, parser, tokens:TokenStream):
        head=Pair(self.get_statement_subparser(tokens.current()).parse(parser, tokens),nil)
        statement=head
        while not tokens.is_end():
            if(tokens.current().name=="DEDENT"):
                break
            statement.second=Pair(self.get_statement_subparser(tokens.current()).parse(parser, tokens),nil)
            statement=statement.second
        return head



# prog: stmnts
class Program(Subparser):
    def parse(self, parser, tokens):
        statements = Statements().parse(parser, tokens)
        tokens.expect_end()
        return statements



class Parser(object):
    def parse(self, tokens):
        return Program().parse(self, tokens)
