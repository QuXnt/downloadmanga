# Made by QuXnt

from pathlib import Path
from send2trash import send2trash
from prettytable import PrettyTable
import requests, sys, bs4, os, lxml, time, img2pdf, threading
queryurl = 'https://ww7.mangakakalot.tv/search/'
lchp = ''
imgdir = "C:/trashimg"
dest = "C:/manga"
passlist = sys.argv[1: len(sys.argv) - 1]
passarg = sys.argv[1:]

def decide(args):
    try:
        a = int(args[-2])
        b = int(args[-1])
        return "multiple"
    except:
        if args[-1] == 'latest':
            return "latest"
        else:
            return "single"

def getquery(args):
    q = ''
    try:
        a = int(args[-2])
        b = int(args[-1])
        for c in args[:-2]:
            q += c
            q += '%20'
        return q
    except:
        if args[-1] == 'latest':
            for c in args[:-1]:
                q += c
                q += '%20'
            return q
        else:
            for c in args[:-1]:
                q += c
                q += '%20'
            return q

def getmangaurl(query):
    global lchp
    mangatable = PrettyTable(["No.", "Title", "Author", "Last Updated"], max_width= 50)
    mangalist = []
    res = requests.get(f'{queryurl}{query}')
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    for i in range(1, 13):
        try:
            mangaurl = soup.select(f'body > div.container > div.main-wrapper > div.leftCol > div.daily-update > div > div:nth-child({i}) > div > h3 > a')[0].attrs['href']
            chpurl = f"https://ww7.mangakakalot.tv/chapter{mangaurl[6:]}/chapter-"
            manganame = soup.select(f'body > div.container > div.main-wrapper > div.leftCol > div.daily-update > div > div:nth-child({i}) > div > h3 > a')[0].getText()
            #temp = soup.select(f'body > div.container > div.main-wrapper > div.leftCol > div.daily-update > div > div:nth-child({i}) > div > em:nth-child(2) > a')[0].attrs['title'].split(" ")
            try:    
                lchpurl = soup.select(f'body > div.container > div.main-wrapper > div.leftCol > div.daily-update > div > div:nth-child({i}) > div > em:nth-child(2) > a')[0].attrs['href']
                lchpno = lchpurl.split("chapter-")[-1]
                temp = str(soup.select(f'body > div.container > div.main-wrapper > div.leftCol > div.daily-update > div > div:nth-child({i}) > div > span:nth-child(4)')[0]).split()
                auth = ''
                for c in temp[2:]:
                    if c == "</span>":
                        break
                    else:
                        auth += c
                        auth += " "
                lastup = soup.select(f'body > div.container > div.main-wrapper > div.leftCol > div.daily-update > div > div:nth-child({i}) > div > span:nth-child(5)')[0].getText().lstrip("Updated : ")
            except:
                auth = "N/A"
                lchpno = 0
                lchpurl = ''
                lastup = "N/A"
            mangatable.add_row([i, manganame, auth, lastup])
            mangalist.append([manganame, mangaurl, lchpno, lchpurl, chpurl])
        except:
            break
    
    print(mangatable)
    inp = input(f"Which manga do you wish to download? ")

    if inp.isalpha():
        sys.exit("Bye")
    print(f"Downloading {mangalist[int(inp) - 1][0]}...")
    lchp = mangalist[int(inp) - 1][2]
    return mangalist[int(inp) - 1]
    
def downImg(i, src):
    req = requests.get(src)
    with open(f"{imgdir}/{i+1}.jpg", "wb") as f:
        f.write(req.content)

def downloadpages(url):
    threads = []
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    img = soup.select('#vungdoc > img')
    for i in img:
        src = i.attrs['data-src']
        downImgThread = threading.Thread(target= downImg, args= (img.index(i), src))
        threads.append(downImgThread)
        downImgThread.start()
        # print(f"Downloading page no. {img.index(i)+1}...")
        # if i == img[-1]:
        #     print("\n")
    
    for th in threads:
        th.join()

def makepdf(namaiwa):
    directory_path = imgdir
    
    ls = os.listdir(directory_path)
    for j in range(len(ls)):
        for i in range(len(ls) - 1):
            try:
                if int(ls[i].split('.')[0]) > int(ls[i + 1].split('.')[0]):
                    temp = ls[i+1]
                    ls[i+1] = ls[i]
                    ls[i] = temp
            except:
                continue

    with open(f"{dest}/{namaiwa}.pdf", "wb") as file:
        file.write(img2pdf.convert([os.path.join(directory_path, i) for i in ls if i.endswith(".jpg")]))
    print(f"Downloaded {namaiwa}.pdf")
    
    os.startfile(f"{dest}/{namaiwa}.pdf")

def deleteimg():
    p = imgdir
    for c in os.listdir(p):
        if c.endswith(".jpg"):
            os.remove(Path(f"{p}/{c}"))
            send2trash(Path(f"{p}/{c}"))

qry = getquery(passarg)
templist = getmangaurl(query= qry)

def downloadManga(chpno= -1):
    if chpno == -1:
        chpno = templist[2]
    print(f"Downloading {templist[0]} Chapter {str(chpno)}...")
    downloadpages(templist[-1] + str(chpno))
    makepdf(f"{templist[0]} Chapter {str(chpno)}")
    deleteimg()

dec = decide(passarg)
if dec == "single":
    downloadManga(int(passarg[-1]))
elif dec == "latest":
    downloadManga()
elif dec == "multiple":
    for i in range(int(passarg[-2]), int(passarg[-1]) + 1):
        downloadManga(i)
else:
    sys.exit("Invalid Input")
    
