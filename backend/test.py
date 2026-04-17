import asyncio
import httpx
import dotenv

NEWS_API_KEY = dotenv.get_key(".env", "NEWS_API_KEY_2")

async def test_domains():
	domains_to_test = ["usatoday.com", "newsweek.com", "fortune.com"]

	async with httpx.AsyncClient() as client:
		for domain in domains_to_test:
			resp = await client.get("https://newsapi.org/v2/everything", params={
				"apiKey": NEWS_API_KEY,
				"q": "trump iran",
				"domains": domain,
				"pageSize": 1
			})
			data = resp.json()
			print(f"{domain:35} → {data.get('totalResults', 0)} results, status: {data.get('status')}, error: {data.get('message', 'none')}")

asyncio.run(test_domains())