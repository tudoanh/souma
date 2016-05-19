#!/usr/bin/python

import argparse
import operator

from collections import Counter
from newspaper import Article

parser = argparse.ArgumentParser(description='Script to show most common words of an article.')

parser.add_argument("url", type=str, help="Url to parse")
args = parser.parse_args()

url = args.url

article = Article(url)
article.download()
article.parse()
article.nlp()

content = []

for line in article.text.splitlines():
    for word in line.split():
        content.append(word)

content_counter = Counter(content)

content_sorted = sorted(content_counter.items(), key=operator.itemgetter(1))

for tup in content_sorted[-50:]:
    print u"Word: {0} - Show: {1} time(s)".format(tup[0], tup[1])

for k in  article.keywords:
    print k
