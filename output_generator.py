import json


def generate_output_html(data: list[dict]) -> str:
    """Generate HTML output with a collapsible list of JSON representations of dictionaries.

    Args:
        data: List of dictionaries to display as JSON in HTML list.

    Returns:
        HTML string containing a collapsible list with JSON representation of each dictionary.
    """
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "    <title>Data Output</title>",
        '    <script src="https://cdn.tailwindcss.com"></script>',
        "</head>",
        '<body class="bg-gray-50 p-8">',
        '    <div class="max-w-6xl mx-auto">',
        '        <h1 class="text-3xl font-bold text-gray-800 mb-6">Data List</h1>',
        "        ",
        "        <!-- Search Bar -->",
        '        <div class="mb-6">',
        '            <div class="relative">',
        '                <input type="text" id="searchInput" placeholder="Search in logs..." ',
        '                       class="w-full px-4 py-2 pl-10 pr-4 text-gray-700 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">',
        '                <div class="absolute inset-y-0 left-0 flex items-center pl-3">',
        '                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">',
        '                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>',
        "                    </svg>",
        "                </div>",
        "            </div>",
        '            <div id="searchResults" class="mt-2 text-sm text-gray-600"></div>',
        "        </div>",
        "        ",
        '        <div class="space-y-4" id="dataContainer">',
    ]

    # Group data into input/output pairs
    i = 0
    pair_number = 1

    while i < len(data):
        input_item = None
        output_item = None

        # Look for input/output pair starting from current position
        if i < len(data) and data[i].get("type") == "task":
            input_item = data[i]
            if i + 1 < len(data) and data[i + 1].get("type") == "task_result":
                output_item = data[i + 1]
                i += 2  # Skip both items
            else:
                i += 1  # Skip only input item
        elif i < len(data) and data[i].get("type") == "task_result":
            output_item = data[i]
            i += 1  # Skip output item
        else:
            # Handle items that don't match expected types
            single_item = data[i]

            # Create title from smart field detection
            try:
                name = single_item["payload"]["name"]
                title = f"{pair_number}. {name}"
            except (KeyError, TypeError):
                title = f"Item {pair_number}"

            # Generate smart content for single item
            smart_content = _generate_smart_content(single_item)
            full_json = (
                json.dumps(single_item, indent=4)
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("&", "&amp;")
            )

            html_parts.append(f"""            <div class="log-item bg-white rounded-lg shadow-md border border-gray-200" data-content="{_escape_for_search(full_json)}">
                <details>
                    <summary class="cursor-pointer p-4 font-medium text-gray-700 hover:bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                        {title}
                    </summary>
                    <div class="px-4 pb-4">
                        {smart_content}
                        <details class="mt-4">
                            <summary class="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
                                Show Raw JSON
                            </summary>
                            <div class="mt-2">
                                <pre class="bg-gray-100 p-3 rounded text-sm overflow-auto text-gray-800 font-mono">{full_json}</pre>
                            </div>
                        </details>
                    </div>
                </details>
            </div>""")

            pair_number += 1
            i += 1
            continue

        # Create title from input item if available, otherwise from output item
        try:
            if input_item:
                name = input_item["payload"]["name"]
            elif output_item:
                name = output_item["payload"]["name"]
            else:
                name = None

            title = f"{pair_number}. {name}" if name else f"Item {pair_number}"
        except (KeyError, TypeError):
            title = f"Item {pair_number}"

        # Prepare search content
        search_content_parts = []
        if input_item:
            search_content_parts.append(json.dumps(input_item, indent=4))
        if output_item:
            search_content_parts.append(json.dumps(output_item, indent=4))
        search_content = _escape_for_search(" ".join(search_content_parts))

        # Create the main collapsible item
        html_parts.append(f"""            <div class="log-item bg-white rounded-lg shadow-md border border-gray-200" data-content="{search_content}">
                <details>
                    <summary class="cursor-pointer p-4 font-medium text-gray-700 hover:bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                        {title}
                    </summary>
                    <div class="px-4 pb-4 space-y-3">""")

        # Add input section if available
        if input_item:
            smart_input_content = _generate_smart_content(input_item)
            input_json = (
                json.dumps(input_item, indent=4)
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("&", "&amp;")
            )

            html_parts.append(f"""                        <div class="bg-blue-50 rounded border border-blue-200">
                            <details>
                                <summary class="cursor-pointer p-3 font-medium text-blue-700 hover:bg-blue-100 rounded focus:outline-none focus:ring-2 focus:ring-blue-400">
                                    Input
                                </summary>
                                <div class="px-3 pb-3">
                                    {smart_input_content}
                                    <details class="mt-3">
                                        <summary class="cursor-pointer text-sm text-blue-600 hover:text-blue-700">
                                            Show Raw JSON
                                        </summary>
                                        <div class="mt-2">
                                            <pre class="bg-gray-100 p-3 rounded text-sm overflow-auto text-gray-800 font-mono">{input_json}</pre>
                                        </div>
                                    </details>
                                </div>
                            </details>
                        </div>""")

        # Add output section if available
        if output_item:
            smart_output_content = _generate_smart_content(output_item)
            output_json = (
                json.dumps(output_item, indent=4)
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("&", "&amp;")
            )

            html_parts.append(f"""                        <div class="bg-green-50 rounded border border-green-200">
                            <details>
                                <summary class="cursor-pointer p-3 font-medium text-green-700 hover:bg-green-100 rounded focus:outline-none focus:ring-2 focus:ring-green-400">
                                    Output
                                </summary>
                                <div class="px-3 pb-3">
                                    {smart_output_content}
                                    <details class="mt-3">
                                        <summary class="cursor-pointer text-sm text-green-600 hover:text-green-700">
                                            Show Raw JSON
                                        </summary>
                                        <div class="mt-2">
                                            <pre class="bg-gray-100 p-3 rounded text-sm overflow-auto text-gray-800 font-mono">{output_json}</pre>
                                        </div>
                                    </details>
                                </div>
                            </details>
                        </div>""")

        html_parts.append(
            "                    </div>\n                </details>\n            </div>"
        )
        pair_number += 1

    # Add JavaScript for search functionality
    html_parts.extend(
        [
            "        </div>",
            "    </div>",
            "    ",
            "    <script>",
            "        // Search functionality",
            "        const searchInput = document.getElementById('searchInput');",
            "        const searchResults = document.getElementById('searchResults');",
            "        const dataContainer = document.getElementById('dataContainer');",
            "        const logItems = document.querySelectorAll('.log-item');",
            "        ",
            "        function performSearch() {",
            "            const searchTerm = searchInput.value.toLowerCase().trim();",
            "            let visibleCount = 0;",
            "            ",
            "            logItems.forEach(item => {",
            "                const content = item.getAttribute('data-content').toLowerCase();",
            "                const isVisible = searchTerm === '' || content.includes(searchTerm);",
            "                ",
            "                item.style.display = isVisible ? 'block' : 'none';",
            "                if (isVisible) visibleCount++;",
            "            });",
            "            ",
            "            // Update search results",
            "            if (searchTerm === '') {",
            "                searchResults.textContent = '';",
            "            } else {",
            "                searchResults.textContent = `Found ${visibleCount} matching items`;",
            "                if (visibleCount === 0) {",
            "                    searchResults.textContent += ' - try different keywords';",
            "                    searchResults.className = 'mt-2 text-sm text-red-600';",
            "                } else {",
            "                    searchResults.className = 'mt-2 text-sm text-green-600';",
            "                }",
            "            }",
            "        }",
            "        ",
            "        // Debounced search",
            "        let searchTimeout;",
            "        searchInput.addEventListener('input', () => {",
            "            clearTimeout(searchTimeout);",
            "            searchTimeout = setTimeout(performSearch, 300);",
            "        });",
            "        ",
            "        // Keyboard shortcuts",
            "        document.addEventListener('keydown', (e) => {",
            "            if (e.ctrlKey && e.key === 'f') {",
            "                e.preventDefault();",
            "                searchInput.focus();",
            "            }",
            "        });",
            "    </script>",
            "</body>",
            "</html>",
        ]
    )

    return "\n".join(html_parts)


def _generate_smart_content(item: dict) -> str:
    """Generate smart content display based on field types and importance."""
    smart_parts = []

    # Extract key information for summary
    summary_fields = []

    # Look for common important fields
    important_keys = [
        "id",
        "name",
        "title",
        "type",
        "status",
        "message",
        "error",
        "user_query",
        "query",
        "response",
        "result",
        "timestamp",
        "time",
    ]

    def extract_nested_value(obj, key_path):
        """Extract value from nested dict using dot notation or direct key."""
        try:
            if "." in key_path:
                keys = key_path.split(".")
                value = obj
                for k in keys:
                    value = value[k]
                return value
            else:
                return obj.get(key_path)
        except (KeyError, TypeError):
            return None

    # Check for important fields in the root and common nested locations
    for key in important_keys:
        value = None

        # Try direct access
        if key in item:
            value = item[key]
        # Try payload access
        elif (
            "payload" in item
            and isinstance(item["payload"], dict)
            and key in item["payload"]
        ):
            value = item["payload"][key]
        # Try input access (for outputs that reference inputs)
        elif (
            "input" in item and isinstance(item["input"], dict) and key in item["input"]
        ):
            value = item["input"][key]

        if value is not None:
            summary_fields.append((key, value))

    # Generate summary section if we found important fields
    if summary_fields:
        smart_parts.append(
            '<div class="mb-4 p-3 bg-blue-50 rounded border-l-4 border-blue-400">'
        )
        smart_parts.append(
            '<h4 class="font-medium text-blue-800 mb-2">Key Information</h4>'
        )

        for key, value in summary_fields[:6]:  # Limit to first 6 important fields
            formatted_value = _format_smart_value(value, key)
            smart_parts.append(
                f'<div class="mb-1"><span class="font-medium text-blue-700">{key.replace("_", " ").title()}:</span> {formatted_value}</div>'
            )

        smart_parts.append("</div>")

    # Process other fields by category
    categories = {
        "Text Fields": [],
        "Numbers & Booleans": [],
        "Arrays": [],
        "Objects": [],
        "Other": [],
    }

    def categorize_fields(obj, prefix=""):
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key

            # Skip if already shown in summary
            if any(
                key.lower() == important_key.lower()
                for important_key, _ in summary_fields
            ):
                continue

            if isinstance(value, str):
                if len(value) > 100:
                    categories["Text Fields"].append((full_key, value, "long"))
                else:
                    categories["Text Fields"].append((full_key, value, "short"))
            elif isinstance(value, (int, float, bool)):
                categories["Numbers & Booleans"].append((full_key, value, "simple"))
            elif isinstance(value, list):
                categories["Arrays"].append((full_key, value, "array"))
            elif isinstance(value, dict):
                if len(value) <= 3:  # Small objects, show inline
                    categories["Objects"].append((full_key, value, "small"))
                else:  # Large objects, show as collapsible
                    categories["Objects"].append((full_key, value, "large"))
            else:
                categories["Other"].append((full_key, value, "other"))

    # Categorize root level fields
    categorize_fields(item)

    # Generate categorized content
    for category, fields in categories.items():
        if fields:
            smart_parts.append('<details class="mb-3">')
            smart_parts.append(
                f'<summary class="cursor-pointer font-medium text-gray-700 hover:text-gray-900">{category} ({len(fields)})</summary>'
            )
            smart_parts.append('<div class="mt-2 space-y-2">')

            for key, value, value_type in fields:
                formatted_value = _format_smart_value(value, key)
                smart_parts.append(
                    f'<div class="flex flex-wrap items-start"><span class="font-medium text-gray-600 mr-2 min-w-0">{key}:</span><span class="flex-1 min-w-0">{formatted_value}</span></div>'
                )

            smart_parts.append("</div>")
            smart_parts.append("</details>")

    return (
        "\n".join(smart_parts)
        if smart_parts
        else '<div class="text-gray-500 italic">No structured data detected</div>'
    )


def _format_smart_value(value, key=""):
    """Format values intelligently based on type and content."""
    if isinstance(value, str):
        if len(value) > 200:
            # Long text - show truncated with expand
            escaped = (
                value.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
            )
            truncated = escaped[:200] + "..."
            return f"""<div>
                <div class="text-gray-800">{truncated}</div>
                <details class="mt-1">
                    <summary class="cursor-pointer text-sm text-blue-600 hover:text-blue-700">Show full text</summary>
                    <div class="mt-1 p-2 bg-gray-50 rounded text-sm whitespace-pre-wrap">{escaped}</div>
                </details>
            </div>"""
        else:
            # Short text
            escaped = (
                value.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
            )
            return f'<span class="text-gray-800">{escaped}</span>'

    elif isinstance(value, list):
        if len(value) == 0:
            return '<span class="text-gray-500 italic">Empty array</span>'
        elif len(value) <= 3:
            # Small array - show all items
            items = []
            for item in value:
                if isinstance(item, str):
                    items.append(f'"{item}"')
                else:
                    items.append(str(item))
            return f'<span class="text-gray-800">[{", ".join(items)}]</span>'
        else:
            # Large array - show count and first few items
            preview_items = []
            for item in value[:3]:
                if isinstance(item, str):
                    preview_items.append(f'"{item}"')
                else:
                    preview_items.append(str(item))
            preview = ", ".join(preview_items)
            full_json = (
                json.dumps(value, indent=2)
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("&", "&amp;")
            )

            return f"""<div>
                <span class="text-gray-600">Array ({len(value)} items): [{preview}, ...]</span>
                <details class="mt-1">
                    <summary class="cursor-pointer text-sm text-blue-600 hover:text-blue-700">Show all items</summary>
                    <div class="mt-1">
                        <pre class="bg-gray-50 p-2 rounded text-sm overflow-auto">{full_json}</pre>
                    </div>
                </details>
            </div>"""

    elif isinstance(value, dict):
        if len(value) == 0:
            return '<span class="text-gray-500 italic">Empty object</span>'
        elif len(value) <= 3:
            # Small object - show key-value pairs
            pairs = []
            for k, v in value.items():
                if isinstance(v, str) and len(v) < 50:
                    pairs.append(f'{k}: "{v}"')
                else:
                    pairs.append(f"{k}: {type(v).__name__}")
            return f'<span class="text-gray-800">{{{", ".join(pairs)}}}</span>'
        else:
            # Large object - show as collapsible
            full_json = (
                json.dumps(value, indent=2)
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("&", "&amp;")
            )
            return f"""<div>
                <span class="text-gray-600">Object ({len(value)} fields)</span>
                <details class="mt-1">
                    <summary class="cursor-pointer text-sm text-blue-600 hover:text-blue-700">Expand object</summary>
                    <div class="mt-1">
                        <pre class="bg-gray-50 p-2 rounded text-sm overflow-auto">{full_json}</pre>
                    </div>
                </details>
            </div>"""

    elif isinstance(value, bool):
        color = "text-green-600" if value else "text-red-600"
        return f'<span class="{color} font-medium">{str(value)}</span>'

    elif isinstance(value, (int, float)):
        return f'<span class="text-purple-600 font-medium">{value}</span>'

    else:
        # Other types
        return f'<span class="text-gray-600">{str(value)}</span>'


def _escape_for_search(text: str) -> str:
    """Escape text for use in HTML data attributes."""
    return text.replace('"', "&quot;").replace("'", "&#39;")
