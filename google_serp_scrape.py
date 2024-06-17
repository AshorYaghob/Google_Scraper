from bs4 import BeautifulSoup
import requests
import urllib
import json
import os
import signal


class GoogleDataSource():
    # num_google_page_search = 1

    #-----------------------------------------------------------------------
    # this function is used to prevent Too Many Requests error
    #-----------------------------------------------------------------------
    def handler(signum, frame):
        raise Exception("Signal handler called with signal %s" % signum)

    signal.signal(signal.SIGALRM, handler)

    def meta_redirect(self, content):
        soup  = BeautifulSoup(content, 'html.parser')

        result=soup.find("meta",attrs={"http-equiv":"Refresh"})
        if not result:
            result=soup.find("meta",attrs={"http-equiv":"refresh"})
        if result:
            wait,text=result["content"].split(";")
            if text.strip().lower().startswith("url="):
                url=text[4:]
                return url
        return None
    
    #TODO
    #we may have to change the filter at the end to exclude only searches that have google in the domain
    #What if we have a search like "is google a bad search engine" and google is in the url ? 
    #We can do something like strip anything before .co, .com. .uk ... etc
    def getLinks(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        links = [goodlist.get('href') for goodlist in soup.find_all('a')]
        links = [i for i in links if i]
        for link in links:
            if link[:7] =="/url?q=":
                lq = urllib.parse.parse_qs(link)["/url?q"][-1]
                links.append(lq)
            pass
        return [link for link in links if link[:4]=="http" and "google" not in link ]
    

    def getDefaultCookie(self, scookies):
        cm = [{'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path} for c in scookies ]
        return str(cm[0]["name"]+"="+cm[0]["value"]+"; "+cm[1]["name"]+"="+cm[1]["value"])
    
    def search(self, query, pages):
        signal.alarm(10)
        s = requests.Session()
        seen = set()
        s.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Upgrade-Insecure-Requests": "1",
                "Connection": "keep-alive",
                "Sec-Fetch-User": "?1",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
            }
        )
        loc = "https://google.com/search"
        while True:
            r = s.get(
                "https://google.com/search",
                params={"q": query},
                headers={
                    "Host": "google.com",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                },allow_redirects=False
            )
            loc = r.headers['location']
            if loc in seen: break
            seen.add(loc)



        s.headers.update({"Host": "www.google.com"})

        r = s.get(
            "https://www.google.com/search",
            params={"q": query},
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
            },
        )
        #response
        #<meta content="0;url=/search?q=orion+nelson&amp;gbv=1&amp;sei=4IqVYa6wNN60qtsPofaxuAU" http-equiv="refresh">

        dcookie = self.getDefaultCookie(s.cookies)
        redirect= self.meta_redirect(r.content)
        links = self.getLinks(r.content)
        ps = urllib.parse.parse_qs(redirect)
        gbv = ps["gbv"][-1]
        sei = ps["sei"][-1]

        s.headers.update(
            {
                "Upgrade-Insecure-Requests": None,
                "Sec-Fetch-User": None,
                "Accept": "image/webp,*/*",
                "Referer": "https://www.google.com/",
                "Sec-Fetch-Dest": "image",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers",
            }
        )

        r = s.get(
            "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png",
            headers={
                "Cookie": dcookie
            },
        )


        r = s.get(
            "https://www.google.com/favicon.ico",
            headers={
                "Cookie": dcookie
            },
        )

        s.headers.update({"Upgrade-Insecure-Requests": "1"})

        r = s.get(
            "https://www.google.com/search",
            params={"q": query, "gbv": gbv, "sei": sei},
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Cookie": dcookie,
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Referer": None,
            },
        )
        #Renew Dcookie
        dcookie = self.getDefaultCookie(s.cookies)

        #Soup Must Fetch the Above Request Thats why this is here
        soup = BeautifulSoup(r.content, 'html.parser')

        s.headers.update(
            {
                "Upgrade-Insecure-Requests": None,
                "Cookie": dcookie,
            }
        )

        r = s.get(
            "https://www.google.com/favicon.ico",
        )
        #<a class="nBDE1b G5eFlf" href="/search?q=orion+nelson&amp;gbv=1&amp;ei=4YqVYdflLZWnqtsPr5yE4A4&amp;start=10&amp;sa=N" aria-label="Next page">
        s.headers.update({"Upgrade-Insecure-Requests": "1", "Sec-Fetch-User": "?1"})
        counter = 1
        while counter < pages:
            alink = [goodlist.get('href') for goodlist in soup.find_all('a') if goodlist.get('aria-label')=="Next page"]
            cq = urllib.parse.parse_qs(alink[-1])
            ei = cq["ei"]
            r = s.get(
                "https://www.google.com/search",
                params={
                    "q": query,
                    "gbv": gbv ,
                    "ei": ei,
                    "start": str(10*counter),
                    "sa": "N",
                },
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-User": "?1",
                },
            )
            links.extend(list(self.getLinks(r.content)))
            soup = BeautifulSoup(r.content, 'html.parser')


            s.headers.update({"Upgrade-Insecure-Requests": None, "Sec-Fetch-User": None})

            r = s.get(
                "https://www.google.com/favicon.ico",
            )
            counter = counter + 1
        signal.alarm(0)
        return links
    

if __name__ == "__main__":
    query = "Justin Trudeau"
    g = GoogleDataSource()
    #change it to how many pages you want
    links = g.search(query, 1) # only one page for this demo
    cnt = 0
    for link in links:
        print("url:", link)
        cnt += 1