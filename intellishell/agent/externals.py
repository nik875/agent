import os
import sys
import subprocess
import urllib
import requests


def search_web(self, query):
    """
    Perform a web search using Google's Custom Search API and return the results as a formatted
    string.
    """
    query = query.replace('"', '')
    url = f'https://www.googleapis.com/customsearch/v1?' \
        f'key={self.google_custom_search_api_key}&' \
        f'cx={self.google_custom_search_engine_id}&' \
        f'q={urllib.parse.quote_plus(query)}'
    # Check if the request was successful
    try:
        response = requests.get(url)
        # Parse the search results
        data = response.json()
        items = data.get("items", [])

        # Format the search results as a numbered list with URLs and descriptions
        result_string = ""
        for i, item in enumerate(items, start=1):
            url = item.get("link", "")
            description = item.get("snippet", "")
            result_string += f"{i}. URL: {url}\n   Description: {description}\n\n"

        # Pass the formatted results through output_mgmt
        return self.output_mgmt(result_string)
    # pylint: disable=broad-exception-caught
    except Exception as e:
        # Return the exception text if the request fails
        return self.output_mgmt(f"Failed to perform the web search. Error: {str(e)}")


class ExternalHandler:
    def __init__(self):
        self.working_directory = os.getcwd()

    def do(self, action):
        path = os.path.join(self.working_directory, 'agent_action.py')
        with open(path, 'w') as f:
            f.write(action)
        with subprocess.Popen(
            ['python', path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # Ensure the output is in text format
        ) as process:
            stdout, stderr = process.communicate()
        os.remove(path)

        # Combine stdout and stderr
        output = f"{stdout}\n{stderr}"
        return output


if __name__ == '__main__':
    eh = ExternalHandler()
    argv = sys.argv[1]
    print(eh.do(argv))

