from collections import Counter
import operator
import hashlib

from flask import Flask, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from newspaper import Article
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required, URL


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'Ringa Linga'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./data.db'
db = SQLAlchemy(app)


def md5_convert(string):
    md5_obj = hashlib.md5(string)
    return md5_obj.hexdigest()


class UrlForm(Form):
    url = StringField("Paste your article's url bellow", validators=[URL()])
    submit = SubmitField("Parse")


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    md5_key = db.Column(db.String, unique=True)
    title = db.Column(db.String)
    content = db.Column(db.Text)
    keywords = db.Column(db.String)
    description = db.Column(db.String)
    top_image = db.Column(db.String)

    def __init__(self, md5_key, title, content, keywords, description,
            top_image):
        self.md5_key = md5_key
        self.title = title
        self.content = content
        self.keywords = keywords
        self.description = description
        self.top_image = top_image

    def __repr__(self):
        return 'Title: %s' % self.title


@app.route("/", methods=["GET", "POST"])
def index():
    url = None
    form = UrlForm()
    if form.validate_on_submit():
        session['url'] = form.url.data
        url_to_md5 = md5_convert(session['url'])
        results = Data.query.filter_by(md5_key="{}".format(url_to_md5)).first()
        if not results:
            data = parse(session['url'])
            items = ["%s,%s" % i for i in data['content_sorted']]
            items_to_str = "|".join(items)
            import_data = Data(md5_key=url_to_md5,
                    title=data['title'],
                    content=data['content'],
                    keywords=items_to_str,
                    description=data['description'],
                    top_image=data['top_image']
                    )
            db.session.add(import_data)
            db.session.commit()
            return redirect('/parsed/{0}'.format(url_to_md5))
        else:
            return redirect('/parsed/{0}'.format(url_to_md5))
    return render_template('index.html',
                           form=form,
                           url=session.get('url')
                           )

def parse(url):
    article = Article(url)
    article.download()
    article.parse()
    content = []

    for line in article.text.splitlines():
        for word in line.split():
            content.append(word)

    content_counter = Counter(content)
    content_sorted = sorted(content_counter.items(),
                            key=operator.itemgetter(1)
                            )
    content_sorted.reverse()

    data = {}
    data['title'] = article.title
    data['content'] = article.text
    data['top_image'] = article.top_image
    data['content_sorted'] = content_sorted
    data['url'] = article.url
    data['description']=article.meta_description

    return data


@app.route("/parsed/<md5>")
def data_render(md5):
    results = Data.query.filter_by(md5_key=md5).first()
    keywords = []
    for i in results.keywords.split("|"):
        keywords.append(tuple(i.split(",")))
    return render_template('results.html',
            content=results.content,
            top_image=results.top_image,
            title=results.title,
            description=results.description,
            keywords=keywords)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
