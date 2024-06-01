from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:database_password@localhost:5432/database'
db = SQLAlchemy(app)

# Sprawdzenie połączenia z bazą danych
try:
    with app.app_context():
        db.session.execute(text('SELECT * FROM units'))
except Exception as e:
    print(f"Błąd połączenia z bazą danych: {e}", file=sys.stderr)
    sys.exit(1)

class Unit(db.Model):
    __tablename__ = 'units'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    ammo = db.Column(db.String(50))

@app.route('/units', methods=['GET'])
def get_units():
    units = Unit.query.all()
    return jsonify([{'id': unit.id, 'name': unit.name, 'ammo': unit.ammo} for unit in units])

@app.route('/unit/<int:id>', methods=['GET'])
def get_unit(id):
    unit = Unit.query.get(id)
    if unit:
        return jsonify({'id': unit.id, 'name': unit.name, 'ammo': unit.ammo})
    else:
        return jsonify({'error': 'Unit not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0')