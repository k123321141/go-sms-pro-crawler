import requests
import base64
import re
import io
import os
from tqdm import tqdm
from PIL import Image
from selenium import webdriver
import logging
from selenium.webdriver.chrome.options import Options

opts = Options()

FORMAT = 'png'
PROXY = "http://localhost:8118"
logger = logging.getLogger(__name__)

opts.add_argument("--incognito")
opts.add_argument(f'--proxy-server={PROXY}')

browser = webdriver.Chrome(chrome_options=opts)
webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
    "httpProxy": PROXY,
    "ftpProxy": PROXY,
    "sslProxy": PROXY,
    "proxyType": "MANUAL",

}


def get_img_urls(browser, url):
    browser.get(url)
    imgs = browser.find_elements_by_css_selector("img")
    ret = []
    for img in imgs:
        image_src = img.get_attribute('src')
        ret.append(image_src)
    return ret


def save_image_from_url(img_src, path):
    global logger, FORMAT
    image_content = requests.get(img_src).content
    try:
        image_content = requests.get(img_src).content
    except requests.exceptions.InvalidSchema:
        # image is probably base64 encoded
        image_data = re.sub('^data:image/.+;base64,', '', img_src)
        image_content = base64.b64decode(image_data)
    except Exception as e:
        logger.info("could not read", e, img_src)
        return
    # size = (720, 720)
    image_file = io.BytesIO(image_content)
    image = Image.open(image_file).convert('RGB')
    with open(path, 'wb') as fout:
        image.save(fout, FORMAT)
        # logger.info(f'Save image to: {path}')


if __name__ == "__main__":
    # urls = ['https://gs.3g.cn/D/de1efd/w']
    base = int('ce1efd', base=16)
    with tqdm() as pbar:
        while True:
            url = f'https://gs.3g.cn/D/{hex(base)[2:]}/w'
            try:
                img_urls = get_img_urls(browser, url)
                for i, img_url in enumerate(img_urls):
                    replaced_url = url.replace("/", "_")
                    path = os.path.join('./imgs', f'{replaced_url}_{i}.{FORMAT}')  # noqa
                    save_image_from_url(img_url, path)
            except Exception:
                logger.info(f'Skip url: {url}')
            pbar.update(1)
            base += 1
