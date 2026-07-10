from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)


database_url = os.environ.get("DATABASE_URL", "sqlite:///gencbaki.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
db = SQLAlchemy(app)

class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500))
    deadline = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

CATEGORY_KEYWORDS = {
    "Düşərgə": ["düşərgə", "dusərgə", "dusarge", "kamp", "yayfest", "çadır", "cadir", "cadır"],
    "Təcrübə": ["təcrübə", "tecrübe", "tecrube", "internship", "staj"],
    "Kurs": ["kurs", "dərs", "ders", "təlim", "telim", "workshop"],
    "Hackathon": ["hackathon", "yarış", "yaris", "müsabiqə", "musabiqe", "competition"],
    "Startap": ["startap", "startup", "sahibkarlıq", "sahibkarliq", "biznes"],
    "Təqaüd": ["təqaüd", "teqaud", "scholarship", "burs"],
}

def classify_with_ai(description):
    text = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return category
    return "Digər"

@app.route("/")
def home():
    opportunities = Opportunity.query.order_by(Opportunity.created_at.desc()).all()
    return render_template("index.html", opportunities=opportunities)

@app.route("/add", methods=["GET", "POST"])
def add_opportunity():
    if request.method == "POST":
        description = request.form["description"]
        ai_category = classify_with_ai(description)
        new_opportunity = Opportunity(
            title=request.form["title"],
            category=ai_category,
            description=description,
            deadline=request.form["deadline"]
        )
        db.session.add(new_opportunity)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html")

@app.route("/delete/<int:opportunity_id>")
def delete_opportunity(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    db.session.delete(opportunity)
    db.session.commit()
    return redirect(url_for("home"))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)