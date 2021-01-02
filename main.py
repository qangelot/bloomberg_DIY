import requests
import smtplib
from email.mime.multipart import MIMEMultipart


# DIY a small bloomberg like app to request some news about stocks 

STOCK_NAME = "MSFT"
COMPANY_NAME = "Microsoft Corporation"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = "STOCK_API_KEY"
NEWS_API_KEY = "NEWS_API_KEY"

# Use a dummy email account and lower security options to allow this script to work
MY_EMAIL = "test_email"
MY_PASSWORD = "password"

## Get stocks variation from https://www.alphavantage.co/documentation/#daily
#Get closing stock price for yesterday and day before
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}

response = requests.get(STOCK_ENDPOINT, params=stock_params)
data = response.json()["Time Series (Daily)"]
# Transforming Json into a list to easily get data
data_list = [v for (k, v) in data.items()]
yesterday_data = data_list[0]
yesterday_closing_price = yesterday_data["4. close"]

# Day before
day_before_data = data_list[1]
day_before_closing_price = day_before_data["4. close"]

# Computing variation and creating an up or down emoji
difference = float(yesterday_closing_price) - float(day_before_closing_price)
up_or_down = None
if difference > 0:
    up_or_down = "UP"
else:
    up_or_down = "DOWN"

variation = round((difference / float(day_before_closing_price)) * 100, 2)
print(variation)
# If variation percentage is greater than 5 then fetch news data
if abs(variation) > 5:
    news_params = {
        "apiKey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME,
    }

    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    articles = news_response.json()["articles"]
    first_articles = articles[:3]

    ## process the news and send them by email
    subject = f"{STOCK_NAME}: {up_or_down} {variation}% "
    formatted = [f"Headline: {article['title'].encode('utf-8')  } \
    \nBrief: {article['description'].encode('utf-8')  }" for article in first_articles]

    with smtplib.SMTP("smtp.gmail.com.") as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=MY_EMAIL,
            msg=f"Subject: {subject} \n\n{formatted[0]} \n{formatted[1]} \n{formatted[2]}"
        )
