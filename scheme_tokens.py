import string
import sys

_NUMERAL_STARTS = set(string.digits) | set('+-.')
_SYMBOL_CHARS = (set('!$%&*/:<=>?@^_~') | set(string.ascii_lowercase) |
                 set(string.ascii_uppercase) | _NUMERAL_STARTS)

_WHITESPACE = set(' \t\n\r')
_SINGLE_CHAR_TOKENS = set("()")
_TOKEN_END = _WHITESPACE | _SINGLE_CHAR_TOKENS
DELIMITERS = _SINGLE_CHAR_TOKENS

def valid_symbol(s):
    """Returns whether s is a well-formed symbol."""
    if len(s) == 0:
        return False
    for c in s:
        if c not in _SYMBOL_CHARS:
            return False
    return True

def next_candidate_token(line, k):
    while k < len(line):
        c = line[k]
        if c == ';':
            return None, len(line)
        elif c in _WHITESPACE:
            k += 1
        elif c in _SINGLE_CHAR_TOKENS:
            if c == ']': c = ')'
            if c == '[': c = '('
            return c, k+1
        elif c == '#':  # Boolean values #t and #f
            return line[k:k+2], min(k+2, len(line))
        elif c == ',': # Unquote; check for @
            if k+1 < len(line) and line[k+1] == '@':
                return ',@', k+2
            return c, k+1
        else:
            j = k
            while j < len(line) and line[j] not in _TOKEN_END:
                j += 1
            return line[k:j], min(j, len(line))
    return None, len(line)

def tokenize_line(line):
    """The list of Scheme tokens on line.  Excludes comments and whitespace."""
    result = []
    text, i = next_candidate_token(line, 0)
    while text is not None:
        if text in DELIMITERS:
            result.append(text)
        elif text == 'nil':
            result.append(text)
        elif text[0] in _SYMBOL_CHARS:
            number = False
            if text[0] in _NUMERAL_STARTS:
                try:
                    result.append(int(text))
                    number = True
                except ValueError:
                    try:
                        result.append(float(text))
                        number = True
                    except ValueError:
                        pass
            if not number:
                if valid_symbol(text):
                    result.append(text.lower())
                else:
                    raise ValueError("invalid numeral or symbol: {0}".format(text))
        else:
            print("warning: invalid token: {0}".format(text), file=sys.stderr)
            print("    ", line, file=sys.stderr)
            print(" " * (i+3), "^", file=sys.stderr)
        text, i = next_candidate_token(line, i)
    return result


