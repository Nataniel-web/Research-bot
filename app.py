from flask import Flask, request, render_template_string, send_file
import requests, csv, io
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = "researchbot_secret"

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
        pre { white-space: pre-wrap; }
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
        <a href="/export">Exportar CSV</a>
    {% endif %}
</div>
</body>
</html>
"""

# ---------- FUNÇÕES ----------

def ai_summary(text):
    parts = text.split(".")
    return ". ".join(parts[:3]) + "."

def search_web(query):
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_redirect": 1,
        "no_html": 1
    }

    r = requests.get(url, params=params, headers=HEADERS)
    data = r.json()

    results = []
    for item in data.get("RelatedTopics", [])[:5]:
        if isinstance(item, dict) and item.get("Text"):
            results.append({
                "type": "web",
                "title": item["Text"],
                "link": item.get("FirstURL")
            })

    return results

def search_youtube(query):
    feed = f"https://www.youtube.com/feeds/videos.xml?search_query={query}"
    r = requests.get(feed, headers=HEADERS)
    soup = BeautifulSoup(r.text, "xml")

    videos = []
    for entry in soup.find_all("entry")[:5]:
        videos.append({
            "type": "youtube",
            "title": entry.title.text,
            "link": entry.link["href"]
        })

    return videos

# ---------- ROTAS ----------

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")

    web_results = search_web(query)
    yt_results = search_youtube(query)

    results = web_results + yt_results

    titles = ". ".join([r["title"] for r in results])
    summary = ai_summary(titles)

    DATA_STORE.extend(results)

    display = f"Resumo IA:\n{summary}\n\nDados:\n{results}"
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
