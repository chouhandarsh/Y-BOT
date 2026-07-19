from langchain_community.document_loaders import YoutubeLoader
from bs4 import BeautifulSoup
import requests
class load:
    @staticmethod
    def videoLoader(url):
        try:
            loader  =  YoutubeLoader.from_youtube_url(url,add_video_info=False,language=['hi','en'])
            data=loader.load()
        except Exception:
            raise ValueError ("Could not fetch the transcript This video might not have the caption")
        if not data[0] or not data[0].page_content.strip():
            raise ValueError("This video has no usable transcript")
        return data[0].page_content
    @staticmethod
    def titleLoader(url):
        try:
            header={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win 64 ; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'}
            webpage=requests.get(url,headers=header)
            soup=BeautifulSoup(webpage.text,features="lxml")
            titile_format = soup.find("yt-formatted-string",{"class": "style-scope ytd-watch-metadata"})
            return soup.title.get_text(strip=True)
        except:
            raise ValueError("Untitled Video")
    @staticmethod
    def thumbnailLoader(url):
        try:
            header={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win 64 ; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'}
            webpage=requests.get(url,headers=header)
            soup=BeautifulSoup(webpage.text,features="lxml")
            meta_tag = soup.find("meta", property="og:image")
            if meta_tag:
                return meta_tag["content"]
            else:
                # Fallback extraction method
                import re
                match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
                if match:
                    return f"http://img.youtube.com/vi/{match.group(1)}/hqdefault.jpg"
                raise ValueError("Thumbnail meta tag not found")
        except:
            raise ValueError("Thumbnail not found")
