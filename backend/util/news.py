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

haiku_system_prompt="""
You are a summarizing assistant. The user will provide you with an article to summarize. Your job is to highlight key takeaways, interesting findings, any data used, and statistics reported in the article. Remember, your job is simply to report to the user what was in the article in a concise manner. They will use the information to write a summary themselves, so do not take it upon yourself to write anything extra about the article.
"""

async def search_article_url(article: dict, client: httpx.AsyncClient) -> dict:
	if not article.get("url"):
		return article

	try:
		resp = await client.get(article["url"], follow_redirects=True, timeout=10)
		doc = Document(resp.text)
		text = BeautifulSoup(doc.summary(), "html.parser").get_text("\n", strip=True)

		haiku_res = await anth_client.messages.create(
			model="claude-haiku-4-5-20251001",
			max_tokens=500,
			system=haiku_system_prompt,
			messages=[{"role": "user", "content": text}]
		)
		article["full_content"] = haiku_res.content[0].text
	
	except Exception as e:
		print(f"[enrichment] Failed for {article.get('url', '?')}: {e}")
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

async def fetch_category(client: httpx.AsyncClient, query: str, domains: str, page_size: int, label: str) -> tuple[str, list[dict]]:
	try:
		resp = await client.get(
			"https://newsapi.org/v2/everything",
			params={
				"apiKey": NEWS_API_KEY,
				"q": query,
				"domains": domains,	
				"sortBy": "relevancy",
				"pageSize": page_size,
			},
			timeout=10.0,
		)
		resp.raise_for_status()
		data = resp.json()

		if data.get("status") != "ok":
			print(f"[{label}] API error: {data.get('message', 'unknown')}")
			return label, []

		return label, data.get("articles", [])

	except httpx.TimeoutException:
		print(f"[{label}] Request timed out")
		return label, []
	except httpx.HTTPStatusError as e:
		print(f"[{label}] HTTP {e.response.status_code}: {e.response.text[:200]}")
		return label, []
	except Exception as e:
		print(f"[{label}] Unexpected error: {e}")
		return label, []

async def fetch_news_api(query: str, max_articles: int) -> str:
	per_category = max_articles // 3

	categories = {
		"LEFT": "apnews.com,cbsnews.com,businessinsider.com,washingtonpost.com,us.cnn.com,nbcnews.com",
		"CENTER": "bbc.co.uk,bloomberg.com,politico.com,thehill.com,usatoday.com,newsweek.com,fortune.com",
		"RIGHT": "foxnews.com,theamericanconservative.com,breitbart.com,washingtontimes.com"
	}

	async with httpx.AsyncClient() as client:
		results = await asyncio.gather(*[
			fetch_category(client, query, domains, per_category, label)
			for label, domains in categories.items()
		])

		all_articles = []
		for label, items in results:
			for article in items:
				article["_category"] = label
				all_articles.append(article)

		enriched = await asyncio.gather(
			*[search_article_url(a, client) for a in all_articles],
			return_exceptions=True,
		)
		enriched = [a for a in enriched if not isinstance(a, Exception)]

	return format_articles_by_category(enriched)