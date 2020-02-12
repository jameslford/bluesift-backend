import io
import requests
from PIL import Image

def url_to_pimage(url) -> Image.Image:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'}
    respone = requests.get(url, headers=headers)
    if not respone.status_code == 200:
        print('bad request')
        return None
    try:
        image: Image = Image.open(io.BytesIO(respone.content))
        return image
    except (OSError, ValueError):
        return None