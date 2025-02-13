"""View pages"""
from flask import Blueprint
from flask import current_app as app
from flask import render_template,request,redirect, url_for
from model import newspaper_data, alto
from utils import regionAnnos


# Blueprint Configuration
view_blueprint = Blueprint("view_blueprint", __name__, template_folder="templates", static_folder="static")

@view_blueprint.route("/", methods=["GET"])
def home() -> str:
    """
    """
    newspapers = newspaper_data.all()
    print ("newspapers:")
    print(newspapers)
    return render_template(
        "homepage.html",
        newspapers=newspapers)

@view_blueprint.route("/view/<int:pid>", methods=["GET"])
def view_issue(pid: int) -> str:
    """
    """
    newspaper = newspaper_data.get(pid)
    return render_template(
        "pages.html",
        newspaper=newspaper)        

@view_blueprint.route("/view/<int:issue>/<int:page>", methods=["GET"])
def view_page(issue: int, page: int) -> str:
    """
    """
    newspaper = newspaper_data.get(issue)
    articles = newspaper.getArticles(page)
    return redirect(url_for("view_blueprint.view_article",issue=issue,page=page,article=articles[0].id))

@view_blueprint.route("/view/<int:issue>/<int:page>/<string:article>", methods=["GET"])
def view_article(issue: int, page: int, article: str) -> str:
    newspaper = newspaper_data.get(issue)
    article = newspaper.article(article)
    annotations = {}
    annotations["tesseract"] = regionAnnos.get(newspaper, article)
    annotations["alto"] = alto.get(newspaper, article)
    return render_template(
        "article.html",
        newspaper = newspaper,
        page=page,
        article=article,
        annotations=annotations
    )
        