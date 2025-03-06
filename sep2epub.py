import requests
from bs4 import BeautifulSoup
from ebooklib import epub

def get_article(url: str) -> BeautifulSoup:
    response = requests.get(url)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    article_div = soup.find("div", {"id": "article"})

    return article_div

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

    # Footnotes
    if footnotes:
        footnotes_content = footnotes.find(id="article-content").find(id="aueditable")

        # Link footnote to annotation
        for note in footnotes_content.find_all("a", href=True):
            note["href"] = note["href"].replace("index.html#", "content.xhtml#")
        
        footnotes_page = epub.EpubHtml(title="Footnotes", file_name="footnotes.xhtml", lang="en")
        footnotes_page.set_content(str(footnotes_content))
        book.add_item(footnotes_page)

        # Link annotation to footnote
        for note in article_content.find_all("a", href=True):
            note["href"] = note["href"].replace("notes.html#", "footnotes.xhtml#")

        content_page = epub.EpubHtml(title="Content", file_name="content.xhtml", lang="en")
        content_page.set_content(str(article_content))
        book.add_item(content_page)

        book.spine = ["nav", copyright_page, content_page, footnotes_page]
    else:
        content_page = epub.EpubHtml(title="Content", file_name="content.xhtml", lang="en")
        content_page.set_content(str(article_content))
        book.add_item(content_page)

        book.spine = ["nav", copyright_page, content_page]

    # Write to file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    epub.write_epub(f"{title}.epub", book)

if __name__ == "__main__":
    url = "https://plato.stanford.edu/entries/kant/"

    article = get_article(url)
    if not article:
        print(f"ERROR: failed to fetch {url}, exiting sep2epub...")
        exit()

    footnotes = get_article(url + "notes.html")
    if not footnotes:
        print(f"INFO: no footnotes page found for {url}, continuing...")

    create_epub(url, article, footnotes)
