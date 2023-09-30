# smartshell

To use, it's necessary to create a creds.py file inside of the `intellishell/agent` directory with the following content:


```python
OPENAI_API_KEY = 'your-key-here'
```

---

To install, clone this repository into your oh-my-zsh plugins folder. Then create a virtual Python environment in the cloned repository called `env` and install these packages:

- openai
- tiktoken
- scikit-learn
- guidance
- redis
- redis-om

Then add 'intellishell' to your list of oh-my-zsh plugins. Obviously it's necessary to install oh-my-zsh and zsh before using this shell plugin.
