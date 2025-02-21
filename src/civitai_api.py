import httpx
import asyncio


async def _fetch_one(client:httpx.AsyncClient, url:str):
    r = await client.get(url)
    return r

async def _fetch_all(urllist:list, **kwargs):
    async with httpx.AsyncClient() as session:
        tasks = (asyncio.create_task(_fetch_one(session, url)) for url in urllist)
        responses = await asyncio.gather(*tasks)
        return responses

def fetch_all(urllist:list, **kwargs):
    if isinstance(urllist,str):
        urllist = [urllist]
    return asyncio.run(_fetch_all(urllist, **kwargs))

def model_lookup(model_id):
    url = f"https://civitai.com/api/v1/models/{model_id}"
    r = httpx.get(url)
    return r.json()

def model_version_lookup(model_version_id):
    url = f"https://civitai.com/api/v1/model-versions/{model_version_id}"
    r = httpx.get(url)
    return r.json()


def bulk_resource_lookup(model_version_ids:list):
    urllist = []
    
    for mvid in model_version_ids:
        urllist.append(f"https://civitai.com/api/v1/model-versions/{mvid}")

    responses = fetch_all(urllist)

    json_responses = [r.json() for r in responses]

    return json_responses

