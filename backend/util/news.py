import httpx
import dotenv
import asyncio

from dotenv import load_dotenv, get_key
from anthropic import AsyncAnthropic
from bs4 import BeautifulSoup
from readability import Document

load_dotenv()
anth_client = AsyncAnthropic()
NEWS_API_KEY = get_key(".env", "NEWS_API_KEY_2")

system="""
You are a summarizing assistant. The user will provide you with an article to summarize. Your job is to highlight key takeaways, interesting findings, any data used, and statistics reported in the article. Remember, your job is simply to report to the user what was in the article in a concise manner. They will use the information to write a summary themselves, so do not take it upon yourself to write anything extra about the article.
"""

async def search_article_url(article: dict) -> dict:
	if not article.get("url"):
		return article

	try:
		async with httpx.AsyncClient() as client:
			resp = await client.get(article["url"], follow_redirects=True, timeout=10)
		doc = Document(resp.text)
		text = BeautifulSoup(doc.summary(), "html.parser").get_text("\n", strip=True)
		print(text)
		haiku_res = await anth_client.messages.create(
			model="claude-haiku-4-5-20251001",
			max_tokens=500,
			system=system,
			messages=[{"role": "user", "content": text}]
		)
		article["full_content"] = haiku_res.content[0].text
	except Exception:
		article["full_content"] = article.get("description", "")

	return article
		

def format_articles_by_category(articles: list[dict]) -> str:
	categories = {"LEFT": [], "CENTER": [], "RIGHT": []}

	for article in articles:
		cat = article.get("_category", "OTHER")
		if cat not in categories:
			continue

		source = article.get("source", {}).get("name", "")
		categories[cat].append(
			f"Source: {source}\n"
			f"Title: {article.get('title', '')}\n"
			f"URL: {article.get('url', '')}\n"
			f"Description: {article.get('description', '')}\n"
			f"Content: {article.get('full_content', article.get('description', ''))}"
		)

	parts = []
	for label, items in categories.items():
		parts.append(f"=== {label} ===")
		if items:
			parts.append("\n---\n".join(items))
		else:
			parts.append("No coverage found from these outlets.")

	return "\n\n".join(parts)

async def fetch_news_api(query: str, max_articles: int) -> str:
	per_category = max_articles // 3

	left_sources = "apnews.com,cbsnews.com,businessinsider.com,washingtonpost.com,us.cnn.com,nbcnews.com"
	center_sources = "bbc.co.uk,bloomberg.com,politico.com,thehill.com,usatoday.com,newsweek.com,fortune.com"
	right_sources = "foxnews.com,theamericanconservative.com,breitbart.com,washingtontimes.com"

	async with httpx.AsyncClient() as client:
		left, center, right = await asyncio.gather(
			client.get("https://newsapi.org/v2/everything", params={
				"apiKey": NEWS_API_KEY,
				"q": query,
				"domains": left_sources,
				"sortBy": "relevancy",
				"pageSize": per_category
			}),
			client.get("https://newsapi.org/v2/everything", params={
				"apiKey": NEWS_API_KEY,
				"q": query,
				"domains": center_sources,
				"sortBy": "relevancy",
				"pageSize": per_category
			}),
			client.get("https://newsapi.org/v2/everything", params={
				"apiKey": NEWS_API_KEY,
				"q": query,
				"domains": right_sources,
				"sortBy": "relevancy",
				"pageSize": per_category
			}),
		)
	
	print("LEFT:", left.json().get("status"), "total:", left.json().get("totalResults"), "error:", left.json().get("message", "none"))
	print("CENTER:", center.json().get("status"), "total:", center.json().get("totalResults"), "error:", center.json().get("message", "none"))
	print("RIGHT:", right.json().get("status"), "total:", right.json().get("totalResults"), "error:", right.json().get("message", "none"))

	articles = {
		"LEFT": left.json().get("articles", []),
		"CENTER": center.json().get("articles", []),
		"RIGHT": right.json().get("articles", []),
	}

	all_articles = []
	for cat, items in articles.items():
		for article in items:
			article["_category"] = cat
			all_articles.append(article)

	enriched = await asyncio.gather(*[search_article_url(a) for a in all_articles])
	return format_articles_by_category(enriched)