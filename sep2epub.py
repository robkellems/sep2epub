import requests
from bs4 import BeautifulSoup
from ebooklib import epub

def get_article(url: str) -> BeautifulSoup:
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch page {url}, returned {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    article_div = soup.find("div", {"id": "article"})

    if not article_div:
        raise Exception(f"Could not find article content in page {url}")

    return article_div

def create_epub(url: str, article: BeautifulSoup):
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

    content_page = epub.EpubHtml(title="Content", file_name="content.xhtml", lang="en")
    content_page.set_content(str(article_content))
    book.add_item(content_page)

    # Write to file
    book.spine = ["nav", copyright_page, content_page]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    epub.write_epub(f"{title}.epub", book)

if __name__ == "__main__":
    url = "https://plato.stanford.edu/entries/kant/"
    article = get_article(url)
    create_epub(url, article)
