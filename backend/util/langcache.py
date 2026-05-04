import httpx
import os
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

REDIS_API_URL="https://aws-us-east-1.langcache.redis.io"
CACHE_ID = os.getenv(".env", "CACHE_ID")
LANGCACHE_API_KEY = os.getenv(".env", "LANGCACHE_API_KEY")

headers = {
	"accept": "application/json",
	"Authorization": f"Bearer {LANGCACHE_API_KEY}",
}

async def check_cache(client: httpx.AsyncClient, key: str, detail: str):
	results = await search_key(key, detail)
	if not results:
		return None # miss
	
	# hit
	return max(results, key=lambda r: r.get("similarity", 0))


async def search_key(client: httpx.AsyncClient, key: str, detail: str):
	# validate key
	if len(key) > 1024:
		raise ValueError("Key must be less than 1024 chars")
	
	# make request
	try: 
		response = await client.post(
			f"{REDIS_API_URL}/v1/caches/{CACHE_ID}/entries/search",
			headers=headers,
			json={
				"prompt": key,
				"similarityThreshold": 0.9,
				"attributes": {
					"detail": detail
				},
				"searchStrategies": ["exact", "semantic"]
			},
			timeout=10.0
		)
		return response.json()
	# returns [] on miss
	except httpx.HTTPError as e:
		print(f"HTTP Exception for {e.request.url} - {e}")
		return []
		

async def insert_pair(client: httpx.AsyncClient, key: str, value: str, detail: str):
	# validate key
	if len(key) > 1024:
		raise ValueError("Key must be less than 1024 chars")
	
	# make request
	try:
		response = await client.post(
			f"{REDIS_API_URL}/v1/caches/{CACHE_ID}/entries",
			headers=headers,
			json={
				"prompt": key,
				"response": value,
				"attributes": {
					"detail": detail
				}
			},
			timeout=10.0
		)
		return response.json()
	except httpx.HTTPError as e:
		print(f"Failed to insert ({key}, {value}): {e}")
		return None

async def delete_pair(client: httpx.AsyncClient, id: str):
	# make request
	try:
		response = await client.delete(
			f"{REDIS_API_URL}/v1/caches/{CACHE_ID}/entries/{id}",
			headers=headers,
			timeout=10.0
		)
	except httpx.HTTPError as e:
		print(f"Failed to delete {id}: {e}")
		return None