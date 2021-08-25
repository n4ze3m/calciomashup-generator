import random
from PIL import Image
from bs4 import BeautifulSoup
import cairosvg
import itertools
import math
import requests
import json
import base64

header ={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
def rgb2hex(color):
    r,g,b = color
    code = "#{:02x}{:02x}{:02x}".format(r, g, b)
    return code

def smallerHex(bigHex):
    smaller = "#"
    for i in [1,3,5]:
        smaller+= bigHex[i]

    return smaller

def downloadLogo(filename,url):
    r = requests.get(url,headers=header)
    cairosvg.svg2png(bytestring=r.text,write_to=f'{filename.lower()}.png')

def getSortedLogoColor():
    logoSortedColors = []
    images = ["team1.png","team2.png"]
    for image in images:
        img = Image.open(image)
        width,height = img.size
        limit = ((width * height) * .01)
        colors = img.convert("RGBA").getcolors(img.size[0] * img.size[1])
        colors = sorted(colors, key=lambda x: x[0], reverse=True)
        colors = [c for c in colors if c[1][3] != 0]
        colorb1 = [rgb2hex(color[1][:3])
                       for color in colors[:5] if color[0] > limit]
        combinations = itertools.combinations(colorb1, 2)

        for pair in combinations:
            r1,g1,b1 = tuple(int(pair[0].replace("#", "")[i:i + 2], 16) for i in (0, 2, 4))
            r2,g2,b2 = tuple(int(pair[1].replace("#", "")[i:i + 2], 16) for i in (0, 2, 4))
            dif =  math.sqrt(math.pow(r1 - r2, 2) + math.pow(g1 - g2, 2) + math.pow(b1 - b2, 2))
            if dif < 50 and pair[1] in colorb1:
                colorb1.remove(pair[1])
        logoSortedColors.append(colorb1)
    return logoSortedColors

global oldColors, newColors

def selectTemplateAndColor(template_data,nameColorList):
    FIRSTTEAM=NAME=0
    LASTTEAMN=COLORS = 1

    template = nameColorList[FIRSTTEAM][NAME]
    color = nameColorList[LASTTEAMN][NAME]

    if len(nameColorList[FIRSTTEAM][COLORS]) > len(nameColorList[LASTTEAMN][COLORS]):
        template,color = color,template

    elif len(nameColorList[FIRSTTEAM][COLORS]) == len(nameColorList[LASTTEAMN][COLORS]):
        if random.randint(0, 2) == 0:
            template,color = color,template
        else:
            template,color = template,color

    tp = template
    templateSvg = requests.get(template_data[template],headers=header)

    for i in nameColorList:
        if i[NAME] == color:
            newColors= i[COLORS]
        else:
            oldColors = i[COLORS]

    colorDict = dict(zip(newColors, oldColors))
        
    return templateSvg.text, colorDict,tp

def clean(text):
    colors_file = open("colors","r")
    color_codes = colors_file.readlines()
    color_codes = [code.split(",") for code in color_codes]

    clean = {}
    for code in color_codes:
        code = code[0].split()
        clean[code[0].lower()] = code[1].replace("\n", "")

    data2 = text

    for key, value in clean.items():
        tag = f'fill="{key}"'

        if tag in data2:
            new_value =  f'fill="{value}"'
            data2.replace(tag, new_value)

        tag=f'fill:{key}'

        if tag in data2:
            new_value = f'fill:{value}'
            data2.replace(tag, new_value)

        if data2 is not text:
            text = data2

        soup = BeautifulSoup(text,"lxml")
        svg = soup.find("svg")

        svg_rects = svg.findAll("react",recursive=False)
        differs = False

        for t in svg_rects:
            fill = t.get("fill")

            if fill is None and t.get("style") is None and t.get("stroke") is None:
                t['fill'] = "#000000"
                differs = True

        svg_paths = svg.findAll('path', recursive=False)

        for t in svg_paths:
            fill = t.get("fill")
            if fill is None and t.get("style") is None and t.get("stroke") is None:
                t['fill'] = "#000000"
                differs = True

        if differs:
            data = str(svg).replace("<html><body>","\n").replace("</body></html>", "")
            text = data

        return text
def mix(svg,changes):
    svgText = clean(svg)
    for new, old in changes.items():
        svgText =  svgText.replace(old, new.replace('#', 'ç'))
        svgText = svgText.replace(old.upper(), new.replace('#', 'ç'))

    for new, old in changes.items():
        svgText = svgText.replace(smallerHex(old), new.replace('#', 'ç'))
        svgText =  svgText.replace(smallerHex(old).upper(), new.replace('#', 'ç'))

    svgText = svgText.replace('ç', '#')
    #bigger = max(width,height,4096)

    cairosvg.svg2png(bytestring=svgText.replace("viewbox", "viewBox"), write_to="output.png", scale=2.0)


def generate(t1, t2):

	url = "https://football-json.nazeemnato.repl.co/api/details"
	headers = {"Content-type": "application/json"}
	body = {'t1': t1, 't2': t2}
	response = requests.post(url=url, data=json.dumps(body), headers=headers)
	tData = response.json()

	template_data = {0: tData["team1"]["image"], 1:tData["team2"]["image"]}

	downloadLogo("team1",tData["team1"]["image"])
	downloadLogo("team2",tData["team2"]["image"])

	c1,c2 = getSortedLogoColor()
	template,colors,tp = selectTemplateAndColor(template_data,[(0,c1),(1,c2)])
	mix(template,colors)

	output = {}

	with open("output.png","rb") as image2string:
		image_64 = base64.b64encode(image2string.read())
		output["image"] = image_64.decode()
		
	return output
