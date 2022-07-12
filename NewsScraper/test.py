from utils import Article # defines article structure
import datetime

print("simple analysis")

with open("test-article_body.txt", "r") as file:
    data = file.read()

test_article = Article(
    headline = "BASF und MAN Energy Solutions vereinbaren Zusammenarbeit für den Bau einer der weltgrößten Wärmepumpen in Ludwigshafen",
    body = data,
    author = ["Patricia Weiss", "Christoph Steitz"],
    date = datetime.datetime.strptime("June 23, 2022", "%B %d, %Y")
)

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

score = 0
for sentence in [test_article.headline, test_article.body]:
    vs = analyzer.polarity_scores(sentence)
    print(vs, str(vs))
    score += vs["compound"]

print(f"score = {score}, avg = {score / 2}")



print("adv. analysis") # TODO: split in sentences

with open("test-article_body.txt", "r") as file:
    data = file.readlines()

test_article = Article(
    headline = "BASF und MAN Energy Solutions vereinbaren Zusammenarbeit für den Bau einer der weltgrößten Wärmepumpen in Ludwigshafen",
    body = data,
    author = ["Patricia Weiss", "Christoph Steitz"],
    date = datetime.datetime.strptime("June 23, 2022", "%B %d, %Y")
)


body_score = 0
for sentence in test_article.body:
    body_score += analyzer.polarity_scores(sentence)["compound"]

headline_score = analyzer.polarity_scores(test_article.headline)["compound"]

print(body_score, headline_score, body_score + headline_score, (body_score+headline_score) / 2)