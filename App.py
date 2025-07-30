from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def search_lex(query):
    search_url = f"https://lex.bg/guide/search?q={query}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for a in soup.select("div.article_list_title a")[:3]:
        title = a.text.strip()
        link = "https://lex.bg" + a["href"]
        results.append((title, link))
    return results

def get_article_text(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    content = soup.find("div", class_="newsbody")
    if content:
        text = content.get_text(strip=True)
        return text[:600] + "..." if len(text) > 600 else text
    return "Няма съдържание."

@app.route("/api/legal-assistant", methods=["POST"])
def legal_assistant():
    data = request.json
    question = data.get("question", "")
    results = search_lex(question)
    articles = [{
        "title": title,
        "link": link,
        "snippet": get_article_text(link)
    } for title, link in results]

    return jsonify({
        "question": question,
        "results": articles
    })

if __name__ == "__main__":
    app.run(debug=True)
