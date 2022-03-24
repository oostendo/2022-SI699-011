import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import time
from random import randint
import csv


csv_data = []

csv_head = ["Rating", "Title", "Date", "Verified Purchase", "Body", "Helpful Votes"]

time_upper_limit = 10

HEADER = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/90.0.4430.212 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})


def set_sleep_timer():
    sleep_time = randint(0, int(time_upper_limit))
    print("\nSleeping for " + str(sleep_time) + " seconds.")
    time.sleep(sleep_time)

def set_url(url):
    # removing pageNumber parameter if it exists in the url
    url = url.split("&pageNumber")
    # if len(url) > 1:
    #     return url[0]
    return url[0]
    

def set_start_page(start_page, url):
    return url + "&pageNumber=" + str(start_page)

def build_rating(review):
    return str(review).split("<span class=\"a-icon-alt\">")[1].split("</span>")[0].split(" ")[0]

def build_title(review):
    return str(review).split("data-hook=\"review-title\"")[1].split("\">")[1].split("</a>")[0]

def build_date(review):
    return review.split("on")[1].strip()

def build_body(review):
    body = str(review).split("data-hook=\"review-body\">")[1].split("</span>")[0] + "\n"
    body = body.replace("<br>", ".").replace("<br/>", ".").replace("</br>", ".").strip()
    return body


def scrape(url, start_page, end_page):
    global csv_data, HEADER
    
    if end_page < start_page:
        print("Start page cannot be greater than end page. Please try again.")
        exit()

    url = set_url(url)

    while start_page <= end_page :

        url = set_start_page(start_page, url)

        # 
        # set_sleep_timer()

        print("Scraping page " + str(start_page) + ".")
        

        values = {}

        data = urllib.parse.urlencode(values).encode('utf-8')
        req = urllib.request.Request(url, data, HEADER)
        response = urllib.request.urlopen(req)
        html = response.read()

        soup = BeautifulSoup(html, 'html.parser')
        reviews = soup.find("div", attrs={"class": "a-section a-spacing-none reviews-content a-size-base"}).find(class_ = "a-section a-spacing-none review-views celwidget").find_all(class_="a-section celwidget")

        for review in reviews:
            

            csv_body = []

            # Star Rating
            rating = build_rating(review)
            csv_body.append(rating)

            # Title
            title = build_title(review)
            csv_body.append(title)
            
            # Date
            date = build_date(review.find("span", class_ = "a-size-base a-color-secondary review-date").text)
            csv_body.append(date)

            # Body
            body = build_body(review)
            csv_body.append(body)

            csv_data.append(csv_body)

        start_page += 1

def write_csv(file_name):
    global csv_data

    print("\nWriting to file.\n")

    with open((file_name + '.csv'), 'w+') as csv_file :
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerows(csv_data)

urls = ["https://www.amazon.com/Yankee-Candle-Large-Vanilla-Cupcake/product-reviews/B000X457HO/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber=1",
"https://www.amazon.com/Yankee-Candle-Large-Lilac-Blossoms/product-reviews/B000WQY7RO/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber=1",
"https://www.amazon.com/Yankee-Candle-Large-Balsam-Cedar/product-reviews/B000JDGC78/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber=1",
"https://www.amazon.com/Yankee-Candle-Large-Mango-Peach/product-reviews/B001PAPPKY/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber=1",
"https://www.amazon.com/Yankee-Candle-Scented-Sugared-Cinnamon/product-reviews/B07FCT517B/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber=1",
"https://www.amazon.com/Yankee-Candle-Large-Sage-Citrus/product-reviews/B000P6THK8/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&pageNumber=1&sortBy=recent",
"https://www.amazon.com/Yankee-Candle-Large-Pink-Sands/product-reviews/B004G9C0SQ/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber=1",
"https://www.amazon.com/Yankee-Candle-Large-Autumn-Wreath/product-reviews/B000TVJ6XW/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber=1",
"https://www.amazon.com/Yankee-Candle-Large-Lemon-Lavender/product-reviews/B000WQZ5PC/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber=1",
"https://www.amazon.com/Yankee-Candle-Large-Bahama-Breeze/product-reviews/B004G9DV66/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber=1"]

csv_data.append(csv_head)

for url in urls:
    scrape(url, 1, 50)
write_csv("reviews")