from flask import Flask, request, render_template_string, send_file
import requests
import csv
import io
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0"}

DATA_STORE = []

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Research Bot PRO</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; background: #eef; padding: 20px; }
        .box { background: #fff; padding: 20px; border-radius: 12px; max-width: 720px; margin: auto; }
        input, button { padding: 12px; width: 100%; margin: 6px 0; font-size: 16px; }
    </style>
</head>
<body>
<div class="box">
    <h2>Research Bot PRO</h2>
    <form method="post" action="/search">
        <input name="query" placeholder="Pesquisar web ou YouTube" required>
        <button>Pesquisar</button>
    </form>

    {% if results %}
        <h3>Resultados + Resumo</h3>
        <pre>{{ results }}</pre>
    {% endif %}

    <hr>
    <a href="/export">Exportar CSV</a>
</div>
</body>
</html>
"""

def ai_summary(text):
    parts = text.split(".")
    return ". ".join(parts[:3])

def search_web(query):
    url = "https://duckduckgo.com/html/?q=" + query
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    results = []

    for a in soup.select("a.result__a")[:3]:
        results.append({
            "type": "web",
            "title": a.get_text(),
            "link": a["href"]
        })

    return results

def search_youtube(query):
    url = "https://www.youtube.com/results?search_query=" + query.replace(" ", "+")
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    videos = []

    for a in soup.select("a#video-title")[:3]:
        videos.append({
            "type": "youtube",
            "title": a.get("title"),
            "link": "https://youtube.com" + a.get("href")
        })

    return videos

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/search", methods=["POST"])
def search():
    query = request.form["query"]
    results = search_web(query) + search_youtube(query)

    titles = " ".join([r["title"] for r in results if r.get("title")])
    summary = ai_summary(titles)

    DATA_STORE.extend(results)

    display = "Resumo IA:\n" + summary + "\n\nDados:\n" + str(results)
    return render_template_string(HTML, results=display)

@app.route("/export")
def export():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["type", "title", "link"])
    writer.writeheader()
    writer.writerows(DATA_STORE)
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="research_data.csv"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
