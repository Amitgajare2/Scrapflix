from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to scrape data based on the actress name
def scrape_data(actress_name):
    url = f"https://www.superporn.com/search?q={actress_name}/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    video_items = soup.select(".listado-videos .thumb-video a")

    data_list = []

    for item in video_items:
        # title = item.get("title")
        href = item.get("href")
        duration_tag = item.find("span", class_="duracion")
        img_tag = item.find("img")
        # preview = item.get("data-trailer_url")
        img_src = img_tag.get("data-src") or img_tag.get("src") if img_tag else None
        title =  img_tag.get("alt") if img_tag else "No title found"
        duration = duration_tag.text.strip() if duration_tag else "N/A"


        if img_src and img_src.startswith("//"):
            img_src = "https:" + img_src

        if title and href and img_src and duration:
            data_list.append({
                "title": title,
                "mainurl": href,
                "img": img_src,
                "duration": duration,
            })

    return data_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    actress_name = request.args.get('actress_name', '').strip()
    page = int(request.args.get('page', 1))

    if not actress_name:
        return render_template('index.html', error="Please enter an actress name.")

    scraped_data = scrape_data(actress_name)
    posts_per_page = 10
    start = (page - 1) * posts_per_page
    end = start + posts_per_page

    paginated_data = scraped_data[start:end]
    total_pages = (len(scraped_data) + posts_per_page - 1) // posts_per_page

    return render_template('results.html', 
                           data=paginated_data, 
                           actress_name=actress_name, 
                           page=page, 
                           total_pages=total_pages)

if __name__ == '__main__':
    app.run(debug=True)
