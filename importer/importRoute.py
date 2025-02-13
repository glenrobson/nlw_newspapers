"""Product pages."""
from flask import Blueprint
from flask import current_app as app
from flask import render_template,request,redirect, url_for

from utils import importer 

# Blueprint Configuration
import_blueprint = Blueprint("import_blueprint", __name__, template_folder="templates", static_folder="static")

@import_blueprint.route("/import/", methods=["GET"])
def import_root() -> str:
    """
    """
    return render_template(
        "main.html")


@import_blueprint.route("/import/import", methods=["POST"])
def import_asset() -> str:
    """
    """
    manifestURI = request.form.get("manifest")  # Get form input
    PID = request.form.get("pid")

    if manifestURI:
        PID = importer.importNewspaper(manifest=manifestURI)
    else:
        importer.importNewspaper(pid=PID)

    return redirect(url_for("view_blueprint.home"))