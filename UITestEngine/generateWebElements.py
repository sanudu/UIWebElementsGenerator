import openai
import requests
import json
import time

# OpenAI API Key (Replace with your actual key)
OPENAI_API_KEY = ".."

# Function to fetch HTML from a URL
def fetch_html(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to process HTML with OpenAI
def extract_locators_with_openai(html):
    prompt = (
        "Extract a list of web elements and their unique locators from the following HTML. "
        "Provide each element in the following structured format:\n"
        "- Tag: <element tag>\n"
        "  - ID: <id if available>\n"
        "  - Class: <class if available>\n"
        "  - XPath: <XPath locator>\n"
        "  - CSS Selector: <CSS selector>\n\n"
        "Here is the HTML:\n\n"
        f"{html[:8000]}"  # Limiting input size to avoid token limits
    )

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are an expert in web scraping and front-end development."},
                  {"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY
    )

    return response["choices"][0]["message"]["content"]

# Main function to process URLs
def process_urls(input_file, output_file):
    with open(input_file, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    results = {}

    for url in urls:
        print(f"Processing {url}...")
        html = fetch_html(url)
        if not html:
            continue
        
        locators = extract_locators_with_openai(html)
        results[url] = locators

        time.sleep(1)  # Avoid hitting rate limits

    # Save the results in a structured text file
    with open(output_file, "w") as f:
        for url, locators in results.items():
            f.write(f"URL: {url}\n")
            f.write("Extracted Web Elements:\n")
            f.write(locators + "\n")
            f.write("=" * 80 + "\n\n")  # Separator for better readability

    print(f"Results saved to {output_file}")

# Run the script
process_urls("urls.txt", "output.txt")