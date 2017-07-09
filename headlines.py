import datetime
import feedparser
import json
import urllib
import urllib2
from flask import Flask, render_template, request, make_response
import myapis
app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}
DEFAULTS = {'publication': 'bbc',
            'city': 'London,UK',
            'currency_from': 'CNY',
            'currency_to': 'USD'}

CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=%s" % (myapis.get_open_currency())


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.form.get(key):
        return request.form.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]


@app.route("/", methods=['GET', 'POST'])
def home():
    publication = get_value_with_fallback("publication")
    articles = get_news(publication)
    city = get_value_with_fallback("city")
    weather = get_weather(city)
    currency_from = get_value_with_fallback("currency_from")
    currency_to = get_value_with_fallback("currency_to")
    rate, currencies = get_rates(currency_from, currency_to)
    response = make_response(render_template("home.html", articles=articles, weather=weather,
                                             currency_from=currency_from, currency_to=currency_to, rate=rate,
                                             currencies=sorted(currencies)))
    expires = datetime.datetime.now()+datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response
#    return render_template("home.html", articles=articles, weather=weather, currency_from=currency_from,
#                           currency_to=currency_to, rate=rate, currencies=sorted(currencies))
#@app.route("/<publication>")    #dynamic route


def get_news(query):
    print(query)
    if not query or query.lower() not in RSS_FEEDS:
        publication="bbc"
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS.get(publication))
#    first_article = feed['entries'][0]
#    weather = get_weather("London,UK")
#    return render_template("home.html", articles=feed['entries'],weather=weather)
    return feed['entries']


def get_weather(query):
    print(myapis.get_open_weather())
    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=%s" % (myapis.get_open_weather())
    print(api_url)
    query = urllib.quote(query)
    url = api_url.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    if parsed.get("weather"):
        weather = {"description":parsed["weather"][0]["description"], "temperature":parsed["main"]["temp"], "city": parsed["name"],
                   'country': parsed['sys']['country']}
    return weather


def get_rates(frm, to):
    all_currency = urllib2.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate/frm_rate, parsed.keys())






# @app.route("/")
# @app.route("/bbc")
# def bbs_news():
#     return get_news("bbc")
#
# @app.route("/cnn")
# def cnn_news():
#     return get_news("cnn")
#
# @app.route("/fox")
# def fox_news():
#     return get_news("fox")



if __name__ == "__main__":
    app.run(port=5000, debug=True)
