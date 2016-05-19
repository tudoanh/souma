import operator
from collections import Counter

from flask import Flask, render_template, session, redirect, url_for
from newspaper import Article
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required, URL
from flask.ext.bootstrap import Bootstrap


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'Ringa Linga'
bootstrap = Bootstrap(app)


class UrlForm(Form):
    url = StringField("Paste your article's url", validators=[URL()])
    submit = SubmitField("Parse")


@app.route("/", methods=["GET", "POST"])
def index():
    url = None
    form = UrlForm()
    if form.validate_on_submit():
        session['url'] = form.url.data
        k = parse(session['url'])
        return render_template('resulst.html', keywords = k)
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

    return content_sorted

if __name__ == "__main__":
    app.run()
