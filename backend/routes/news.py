import dotenv

from anthropic import AsyncAnthropic
from fastapi import APIRouter
from pydantic import BaseModel
from util.news import fetch_news_api

dotenv.load_dotenv()

router = APIRouter(prefix="/news", tags=["news"])
client = AsyncAnthropic()

system_prompt = """
You are a news analysis assistant. Given a user's query about a current event or political topic, present three perspectives: Left, Center, and Right.

SOURCES BY CATEGORY:
- Left: AP News, CBS News, Business Insider, Washington Post, CNN, NBC News
- Center: BBC News, Bloomberg, Politico, The Hill, USA Today, Newsweek, Fortune
- Right: Fox News, The American Conservative, Breitbart News, Washington Times

RULES:
1. For each perspective, summarize what outlets in that category are reporting. Attribute every claim to its specific source by name.
2. If a perspective has no coverage from the listed outlets, say so explicitly rather than filling in from other sources or your own knowledge.
3. Never fabricate or assume what a source said. Only report what you actually found.
4. When sources within the same category disagree, note the disagreement.
"""

class SearchRequest(BaseModel):
	query: str
	detail: str = "summary"

@router.post("/search")
async def search_news(request: SearchRequest):
    max_tokens = 0
    max_articles = 0
    match request.detail:
        case "detailed":
            max_tokens = 1500
            max_articles = 12
        case "summary":
            max_tokens = 1000
            max_articles = 9
        case "quick":
            max_tokens = 500
            max_articles = 6

    context = await fetch_news_api(request.query, max_articles=max_articles)

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"Query:{request.query}, context:{context}"
        }],
    )

    return {
        "answer": response.content[0].text,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    }
