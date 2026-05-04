import dotenv
import util.langcache as langcache

from anthropic import AsyncAnthropic
from contextlib import asynccontextmanager
from httpx import AsyncClient
from fastapi import FastAPI, APIRouter, Request, BackgroundTasks
from pydantic import BaseModel
from util.news import fetch_news_api

dotenv.load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # global client that cleans up resources on shutdown
    client = AsyncClient()
    yield {"redis_http_client": client}
    await client.aclose()

router = APIRouter(prefix="/news", tags=["news"], lifespan=lifespan)
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
async def search_news(request: Request, req_data: SearchRequest, bg_tasks: BackgroundTasks):
    redis_http_client = request.app.state.redis_http_client

    max_tokens = 0
    max_articles = 0
    match req_data.detail:
        case "detailed":
            max_tokens = 1500
            max_articles = 12
        case "summary":
            max_tokens = 1000
            max_articles = 9
        case "quick":
            max_tokens = 500
            max_articles = 6
        case _:
            max_tokens, max_articles = 1000, 9
            req_data.detail = "summary"
    
    # check cache
    cache_res = await langcache.check_cache(redis_http_client, req_data.query, req_data.detail)
    if cache_res:
        return {
            "answer": cache_res,
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0
            }
        }

    # fetch news, get summaries
    context = await fetch_news_api(req_data.query, max_articles=max_articles)

    # synthesize with Sonnet
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"Query:{req_data.query}, context:{context}"
        }],
    )
    answer = response.content[0].text
    
    # insert into cache in the background
    bg_tasks.add_task(
        langcache.insert_pair, 
        redis_http_client, 
        req_data.query, 
        answer, 
        req_data.detail
    )

    # return to client
    return {
        "answer": answer,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    }
