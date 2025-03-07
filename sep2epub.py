import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import argparse
import time
import re
import matplotlib.pyplot as plt
import io
import base64

latex_regex = re.compile(r'\\\(([\s\S]*?)\\\)|\\\[([\s\S]*?)\\\]')

def get_article(url: str) -> BeautifulSoup:
    response = requests.get(url)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    article_div = soup.find("div", {"id": "article"})

    return article_div

def render_latex_as_image(latex: str) -> str:
    # Create plot with rendered LaTeX
    fig, ax = plt.subplots(figsize=(0.01, 0.01))
    ax.text(0.5, 0.5, f"${latex}$", fontsize=10, ha='center', va='center')
    ax.set_axis_off()

    # Write the plot to buffer as png
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close(fig)
    buffer.seek(0)
    
    # Encode the png and convert to a string to be inserted into XHTML
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode('utf-8')

def replace_latex(content: str) -> str:
    def replacer(match: re.Match) -> str:
        latex = (match.group(1) or match.group(2)).replace("\n", "")
        image_data = render_latex_as_image(latex)
        return f'<img src="{image_data}" alt="{latex}"> '
        
    return latex_regex.sub(replacer, content)

def create_epub(url: str, article: BeautifulSoup, footnotes: BeautifulSoup):
    book = epub.EpubBook()

    book.set_identifier(url)
    book.set_language("en")
    book.add_author("Stanford Encyclopedia of Philosophy")

    # Copyright page
    article_copyright = article.find(id="article-copyright").find("p")
    shilling = '<br><p>EPUB created with <a href="https://github.com/robkellems/sep2epub">sep2epub</a></p>'

    copyright_page = epub.EpubHtml(title="Copyright", file_name="copyright.xhtml", lang="en")
    copyright_page.set_content(str(article_copyright) + shilling)
    book.add_item(copyright_page)

    # Article content
    article_content = article.find(id="article-content").find(id="aueditable")

    title = article_content.find("h1").text + " (Stanford Encyclopedia of Philosophy)"
    book.set_title(title)

    for note in article_content.find_all("a", href=True):
        note["href"] = note["href"].replace("notes.html#", "footnotes.xhtml#")

    article_content_string = str(article_content)
    article_content_string = replace_latex(article_content_string)

    content_page = epub.EpubHtml(title="Content", file_name="content.xhtml", lang="en")
    content_page.set_content(article_content_string)
    book.add_item(content_page)

    # Footnotes
    if footnotes:
        footnotes_content = footnotes.find(id="article-content").find(id="aueditable")

        # Link footnote to annotation
        for note in footnotes_content.find_all("a", href=True):
            note["href"] = note["href"].replace("index.html#", "content.xhtml#")
        
        footnotes_page = epub.EpubHtml(title="Footnotes", file_name="footnotes.xhtml", lang="en")
        footnotes_page.set_content(str(footnotes_content))
        book.add_item(footnotes_page)

        book.spine = ["nav", copyright_page, content_page, footnotes_page]
    else:
        book.spine = ["nav", copyright_page, content_page]

    # Write to file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    filename = title + ".epub"
    epub.write_epub(filename, book)

    print(f"Successfully created epub: {filename}")

def process_url(url: str):
    article = get_article(url)
    if not article:
        print(f"ERROR: failed to fetch {url}, exiting sep2epub...")
        return None

    footnotes = get_article(url + "notes.html")
    if not footnotes:
        print(f"INFO: no footnotes page found for {url}, continuing...")

    create_epub(url, article, footnotes)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="SEP article URL, e.g. https://plato.stanford.edu/entries/kant/ OR .txt file containing one URL per line.")
    args = parser.parse_args()

    if args.input[0:5] == "https":
        process_url(args.input)
    elif args.input[-4:] == ".txt":
        with open(args.input, "r") as f:
            for i, line in enumerate(f):
                if i != 0:
                    # Per SEP's robot.txt
                    time.sleep(5)
                process_url(line.strip())
    else:
        print("ERROR: invalid input, provide either a URL or a .txt file")