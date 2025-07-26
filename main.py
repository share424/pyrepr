import json
from argparse import ArgumentParser

from output_generator import generate_output_html

import tokenizer


def parse_args():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    parse_parser = subparsers.add_parser("json", help="Parse the input file")
    parse_parser.add_argument("--input", type=str, required=True)
    parse_parser.add_argument("--output", type=str, required=True)
    output_parser = subparsers.add_parser("generate", help="Generate the output file")
    output_parser.add_argument("--input", type=str, required=True)
    output_parser.add_argument("--output", type=str, required=True)
    html_parser = subparsers.add_parser("html", help="Generate the output file")
    html_parser.add_argument("--input", type=str, required=True)
    html_parser.add_argument("--output", type=str, required=True)
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.input, "r") as f:
        data = f.read()

    if args.command == "json":
        result = tokenizer.parse_dict_with_tokenizer(data)
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)

    elif args.command == "html":
        result = tokenizer.parse_dict_with_tokenizer(data)
        output = generate_output_html(result)
        with open(args.output, "w") as f:
            f.write(output)

    elif args.command == "generate":
        tokenizer.tokenize_raw(data, args.output)


if __name__ == "__main__":
    main()
