import re
from bs4 import BeautifulSoup, Comment
import requests
import chardet
import random
from fake_useragent import UserAgent, FakeUserAgentError 
import random

authorset = {'责任编辑', '阿菜'}

try:
    ua = UserAgent()
except FakeUserAgentError:
    pass


first_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Host": "www.wzrb.com.cn",
        "Proxy-Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": ua.random,
        }


# 随机一个User-Agent
def get_headers():  
    first_headers['User-Agent'] = ua.random 
    print(first_headers['User-Agent'])
    return first_headers

# 返回response
def getcontentfromweb(src):
    headers = get_headers()
    obj = requests.get(src, headers=headers, timeout=8)
    
    # 自动检测编码，更换编码，防止乱码
    try:
        result = chardet.detect(obj.content)
        obj.encoding = str(result['encoding'])
    except Exception:
        pass
		
    return obj.text


# 去掉html标签
def getTitle(html):
    titleFilter = r'<title>([\s\S]*?)</title>'
    h1Filter = r'<h1.*?>(.*?)</h1>'
    # clearFilter = r"<.*?>"

    title = ""
    match = re.findall(titleFilter, html)
    if match:
        try:
            title = match[0]
        except Exception:
            title = ' '

    match = re.findall(h1Filter, html)
    if match:
        try:
            h1 = match[0]
            if h1 and title.startswith(h1):
                title = h1
        except Exception:
            h1 = ' '

    return title


# 日期
def getDate(html):
    text = re.sub('(?is)<.*?>', '', html)
    reg = r'((\d{4}|\d{2})(\-|\/)\d{1,2}\3\d{1,2})(\s?\d{2}:\d{2})?|(\d{4}年\d{1,2}月\d{1,2}日)(\s?\d{2}:\d{2})?'
    match = re.findall(reg, text)
    dateStr = ''
    if match:
        try:
            date = match[0]
            if type(date) is tuple:
                dateStr = date[0]
        except Exception:
            date = ''
            dateStr = ''
    return dateStr


# 更换reg获得浏览数
def getVisit(html):
    text = re.sub('(?is)<.*?>', '', html)
    reg = r'浏览：(\d*)'
    match = re.findall(reg, text)
    visitCount = 0
    if match:
        try:
            visitCount = int(match[0])
        except Exception:
            visitCount = 0
    """
    reg2 = r'阅读：(\d*)'
    match2 = re.findall(reg2, text)
    if match2 and visitCount == 0:
        try:
            visitCount = int(match2[0])
        except Exception:
            visitCount = 0
    """
    return visitCount


def filter_tags(html_str):
    soup = BeautifulSoup(html_str)
    title = getTitle(html_str)
    date = getDate(html_str)
    visitCount = getVisit(html_str)
    [script.extract() for script in soup.findAll('script')]
    [style.extract() for style in soup.findAll('style')]
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
    [comment.extract() for comment in comments]
    reg1 = re.compile("<[^>]*>")
    content = reg1.sub('', soup.prettify()).split('\n')
    return title, content, date, visitCount


def getcontent(lst, title, authorset):
    lstlen = [len(x) for x in lst]
    threshold = 50
    startindex = 0
    maxindex = lstlen.index(max(lstlen))
    endindex = 0
    for i, v in enumerate(lstlen[:maxindex - 3]):
        if v > threshold and lstlen[i + 1] > 5 and lstlen[i + 2] > 5 and lstlen[i + 3] > 5:
            startindex = i
            break
    for i, v in enumerate(lstlen[maxindex:]):
        if v < threshold and lstlen[maxindex + i + 1] < 10 and lstlen[maxindex + i + 2] < 10 and lstlen[
            maxindex + i + 3] < 10:
            endindex = i
            break
    content = ['<p>' + x.strip() + '</p>' for x in lst[startindex:endindex + maxindex] if len(x.strip()) > 0]
    return content


def run(url):
    ctthtml = getcontentfromweb(url)
    title, content, date, visitCount = filter_tags(ctthtml)
    newcontent = getcontent(content, title, authorset)
    ctt = ''.join(newcontent)
    lessContent = ctt.replace(r'<p>', '')
    lessContent = lessContent.replace(r'</p>', '')
    return title, ctt, date, visitCount,lessContent

if __name__ == '__main__':
    url = "http://www.wzrb.com.cn/article877241show.html"
    title, ctt, date, visitCount,lessContent = run(url)
    print(title)
    print(visitCount)
    print(date)
    print(ctt)
    print(lessContent)
