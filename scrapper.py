from lxml import html
import requests

url = "https://weather.com/weather/today/l/c96b51c0dfb56cf48d138d54f0877301eefcb12228059a43b2cd5f15769f020a"
path = "//*[@id=\"main-Nowcard-92c6937d-b8c3-4240-b06c-9da9a8b0d22b\"]/div/div/section/div[3]/table/tbody/tr[1]/td/span/text()"

# get a single data point from xpath
def ScrapeXpath(url, path):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    text = tree.xpath(path + "/text()")
    print(text)
    return text

# get multiple data points from multiple xpaths from the same url
# used for optimization of requests to the same URL
def ScrapeXpaths(url, paths):
    page = requests.get(url)
    # html tree to navigate
    tree = html.fromstring(page.content)
    result = []

    # grab all values
    for i in paths:
        result.append(tree.xpath(i))
    
    return result

if __name__ == '__main__':
    print(ScrapeXpath(url, path))