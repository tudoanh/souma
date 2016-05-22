import operator
from collections import Counter

from flask import Flask, render_template, session, redirect, url_for
from newspaper import Article
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required, URL


app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = 'Ringa Linga'


class UrlForm(Form):
    url = StringField("Paste your article's url bellow", validators=[URL()])
    submit = SubmitField("Parse")


@app.route("/", methods=["GET", "POST"])
def index():
    url = None
    form = UrlForm()
    if form.validate_on_submit():
        session['url'] = form.url.data
        data = parse(session['url'])
        return render_template(
            'resulst.html',
            keywords=data['content_sorted'],
            authors=data['authors'],
            content=data['content'],
            top_image=data['top_image'],
            date=data['publish_date'],
            title=data['title'],
            article_url=data['url'],
            description=data['description'],
            images=data['images']
        )
    return render_template('index.html', form=form, url=session.get('url'))


def parse(url):
    article = Article(url)
    article.download()
    article.parse()
    content = []

    for line in article.text.splitlines():
        for word in line.split():
            content.append(word)

    content_counter = Counter(content)
    content_sorted = sorted(content_counter.items(), key=operator.itemgetter(1))
    content_sorted.reverse()

    data = {}
    data['title'] = article.title
    data['authors'] = article.authors
    data['content'] = article.text
    data['top_image'] = article.top_image
    data['publish_date'] = article.publish_date
    data['content_sorted'] = content_sorted
    data['url'] = article.url
    data['description']=article.meta_description
    data['images'] = article.images

    return data

if __name__ == "__main__":
    app.run(host='0.0.0.0')
