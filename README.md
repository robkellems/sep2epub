# sep2epub
Create EPUB files from [Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/) entries.
## Installation
Clone the repo:
```
git clone https://github.com/robkellems/sep2epub.git
cd sep2epub
```
Install Python dependencies:
```
pip install -r requirements.txt
```
And you should be good to go!
## Usage
To download a single entry, provide a single URL, e.g.:
```
python3 sep2epub.py https://plato.stanford.edu/entries/wittgenstein/
```
To download a list of entries, create a text file with one URL per line, and then provide the path to it, e.g.:
**articles.txt**
```
https://plato.stanford.edu/entries/anscombe/
https://plato.stanford.edu/entries/ockham/
https://plato.stanford.edu/entries/spinoza/
```
```
python3 sep2epub.py articles.txt
```
## Notes
- Tested with Python 3.12.3.
- If you're trying to download entries with a ton of LaTeX ([for example](https://plato.stanford.edu/entries/logic-inductive/)), you'll likely need to do a lot of tinkering. This code relies on matplotlib's math rendering; if you want to use your own TeX distribution, you can add `matplotlib.rcParams["text.usetex"] = True`. Even with this, a lot of the pages I've encountered use some non-standard commands and/or have typos that you'll have to deal with on a case-by-case basis.
- Intended for personal use only. Refer to SEP policy regarding distribution of their content.