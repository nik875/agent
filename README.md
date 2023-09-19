# smartshell

To use, it's necessary to create a creds.py file inside of the `agent` directory with the following content:


```python
OPENAI_API_KEY = 'your-key-here'
GOOGLE_API_KEY = 'your-key-here'
GOOGLE_CUSTOM_SEARCH_ENGINE_ID = 'your-engine-id-here'
WORKING_DIRECTORY = 'your-working-directory-path'
```

---

To install, create a virtual Python environment and install these packages:

- openai
- tiktoken
- scikit-learn
- guidance

Then activate the environment and run `python sh.py` to enter a smart shell environment.
