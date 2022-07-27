from PIL import Image
import requests # request img from web
import shutil # save img locally
import json
import re
import base64
from io import BytesIO  
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def add_margin(pil_img, right, left):
    width, height = pil_img.size
    new_width = width + right + left
    result = Image.new("RGBA", (new_width, height),(255,0,0,0))
    result.paste(pil_img, (left, 0))
    return result

def to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str

def downlaod(url,file_name):
    res = requests.get(url, stream = True)
    if res.status_code == 200:
        with open(file_name,'wb') as f:
            shutil.copyfileobj(res.raw, f)
        print('Image sucessfully Downloaded: ',file_name)
    else:
        print('Image Couldn\'t be retrieved')

def upload(img_str):
    secret_file = open('secrets.json') 
    secret_data = json.load(secret_file) 
    image_host_key = secret_data["image_host_key"]
    image_host_url = "https://freeimage.host/api/1/upload"
    secret_file.close() 

    data = {
        "key":image_host_key,
        "source":img_str,
        "action":"upload",
        "format":"json"
    }
    with requests.Session() as s:
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        s.mount('http://', adapter)
        s.mount('https://', adapter)
        r = s.post(image_host_url,data=data)
        return r.json()["image"]["url"]

def get_url(url):
    id = re.search(r"(https://books.google.com/books/content\?id=)(\w+)(&.*)",url).group(2)
    file_name = f"covers/{id}.png"
    downlaod(url,file_name)
    thumbnail= Image.open(file_name)
    height = thumbnail.size[1]
    width = thumbnail.size[0]

    margin = int((height-width)/2)
    icon_image = add_margin(thumbnail,margin,margin)
    icon_str = to_base64(icon_image) 
    icon_url = upload(icon_str)

    image_width = int((height*7)/5)
    margin = int((image_width-width)/1.9)
    cover_image = add_margin(thumbnail,margin,margin) 
    cover_str = to_base64(cover_image)
    cover_url = upload(cover_str)
    
    urls = {
        "cover":cover_url,
        "icon":icon_url
    }
    return urls
