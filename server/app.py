#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])

@app.route("/restaurants/<int:restaurant_id>", methods=["GET"])
def get_restaurant(restaurant_id):
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    restaurant_data = restaurant.to_dict()
    restaurant_data["restaurant_pizzas"] = [rest.pizza.to_dict() for rest in restaurant.restaurant_pizzas]
    
    return jsonify(restaurant_data)

@app.route("/restaurants/<int:restaurant_id>", methods=["DELETE"])
def delete_restaurant(restaurant_id):
    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    db.session.delete(restaurant)
    db.session.commit()
    
    return make_response(jsonify({"message": "Restaurant deleted"}), 204)

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    if not all([price, pizza_id, restaurant_id]):
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    if not (1 <= price <= 30):
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    pizza = db.session.get(Pizza, pizza_id)
    if not pizza:
        return make_response(jsonify({"errors": ["validation errors"]}), 404)

    restaurant = db.session.get(Restaurant, restaurant_id)
    if not restaurant:
        return make_response(jsonify({"errors": ["validation errors"]}), 404)

    restaurant_pizza = RestaurantPizza(price=price, pizza=pizza, restaurant=restaurant)
    db.session.add(restaurant_pizza)
    db.session.commit()

    # return make_response(jsonify({"message": "Added successfully"}),404)

    return jsonify(restaurant_pizza.to_dict()), 201

if __name__ == "__main__":
    app.run(port=5555, debug=True)