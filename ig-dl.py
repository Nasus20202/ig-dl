from pathlib import Path
import requests
import sys
import shutil
import string

class Photo:
    def __init__(self, url, filename):
        self.url = url
        self.filename = filename

def repair_link(link):
    return link.replace("&amp;", "&").replace("\/", "/").replace("\\", "/").replace("//u0026", "&")


def get_photos(link):
    photos = []
    cookies = {
        'ds_user_id': '53844256922',
        'sessionid': '53844256922%3Al4oOezFZYRYDUz%3A19',
    }
    headers = {
        'x-ig-app-id': '936619743392459'
    }

    response = requests.get(link, cookies=cookies)
    content = response.text
    media_id = None
    for i in content.split('{'):
        for j in i.split('}'):
            if "media_id" in j:
                media_id = j.split('"')[3]
                break
        if media_id is not None:
            break


    response = requests.get(f'https://i.instagram.com/api/v1/media/{media_id}/info/', cookies=cookies, headers=headers)
    data = response.json()
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    name = f'{data["items"][0]["user"]["full_name"]} - {data["items"][0]["caption"]["text"]}'
    if "carousel_media" in data["items"][0]:
        photo_count = int(data["items"][0]["carousel_media_count"])
        for i in range(photo_count):
            photos.append(Photo(data["items"][0]["carousel_media"][i]["image_versions2"]["candidates"][0]["url"], "".join(x for x in f"{name} ({i+1})" if x in valid_chars) + ".jpg"))
    else:
        photos.append(Photo(data["items"][0]["image_versions2"]["candidates"][0]["url"], "".join(x for x in f"{name}" if x in valid_chars) + ".jpg"))
    return photos

def download_photo(url, folder, filename):
    response = requests.get(repair_link(url), stream=True)
    Path(folder).mkdir(parents=True, exist_ok=True)
    with open(f"./{folder}/{photo.filename}", 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

links = sys.argv[1:]
for link in links:
    for photo in get_photos(link):
        download_photo(photo.url, "ig-photos", photo.filename)