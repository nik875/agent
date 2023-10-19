# Axon Terminal

An intelligent shell made for scientific and academic researchers. Operates as a plugin on top of [oh-my-zsh](https://ohmyz.sh/#install). The only dependency is Python 3.8+.

To install, first install/configure zsh and oh-my-zsh. To install zsh, run `sudo apt install zsh`, and then `chsh -s $(which zsh)` to set as default shell (change install command depending on your system's package manager). Don't worry about configuring anything when it asks, just leave it on the minimal .zshrc.

Once zsh is installed, install oh-my-zsh with the following command: `sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`. The website has other install methods, including through wget instead of curl.

Now clone this repository into the plugins directory: `git clone https://github.com/nik875/axon-terminal ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/axon-terminal`.

Then go to the plugin directory: `cd ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/axon-terminal` and create a `creds.py` file with the following line:

```python
API_KEY = 'YOUR_INTELLISHELL_API_KEY_HERE'
```

Once this is done, edit the `~/.zshrc` configuration file, find the line that says `plugins=`, and add "intellishell" to the list. The list is whitespace separated. At a bare minimum, your line should look like this (if you have no other plugins)

```zsh
plugins=(intellishell)
```

Now you're ready to start using IntelliShell! Simply run `omz reload` in your shell to reload all shell configuration. Then relax and have your first conversation with IntelliShell!

---

## Common Problems

The plugin assumes that `python3` is the correct alias for Python 3.8. This may not be the case on every system, especially if you had to manually install an up-to-date Python version. To handle these cases, add the line `export PYTHON_PATH=path/to/your/installation` to your `.zshrc`.
