import requests, sys, webbrowser, bs4

res = requests.get('http://google.com/search?q=' + ' ' .join(sys.argv[1:]))

res.raise_for_status()

soup = bs4.BeautifulSoup(res.text, "html.parser")

linkElems = soup.select('.r a')

numOpen = min(3, len(linkElems))
for i in range(numOpen):
    #print ('http://google.com' + linkElems[i].get('href'))
    webbrowser.open('http://google.com' + linkElems[i].get('href'))
