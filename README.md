# PyReprParser (PyRepr)

A Python application for parsing and visualizing Python data structures from stdout logs. This tool is designed to parse complex Python objects (lists, dictionaries, tuples, sets) that have been printed to stdout, including handling Python object representations like `<MyClass object at 0x773679cded50>`.

## Features

- **Parse Python Data Structures**: Converts stdout-printed Python lists, dictionaries, tuples, and sets into structured data
- **Object Handling**: Automatically converts Python object representations (e.g., `<ClassName object at 0x...>`) into string format
- **HTML Visualization**: Generates interactive HTML output with collapsible sections for better readability
- **Search Functionality**: Built-in search capabilities in the generated HTML viewer
- **Tokenization**: Raw tokenization support for detailed analysis of Python syntax
- **Multiple Input Types**: Supports various Python data types including nested structures

## Installation

This project requires Python 3.11+ and has no external dependencies - it uses only Python standard library modules.

```bash
# Clone the repository
git clone https://github.com/share424/pyrepr.git
cd pyrepr

# No dependencies to install - ready to use!
```

## Usage

The application provides three main commands: `json`, `html`, and `generate`.

### JSON Command

Converts Python data structures from stdout logs into structured JSON format:

```bash
python main.py json --input <input-file> --output <output-file.json>
```

**Example:**
```bash
python main.py json --input trace.log --output parsed_data.json
```

### HTML Command

Converts Python data structures from stdout logs into an interactive HTML viewer:

```bash
python main.py html --input <input-file> --output <output-file.html>
```

**Example:**
```bash
python main.py html --input trace.log --output log_viewer.html
```

### Generate Command

Tokenizes raw Python syntax and outputs detailed token information:

```bash
python main.py generate --input <input-file> --output <output-file>
```

**Example:**
```bash
python main.py generate --input trace.log --output tokens.txt
```

## Input Format

The application expects input files containing Python data structures as they would appear when printed to stdout. Examples of supported formats:

### Basic Data Structures
```python
[{'key': 'value', 'number': 42}, {'list': [1, 2, 3]}]
{'nested': {'dict': {'with': 'values'}}}
(1, 2, 'tuple', {'mixed': 'types'})
```

### Python Objects
The parser can handle Python object representations:
```python
{'event_emitter': <MyObject object at 0x773679cded50>, 'data': 'some_value'}
```

Objects like `<ClassName object at 0x...>` are automatically converted to their string representation for better readability.

### Complex Nested Structures
```python
[
    {
        'task_id': 'task_001',
        'handler': <my_module.Handler object at 0x7f8a1b2c3d40>,
        'data': [
            {'timestamp': '2024-01-01', 'values': [1, 2, 3]},
            {'timestamp': '2024-01-02', 'values': [4, 5, 6]}
        ]
    }
]
```

## Output

### JSON Output
The `json` command generates structured JSON data with:
- **Clean data structures** with Python objects converted to strings
- **Proper JSON formatting** with indentation for readability
- **Programmatic access** to parsed data for further processing
- **Type preservation** for primitives (int, float, str, bool, None)

### HTML Viewer
The `html` command generates an interactive HTML file with:
- **Collapsible sections** for large data structures
- **Syntax highlighting** for different data types
- **Search functionality** to quickly find specific content
- **Responsive design** that works on different screen sizes
- **Smart formatting** that adapts based on data size and complexity

### Token Output
The `generate` command produces detailed tokenization information showing:
- Token types (STRING, NUMBER, OP, etc.)
- Token values and positions
- JSON-formatted output for programmatic processing

## Technical Details

### Architecture
- **tokenizer.py**: Core parsing logic using Python's built-in tokenizer
- **output_generator.py**: HTML generation with Tailwind CSS styling
- **main.py**: Command-line interface and coordination

### Parsing Strategy
1. Uses Python's `tokenize` module for accurate syntax parsing
2. Implements recursive descent parsing for nested structures
3. Special handling for Python object representations (converts `<object>` patterns to strings)
4. Maintains type information during parsing (int, float, str, bool, None)

### Supported Types
- **Primitives**: `str`, `int`, `float`, `bool`, `None`
- **Collections**: `list`, `dict`, `tuple`, `set`
- **Objects**: Any Python object representation (converted to string)
- **Nested**: Arbitrarily nested combinations of the above

## Dependencies

This project has no external dependencies and uses only Python standard library modules:
- **tokenize**: For Python syntax tokenization
- **json**: For data serialization
- **io**: For string I/O operations
- **argparse**: For command-line interface
- **Python 3.11+**: Required for modern typing features

## Development

The project follows Python best practices:
- Type hints throughout the codebase
- PEP 8 compliance
- Comprehensive error handling
- Modular architecture for easy extension

## Examples

### Example Input
```
[{'user_id': 123, 'session': <auth.Session object at 0x7f123456>, 'actions': ['login', 'browse', 'logout']}, {'user_id': 456, 'session': <auth.Session object at 0x7f789abc>, 'actions': ['signup', 'profile_update']}]
```

### Example Output (JSON)
```json
[
  {
    "user_id": 123,
    "session": "<auth.Session object at 0x7f123456>",
    "actions": ["login", "browse", "logout"]
  },
  {
    "user_id": 456,
    "session": "<auth.Session object at 0x7f789abc>",
    "actions": ["signup", "profile_update"]
  }
]
```

### Example Output (HTML)
The parser will generate an interactive HTML page where:
- The sessions objects become readable strings
- User actions are displayed as expandable lists
- The entire structure is searchable
- Large objects are collapsible for better navigation

## Contributing

When contributing to this project, please:
1. Follow PEP 8 style guidelines
2. Add type hints to new functions
3. Include docstrings following Google style
4. Test with various Python data structure formats

## License

MIT
