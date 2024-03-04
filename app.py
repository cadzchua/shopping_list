from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import requests

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = 'iloveflasks'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

db.init_app(app)

class ShoppingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(100), nullable=True)
    checked = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        items_name = request.form["input_items_name"]
        new_item = ShoppingItem(name=items_name)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for("home"))
    items = ShoppingItem.query.all()
    return render_template("index.html", items=items)

@app.route("/checked/<int:item_id>", methods=["POST"])
def checked_items(item_id):
    item = ShoppingItem.query.get_or_404(item_id)
    item.checked = not item.checked
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/edit_items/<int:item_id>", methods=["GET", "POST"])
def edit_items(item_id):
    item = ShoppingItem.query.get_or_404(item_id)
    if request.method == "POST":
        new_name = request.form.get("name")
        try:
            item.name = new_name
            db.session.commit()
            flash("Item name updated successfully.", "success")
            return redirect(url_for("home"))
        except Exception as e:
            flash(f"There was a problem updating the item name: {str(e)}", "error")
            db.session.rollback()
            return redirect(url_for("home"))
    return render_template("update.html", item=item)


@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_items(item_id):
    item = ShoppingItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/clear_checked_items", methods=["POST"])
def clear_checked_items():
    checked_items = ShoppingItem.query.filter_by(checked=True).all()
    for item in checked_items:
        db.session.delete(item)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/clear_all_items", methods=["POST"])
def clear_all_items():
    try:
        db.session.query(ShoppingItem).delete()
        db.session.commit()
        return redirect(url_for("home"))  
    except Exception as e:
        db.session.rollback()
        print("An error occurred:", str(e))
        flash(f"There was a problem updating the item name: {str(e)}", "error")
        return redirect(url_for("home"))

@app.route("/googlemap", methods=["GET", "POST"])
def googlemap():
    if request.method == "POST":
        if 'geolocation' in request.headers.get('User-Agent'):
            return render_template("googlemap.html", use_geolocation=True)
        else:
            location = "Singapore"
            radius = 5
            keyword = "shopping mall" 

            places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&keyword={keyword}&key=YOUR_API_KEY"
            response = requests.get(places_url)
            data = response.json()

            return render_template("googlemap.html", data=data)

    return render_template("googlemap.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=6969)
