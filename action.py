import urllib
import requests
import subprocess
import tiktoken
from googleapiclient.discovery import build

class ActionModule:
    def __init__(self, max_token_length, google_custom_search_api_key, google_custom_search_engine_id):
        """
        Initialize the ActionModule with a maximum token length, the Google Custom Search API key, and the Google Custom Search Engine ID.
        """
        self.max_token_length = max_token_length
        self.google_custom_search_api_key = google_custom_search_api_key
        self.google_custom_search_engine_id = google_custom_search_engine_id
        self.action_dict = {
            "read_file": (self.read_file, 1, "Read the content of a file. Argument: (path)"),
            "write_file": (self.write_file, 2, "Write data to a file. Arguments: (path, data)"),
            "browse_url": (self.browse_url, 1, "Access a URL and retrieve its content. Argument: (url)"),
            "search_web": (self.search_web, 1, "Perform a web search and return results. Argument: (query)"),
            "run_command": (self.run_command, 1, "Run a shell command and return output. Argument: (cmd)"),
            "present_result": (self.present_result, 1, "Output a result to the user. Argument: (result)"),
        }

    def output_mgmt(self, result):
        """
        Check the token length of the output and raise an exception if it exceeds the maximum.
        Otherwise, return the original return value.
        """
        # Tokenize the return value
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = len(encoding.encode(result))

        # Check if the number of tokens exceeds the maximum
        if tokens > self.max_token_length:
            raise Exception(f"Output token length ({tokens}) exceeds the maximum allowed ({self.max_token_length})")
        
        print(f'DEBUG: action output: {result}')
        return result

    def read_file(self, path):
        """
        Open and read the file at the given path, pass the result through output_mgmt, and return it.
        """
        with open(path, 'r') as file:
            file_contents = file.read()
        
        # Pass the file contents through output_mgmt
        return self.output_mgmt(file_contents)

    def write_file(self, path, data):
        """
        Write the given data to the file at the specified path.
        """
        with open(path, 'w') as file:
            file.write(data)

    def browse_url(self, url):
        """
        Access the given URL, download the content, pass it through output_mgmt, and return it.
        """
        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Pass the content through output_mgmt
            return self.output_mgmt(response.text)
        else:
            # Return the exception text if the request fails
            return f"Failed to access URL: {url}. Status code: {response.status_code}"

    def search_web(self, query):
        """
        Perform a web search using Google's Custom Search API and return the results as a formatted string.
        """
        url = f"https://www.googleapis.com/customsearch/v1?key={self.google_custom_search_api_key}"\
            f"&cx={self.google_custom_search_engine_id}&q={query}"
        url = urllib.parse.quote_plus(url)
        response = requests.get(url).json()
        breakpoint()

        # Check if the request was successful
        if response.status_code == 200:
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
        else:
            # Return the exception text if the request fails
            return f"Failed to perform the web search. Status code: {response.status_code}"

    def run_command(self, cmd):
        """
        Run the provided command on the shell and return the output, including stdout and stderr.
        Return value needs to pass through output_mgmt.
        """
        try:
            # Run the command and capture both stdout and stderr
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True  # Ensure the output is in text format
            )
            stdout, stderr = process.communicate()

            # Combine stdout and stderr
            output = f"stdout:\n{stdout}\n\nstderr:\n{stderr}"

            # Pass the output through output_mgmt
            return self.output_mgmt(output)
        except Exception as e:
            # Return the exception text if an error occurs
            return f"Error running the command: {str(e)}"

    def present_result(self, text):
        """
        Print the result to the user. This is an objective completion method.
        """
        print(text)
