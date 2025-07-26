import io
import itertools
import json
import token as tok
import tokenize
from typing import Generator

TOKEN_NAMES = {
    0: "ENDMARKER",
    1: "NAME",
    2: "NUMBER",
    3: "STRING",
    4: "NEWLINE",
    5: "INDENT",
    6: "DEDENT",
    7: "LPAR",
    8: "RPAR",
    9: "LSQB",
    10: "RSQB",
    11: "COLON",
    12: "COMMA",
    13: "SEMI",
    14: "PLUS",
    15: "MINUS",
    16: "STAR",
    17: "SLASH",
    18: "VBAR",
    19: "AMPER",
    20: "LESS",
    21: "GREATER",
    22: "EQUAL",
    23: "DOT",
    24: "PERCENT",
    25: "LBRACE",
    26: "RBRACE",
    27: "EQEQUAL",
    28: "NOTEQUAL",
    29: "LESSEQUAL",
    30: "GREATEREQUAL",
    31: "TILDE",
    32: "CIRCUMFLEX",
    33: "LEFTSHIFT",
    34: "RIGHTSHIFT",
    35: "DOUBLESTAR",
    36: "PLUSEQUAL",
    37: "MINEQUAL",
    38: "STAREQUAL",
    39: "SLASHEQUAL",
    40: "PERCENTEQUAL",
    41: "AMPEREQUAL",
    42: "VBAREQUAL",
    43: "CIRCUMFLEXEQUAL",
    44: "LEFTSHIFTEQUAL",
    45: "RIGHTSHIFTEQUAL",
    46: "DOUBLESTAREQUAL",
    47: "DOUBLESLASH",
    48: "DOUBLESLASHEQUAL",
    49: "AT",
    50: "ATEQUAL",
    51: "RARROW",
    52: "ELLIPSIS",
    53: "COLONEQUAL",
    54: "OP",
    55: "AWAIT",
    56: "ASYNC",
    57: "TYPE_IGNORE",
    58: "TYPE_COMMENT",
    59: "SOFT_KEYWORD",
    60: "ERRORTOKEN",
    61: "COMMENT",
    62: "NL",
    63: "ENCODING",
    64: "N_TOKENS",
    256: "NT_OFFSET",
}


class TokenGenerator:
    def __init__(self, generator: Generator[tokenize.TokenInfo, None, None]):
        self.generator = generator

    def next(self) -> tokenize.TokenInfo:
        return next(self.generator)

    def peek(self, offset: int) -> tokenize.TokenInfo:
        token_generator, peek_iter = itertools.tee(self.generator)

        for _ in range(offset):
            next(peek_iter)

        self.generator = token_generator

        return next(peek_iter)

    def next_and_expect(
        self,
        expected_type: int | None = None,
        expected_string: str | None = None,
    ) -> tokenize.TokenInfo:
        current_token = self.next()
        expected_type_str = (
            TOKEN_NAMES[expected_type] if expected_type is not None else None
        )
        current_type_str = TOKEN_NAMES[current_token.type]
        if (
            expected_type is not None
            and expected_string is not None
            and current_token.type != expected_type
            and current_token.string != expected_string
        ):
            raise ValueError(
                f"Invalid token. Expected `{expected_string}`({expected_type_str}), got `{current_token.string}`({current_type_str}): {current_token.start[1]}:{current_token.end[1]}"
            )
        if expected_type is not None and current_token.type != expected_type:
            raise ValueError(
                f"Invalid token. Expected {expected_type_str}, got {current_type_str}: {current_token.start[1]}:{current_token.end[1]}"
            )
        if expected_string is not None and current_token.string != expected_string:
            raise ValueError(
                f"Invalid token. Expected {expected_string}, got {current_token.string}: {current_token.start}-{current_token.end}"
            )
        return current_token


VALUE_TYPES = str | int | float | list | set | dict | tuple | None | bool


def parse_object_value(
    token_generator: TokenGenerator,
):
    stack = []
    value = []
    current_token = token_generator.next_and_expect(
        expected_type=tok.OP, expected_string="<"
    )
    stack.append(current_token.string)
    value.append(current_token.string)

    while True:
        current_token = token_generator.next()
        value.append(current_token.string)

        if current_token.type == tok.OP and current_token.string == ">":
            stack.pop()
            if len(stack) == 0:
                break

        if current_token.type == tok.OP and current_token.string == "<":
            stack.append("<")
            value.append("<")

    return "".join(value)


def parse_dict(
    token_generator: TokenGenerator,
) -> dict:
    token_generator.next_and_expect(expected_type=tok.OP, expected_string="{")

    data_kv = {}
    data_list = []
    mode = None

    while True:
        next_token = token_generator.peek(0)
        if next_token.type == tok.OP and next_token.string == "}":
            token_generator.next()
            break

        key = parse_value(token_generator)

        next_token = token_generator.peek(0)
        if next_token.type == tok.OP and next_token.string == "}":
            token_generator.next()
            data_list.append(key)
            break
        elif next_token.type == tok.OP and next_token.string == ":":
            if mode != "dict" and mode is not None:
                raise ValueError(
                    f"Invalid token. Expected :, got {TOKEN_NAMES[next_token.type]}: `{next_token.string}`: {next_token.start[1]}:{next_token.end[1]}"
                )
            token_generator.next()
            value = parse_value(token_generator)
            data_kv[key] = value
            mode = "dict"
            next_token = token_generator.peek(0)
            if next_token.type == tok.OP and next_token.string == ",":
                token_generator.next()
                continue
        elif next_token.type == tok.OP and next_token.string == ",":
            if mode != "set" and mode is not None:
                raise ValueError(
                    f"Invalid token. Expected `,`, got {TOKEN_NAMES[next_token.type]}: `{next_token.string}`: {next_token.start[1]}:{next_token.end[1]}"
                )
            mode = "set"
            token_generator.next()
            data_list.append(key)
            continue

    if mode == "dict":
        return data_kv
    elif mode == "set":
        return data_list
    else:
        return {}


def parse_name(
    token_generator: TokenGenerator,
):
    current_token = token_generator.next_and_expect(expected_type=tok.NAME)
    if current_token.string == "None":
        return None
    elif current_token.string == "False":
        return False
    elif current_token.string == "True":
        return True

    names = [current_token.string]
    stack = []
    while True:
        next_token = token_generator.peek(0)
        if next_token.type == tok.OP and next_token.string == ".":
            names.append(next_token.string)
            token_generator.next()
        elif next_token.type == tok.NAME:
            names.append(next_token.string)
            token_generator.next()
        elif next_token.type == tok.OP and next_token.string == "(":
            stack.append("(")
            names.append(next_token.string)
            token_generator.next()
        elif next_token.type == tok.OP and next_token.string == ")":
            stack.pop()
            names.append(next_token.string)
            token_generator.next()
            if len(stack) == 0:
                break
        elif len(stack) > 0:
            # append everything
            names.append(next_token.string)
            token_generator.next()
        else:
            break

    return "".join(names)


def parse_list(
    token_generator: TokenGenerator,
):
    token_generator.next_and_expect(expected_type=tok.OP, expected_string="[")

    data = []

    while True:
        next_token = token_generator.peek(0)
        if next_token.type == tok.OP and next_token.string == "]":
            token_generator.next()
            break
        if next_token.type == tok.OP and next_token.string == ",":
            token_generator.next()
            continue

        current_value = parse_value(token_generator)
        data.append(current_value)

    return data


def clean_token(token: tokenize.TokenInfo):
    if token.type == tok.STRING:
        return token.string.removeprefix("'").removesuffix("'")
    elif token.type == tok.NUMBER:
        if "." in token.string:
            return float(token.string)
        else:
            return int(token.string)

    raise ValueError(
        f"Invalid token. Expected STRING or NUMBER, got {TOKEN_NAMES[token.type]}: `{token.string}`: {token.start[1]}:{token.end[1]}"
    )


def parse_tuple(
    token_generator: TokenGenerator,
) -> tuple:
    token_generator.next_and_expect(expected_type=tok.OP, expected_string="(")

    data = []

    while True:
        next_token = token_generator.peek(0)
        if next_token.type == tok.OP and next_token.string == ")":
            token_generator.next()
            break
        if next_token.type == tok.OP and next_token.string == ",":
            token_generator.next()
            continue

        current_value = parse_value(token_generator)
        data.append(current_value)

    return tuple(data)


def parse_set(
    token_generator: TokenGenerator,
) -> set:
    token_generator.next_and_expect(expected_type=tok.OP, expected_string="{")

    data = []

    while True:
        next_token = token_generator.peek(0)
        if next_token.type == tok.OP and next_token.string == "}":
            token_generator.next()
            break
        if next_token.type == tok.OP and next_token.string == ",":
            token_generator.next()
            continue

        current_value = parse_value(token_generator)
        data.append(current_value)

    return data


def parse_value(
    token_generator: TokenGenerator,
) -> VALUE_TYPES:
    # get the value
    next_token = token_generator.peek(0)

    # can be a dict, list, or string
    if next_token.type == tok.OP and next_token.string == "<":
        return parse_object_value(token_generator)
    elif next_token.type in [tok.STRING, tok.NUMBER]:
        current_token = token_generator.next()
        return clean_token(current_token)
    elif next_token.type == tok.NAME:
        return parse_name(token_generator)
    elif next_token.type == tok.OP and next_token.string == "{":
        return parse_dict(token_generator)
    elif next_token.type == tok.OP and next_token.string == "[":
        return parse_list(token_generator)
    elif next_token.type == tok.OP and next_token.string == "(":
        return parse_tuple(token_generator)
    else:
        raise ValueError(
            f"Invalid token. Expected STRING, NUMBER, OP, [, or < got {TOKEN_NAMES[next_token.type]}: `{next_token.string}`: {next_token.start[1]}:{next_token.end[1]}"
        )


def tokenize_raw(data: str, output_file: str):
    dict_str = data.strip() + "\n"
    readline = io.StringIO(dict_str).readline
    token_generator = TokenGenerator(tokenize.generate_tokens(readline))

    with open(output_file, "w") as f:
        for token in token_generator.generator:
            f.write(
                json.dumps(
                    {
                        "type": TOKEN_NAMES[token.type],
                        "string": token.string,
                        "start": token.start,
                        "end": token.end,
                    }
                )
                + "\n"
            )


def parse_dict_with_tokenizer(data: str):
    dict_str = data.strip() + "\n"
    readline = io.StringIO(dict_str).readline
    token_generator = TokenGenerator(tokenize.generate_tokens(readline))

    data = parse_list(token_generator)

    return data


def print_token(token: tokenize.TokenInfo):
    print(
        {
            "type": TOKEN_NAMES[token.type],
            "string": token.string,
            "start": token.start,
            "end": token.end,
        }
    )
