# Axon Terminal

An intelligent shell made for scientific and academic researchers. Operates as a plugin on top of [oh-my-zsh](https://ohmyz.sh/#install). The only dependency is Python 3.8+.

To install, first install/configure zsh and oh-my-zsh. To install zsh, run `sudo apt install zsh` (or whatever's right for your Linux distro's package manager), and then `chsh -s $(which zsh)` to set as default shell (change install command depending on your system's package manager). Don't worry about configuring anything when it asks, just leave it on the minimal .zshrc.

Once zsh is installed, install oh-my-zsh with the following command. The website also has other install methods, including through wget instead of curl.

```zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

Now clone this repository into the plugins directory:

```zsh
git clone --depth 1 https://github.com/nik875/axon-terminal ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/axon-terminal
```

Once this is done, simply run `omz plugin enable axon-terminal` to finish installation. On the first run, you will be asked for an API key. Currently this project is in alpha release, so contact me for a key if you want to give Axon a try.

---

## Common Problems

The plugin assumes that `python3` is the correct alias for Python 3.8. This may not be the case on every system, especially if you had to manually install an up-to-date Python version. To handle these cases, add the line `export PYTHON_PATH=path/to/your/installation` to your `.zshrc`.

If you accidentally entered the wrong API key, or need to update your key for whatever reason, run this command:

```zsh
rm ~/.oh-my-zsh/custom/plugins/axon-terminal/creds.py
```

Then do an `omz reload` and the prompt will reappear.
