Research Bot PRO – AI Summary + Mobile Install (PWA)

Web App com resumo inteligente e instalável no telemóvel

from flask import Flask, request, render_template_string, send_file, redirect, url_for, session import requests, csv, io from bs4 import BeautifulSoup

app = Flask(name) app.secret_key = "researchbot_secret" HEADERS = {"User-Agent": "Mozilla/5.0"}

ADMIN_USER = "admin" ADMIN_PASS = "admin123" DATA_STORE = []

HTML = """

<!DOCTYPE html><html>
<head>
<title>Research Bot PRO</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="manifest" href="/manifest.json">
<style>
body{font-family:Arial;background:#eef;padding:20px}
.box{background:#fff;padding:20px;border-radius:12px;max-width:720px;margin:auto}
input,button{padding:12px;width:100%;margin:6px 0;font-size:16px}
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
<pre>{{results}}</pre>
{% endif %}
<hr>
<a href="/export">Exportar CSV</a>
</div>
</body>
</html>
"""MANIFEST = { "name": "Research Bot PRO", "short_name": "ResearchBot", "start_url": "/", "display": "standalone", "background_color": "#eef", "theme_color": "#ffffff", "icons": [] }

def ai_summary(text): # resumo simples (legal, sem scraping privado) sentences = text.split('.') return '. '.join(sentences[:3])

def search_web(query): url = f"https://duckduckgo.com/html/?q={query}" r = requests.get(url, headers=HEADERS) soup = BeautifulSoup(r.text, 'html.parser') results = [] for a in soup.select('a.result__a')[:3]: results.append({"type":"web","title":a.get_text(),"link":a['href']}) return results

def search_youtube(query): url = f"https://www.youtube.com/results?search_query={query.replace(' ','+')}" r = requests.get(url, headers=HEADERS) soup = BeautifulSoup(r.text, 'html.parser') videos = [] for a in soup.select('a#video-title')[:3]: videos.append({"type":"youtube","title":a.get('title'),"link":"https://youtube.com"+a.get('href')}) return videos

@app.route('/') def home(): return render_template_string(HTML)

@app.route('/search', methods=['POST']) def search(): query = request.form['query'] results = search_web(query) + search_youtube(query)

summary_text = ' '.join([r['title'] for r in results])
summary = ai_summary(summary_text)

DATA_STORE.extend(results)
display = f"Resumo IA:\n{summary}\n\nDados:\n{results}"
return render_template_string(HTML, results=display)

@app.route('/export') def export(): output = io.StringIO() writer = csv.DictWriter(output, fieldnames=["type","title","link"]) writer.writeheader() writer.writerows(DATA_STORE) output.seek(0) return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='research_data.csv')

@app.route('/manifest.json') def manifest(): return MANIFEST

if name == 'main': app.run(host="0.0.0.0", port=10000)
