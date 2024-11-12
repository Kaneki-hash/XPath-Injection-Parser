# XPath-Injection-Parser

## Overview

This script automates the process of parsing the root node and its child nodes using XPath injection. It is designed to work with web applications that are vulnerable to XPath injection and respond differently based on the validity of the injected XPath queries.

## Features

- **Determine Root Node Length:** Automatically finds the length of the root node's name.
- **Extract Root Node Name:** Extracts the name of the root node character by character.
- **Count Child Nodes:** Counts the number of child nodes under the root node.
- **Extract Child Node Names:** Extracts the names of the child nodes.
- **Extract Node Values:** Extracts the values of the child nodes.
- **Flexible Success Condition:** Checks for "Success" in the response text and measures response time for blind injections.
- **Customizable Response Time Threshold:** Allows setting a customizable response time threshold for detecting successful injections.
- **Error and Exception Handling:** Handles network errors and timeouts gracefully.
- **Optimized Character Enumeration:** Starts with more likely characters first to speed up the process.

## Prerequisites

- Python 3.x
- `requests` library (`pip install requests`)

## Usage

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Kaneki-hash/XPath-Injection-Parser.git
   cd XPath-Injection-Parser
   ```

2. **Install Required Libraries:**

   ```bash
   pip install requests
   ```

3. **Configure the Script:**
   - You may need to modify the code to suit the purpose.
   - Update the `url` variable in the script with the target web application URL.
   - Adjust the `response_time_threshold` variable if needed based on your network and server performance.

4. **Run the Script:**

   ```bash
   python xpath_injection_parser.py
   ```

## Example Output

```
Length of the root node's name: 5
Root node's name: users
Number of child nodes: 3
Child node names:
  - user
  - user
  - user
Child node values:
  - admin
  - guest
  - test
```

## Notes

- **Customization:** You can extend the script to handle more complex XML structures or different types of data by modifying the XPath expressions and character sets.
