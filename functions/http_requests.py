import requests
from bs4 import BeautifulSoup

header = {
    "User-Agent": "MinecraftLauncher"
}

news_minecraft_url_config = "https://www.minecraft.net/content/minecraftnet/language-masters/ru-ru/articles/jcr:content/root/container/image_grid_a.articles.page-1.json"
minecraft_url = "https://www.minecraft.net"


def get_news_article_urls():
    try:
        response = requests.get(news_minecraft_url_config, headers=header)
        response.raise_for_status()
        data = response.json()

        article_urls = []
        for article in data.get("article_grid", []):
            if article.get("primary_category") == "News":
                article_urls.append([article.get("article_url"),
                                     minecraft_url+article.get("default_tile", {}).get("image", {}).get("imageURL")
                                    .replace(" ", "%20")])
        return article_urls

    except requests.RequestException as e:
        print(f"Ошибка при запросе данных: {e}")
        return []


def fetch_article_data(article_url, article_image):
    full_url = minecraft_url + article_url

    try:
        response = requests.get(full_url, headers=header)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        header_element = soup.find('h1', class_='MC_Heading_1')
        content_div = soup.find('div', class_='MC_Link_Style_RichText')

        header_text = header_element.get_text(strip=True) if header_element else None
        content_html = str(content_div) if content_div else None  # Сохраняем HTML-код содержимого
        html_content = f"<h1>{header_text}</h1>" + content_html

        return {
            'url': article_url,
            'image': article_image,
            'header': header_text,
            'content_html': html_content  # Возвращаем HTML-код
        }

    except requests.RequestException as e:
        print(f"Ошибка при запросе статьи {article_url}: {e}")
        return None


def getJsonNews() -> list:
    news_article_urls = get_news_article_urls()
    articles_data = []

    for url in news_article_urls:
        article_data = fetch_article_data(url[0], url[1])
        if article_data:
            articles_data.append(article_data)

    return articles_data


#     --mc-vanilla-fontlist: "MinecraftTen", "Noto Sans", "Helvetica Neue", "Helvetica", "Arial", "sans-serif";

if __name__ == "__main__":
    articles = getJsonNews()
    print("Полученные данные о статьях:")
    for article in articles:
        print(article)
