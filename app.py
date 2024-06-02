from flask import Flask, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:database_password@192.168.43.218:5432/earofnapoleon'
db = SQLAlchemy(app)

# Sprawdzenie połączenia z bazą danych
try:
	with app.app_context():
		db.session.execute(text('SELECT * FROM reports'))
except Exception as e:
	print(f"Błąd połączenia z bazą danych: {e}", file=sys.stderr)
	sys.exit(1)

class Point(db.Model):
	__tablename__ = "points"

	id = db.Column(db.Integer, primary_key = True)
	location = db.Column(db.String(64))
	time = db.Column(db.Integer)	# time of last contact/report
	type = db.Column(db.String(50))

	__mapper_args__ = {
		'polymorphic_on': type,
		'polymorphic_identity': 'point'
	}

@app.route('/points', methods=['GET'])
def get_points():
	points = Point.query.all()
	return jsonify([{'id': point.id, 'location': point.location, 'time': point.time, 'type': point.type} for point in points])

@app.route('/point/<int:id>', methods=['GET'])
def get_point(id):
	point = Point.query.get(id)
	if point:
		return jsonify({'id': point.id, 'location': point.location, 'time': point.time, 'type': point.type})
	else:
		return jsonify({'error': 'Point not found'}), 404	
	
class Ally(Point):
	__tablename__ = "allies"

	id = db.Column(db.Integer, db.ForeignKey('points.id'), primary_key=True)
	name = db.Column(db.String(64))
	losses = db.Column(db.Integer)
	ammunition = db.Column(db.Integer)
	equipment = db.Column(db.Integer)
	situation = db.Column(db.String(64))
	action = db.Column(db.String(64))

	__mapper_args__ = {
		'polymorphic_identity': 'ally'
	}

@app.route('/allies', methods=['GET'])
def get_allies():
	allies = Ally.query.all()
	return jsonify([{'id': ally.id, 'name': ally.name, 'losses': ally.losses, 'ammunition': ally.ammunition, 'equipment': ally.equipment, 'situation': ally.situation, 'action': ally.action} for ally in allies])

@app.route('/ally/<int:id>', methods=['GET'])
def get_ally(id):
	ally = Ally.query.get(id)
	if ally:
		return jsonify({'id': ally.id, 'name': ally.name, 'losses': ally.losses, 'ammunition': ally.ammunition, 'equipment': ally.equipment, 'situation': ally.situation, 'action': ally.action})
	else:
		return jsonify({'error': 'Ally not found'}), 404

class Enemy(Point):
	__tablename__ = "enemies"

	id = db.Column(db.Integer, db.ForeignKey('points.id'), primary_key=True)
	size = db.Column(db.Integer)
	activity = db.Column(db.String(64))
	uniforms = db.Column(db.String(64))
	equipment = db.Column(db.String(64))

	__mapper_args__ = {
		'polymorphic_identity': 'enemy'
	}

@app.route('/enemies', methods=['GET'])
def get_enemies():
	enemies = Enemy.query.all()
	return jsonify([{'id': enemy.id, 'size': enemy.size, 'activity': enemy.activity, 'uniforms': enemy.uniforms, 'equipment': enemy.equipment} for enemy in enemies])

@app.route('/enemy/<int:id>', methods=['GET'])
def get_enemy(id):
	enemy = Enemy.query.get(id)
	if enemy:
		return jsonify({'id': enemy.id, 'size': enemy.size, 'activity': enemy.activity, 'uniforms': enemy.uniforms, 'equipment': enemy.equipment})
	else:
		return jsonify({'error': 'Enemy not found'}), 404
	
class Evacuation(Point):
	__tablename__ = "units"

	id = db.Column(db.Integer, db.ForeignKey('points.id'), primary_key=True)
	size = db.Column(db.Integer)			# number of people in need of evacuation
	frequency = db.Column(db.Float)
	activity = db.Column(db.String(64))
	equipment = db.Column(db.String(64))	# required equipment
	safety = db.Column(db.String(64))
	landing_site_marking = db.Column(db.String(64))
	nationality = db.Column(db.String(64))
	contamination = db.Column(db.String(64))
	
	__mapper_args__ = {
		'polymorphic_identity': 'evacuation'
	}

@app.route('/evacuations', methods=['GET'])
def get_evacuations():
	evacuations = Evacuation.query.all()
	return jsonify([{'id': evacuation.id, 'size': evacuation.size, 'frequency': evacuation.frequency, 'activity': evacuation.activity, 'equipment': evacuation.equipment, 'safety': evacuation.safety, 'landing_site_marking': evacuation.landing_site_marking, 'nationality': evacuation.nationality, 'contamination': evacuation.contamination} for evacuation in evacuations])

@app.route('/evacuation/<int:id>', methods=['GET'])
def get_evacuation(id):
	evacuation = Evacuation.query.get(id)
	if evacuation:
		return jsonify({'id': evacuation.id, 'size': evacuation.size, 'frequency': evacuation.frequency, 'activity': evacuation.activity, 'equipment': evacuation.equipment, 'safety': evacuation.safety, 'landing_site_marking': evacuation.landing_site_marking, 'nationality': evacuation.nationality, 'contamination': evacuation.contamination})
	else:
		return jsonify({'error': 'Enemy not found'}), 404

class Report(db.Model):
	__tablename__ = "reports"

	id = db.Column(db.Integer, primary_key = True)

	sent_by = db.Column(db.Integer, db.ForeignKey("allies.id"))
	sender = db.relationship("Ally", backref = "allies", lazy = False)
	recording = db.Column(db.Integer)
	transcription = db.Column(db.String(64))
	type = db.Column(db.String(50))

	__mapper_args__ = {
		'polymorphic_on': type,
		'polymorphic_identity': 'report'
	}

@app.route('/reports', methods=['GET'])
def get_reports():
	reports = Report.query.all()
	return jsonify([{
		'id': report.id, 
		'sent_by': report.sent_by, 
		'sender': {
			'id': report.sender.id,
			'name': report.sender.name,
			'losses': report.sender.losses,
			'ammunition': report.sender.ammunition,
			'equipment': report.sender.equipment,
			'situation': report.sender.situation,
			'action': report.sender.action
		} if report.sender else None,
		'recording': report.recording, 
		'transcription': report.transcription,
		'type': report.type
	} for report in reports])

@app.route('/report/<int:id>', methods=['GET'])
def get_report(id):
	report = Report.query.get(id)
	if report:
		return jsonify({
			'id': report.id, 
			'sent_by': report.sent_by, 
			'sender': {
				'id': report.sender.id,
				'name': report.sender.name,
				'losses': report.sender.losses,
				'ammunition': report.sender.ammunition,
				'equipment': report.sender.equipment,
				'situation': report.sender.situation,
				'action': report.sender.action
			} if report.sender else None,
			'recording': report.recording,
			'transcription': report.transcription,
			'type': report.type
		})
	else:
		return jsonify({'error': 'Report not found'}), 404
	
class GOTWA(Report):
	__tablename__ = 'gotwa_reports'
	id = db.Column(db.Integer, db.ForeignKey('reports.id'), primary_key=True)
	going = db.Column(db.String(64))
	others = db.Column(db.String(64))
	time = db.Column(db.Integer)
	what = db.Column(db.String(64))
	action = db.Column(db.String(64))

	__mapper_args__ = {
		'polymorphic_identity': 'gotwa'
	}

@app.route('/gotwa_reports', methods=['GET'])
def get_gotwa_reports():
	gotwa_reports = GOTWA.query.all()
	return jsonify([{
		'id': gotwa.id, 
		'going': gotwa.going,
		'others': gotwa.others,
		'time': gotwa.time,
		'what': gotwa.what,
		'action': gotwa.action
	} for gotwa in gotwa_reports])

@app.route('/gotwa/<int:id>', methods=['GET'])
def get_gotwa(id):
	gotwa = GOTWA.query.get(id)
	if gotwa:
		return jsonify({
			'id': gotwa.id, 
			'going': gotwa.going,
			'others': gotwa.others,
			'time': gotwa.time,
			'what': gotwa.what,
			'action': gotwa.action
		})
	else:
		return jsonify({'error': 'GOTWA not found'}), 404
	
class LACE(Report):
	__tablename__ = 'lace_reports'

	id = db.Column(db.Integer, db.ForeignKey('reports.id'), primary_key=True)
	liquids = db.Column(db.String(64))
	ammunition = db.Column(db.String(64))
	casualties = db.Column(db.String(64))
	equipment = db.Column(db.String(64))

	__mapper_args__ = {
		'polymorphic_identity': 'lace'
	}

@app.route('/lace_reports', methods=['GET'])
def get_lace_reports():
	lace_reports = LACE.query.all()
	return jsonify([{
		'id': lace.id, 
		'liquids': lace.liquids,
		'ammunition': lace.ammunition,
		'casualties': lace.casualties,
		'equipment': lace.equipment
	} for lace in lace_reports])

@app.route('/lace/<int:id>', methods=['GET'])
def get_lace(id):
	lace = LACE.query.get(id)
	if lace:
		return jsonify({
			'id': lace.id, 
			'liquids': lace.liquids,
			'ammunition': lace.ammunition,
			'casualties': lace.casualties,
			'equipment': lace.equipment
		})
	else:
		return jsonify({'error': 'LACE not found'}), 404
	
class SALTR(Report):
	__tablename__ = 'saltr_reports'
	id = db.Column(db.Integer, db.ForeignKey('reports.id'), primary_key=True)
	situation = db.Column(db.String(64))
	action = db.Column(db.String(64))
	location = db.Column(db.String(64))
	time = db.Column(db.String(64))
	reaction = db.Column(db.String(64))

	__mapper_args__ = {
		'polymorphic_identity': 'saltr'
	}

@app.route('/saltr_reports', methods=['GET'])
def get_saltr_reports():
	saltr_reports = SALTR.query.all()
	return jsonify([{
		'id': saltr.id, 
		'situation': saltr.situation,
		'action': saltr.action,
		'location': saltr.location,
		'time': saltr.time,
		'reaction': saltr.reaction
	} for saltr in saltr_reports])

@app.route('/saltr/<int:id>', methods=['GET'])
def get_saltr(id):
	saltr = SALTR.query.get(id)
	if saltr:
		return jsonify({
			'id': saltr.id, 
			'situation': saltr.situation,
			'action': saltr.action,
			'location': saltr.location,
			'time': saltr.time,
			'reaction': saltr.reaction
		})
	else:
		return jsonify({'error': 'SALTR not found'}), 404
	
class SALUTE(Report):
	__tablename__ = 'salute_reports'

	id = db.Column(db.Integer, db.ForeignKey('reports.id'), primary_key=True)
	size = db.Column(db.String(64))
	activity = db.Column(db.String(64))
	location = db.Column(db.String(64))
	uniforms = db.Column(db.String(64))
	time = db.Column(db.String(64))
	equipment = db.Column(db.String(64))

	__mapper_args__ = {
		'polymorphic_identity': 'salute'
	}

@app.route('/salute_reports', methods=['GET'])
def get_salute_reports():
	salute_reports = SALUTE.query.all()
	return jsonify([{
		'id': salute.id, 
		'size': salute.size,
		'activity': salute.activity,
		'location': salute.location,
		'uniforms': salute.uniforms,
		'time': salute.time,
		'equipment': salute.equipment
	} for salute in salute_reports])

@app.route('/salute/<int:id>', methods=['GET'])
def get_salute(id):
	salute = SALUTE.query.get(id)
	if salute:
		return jsonify({
			'id': salute.id, 
			'size': salute.size,
			'activity': salute.activity,
			'location': salute.location,
			'uniforms': salute.uniforms,
			'time': salute.time,
			'equipment': salute.equipment
		})
	else:
		return jsonify({'error': 'SALUTE not found'}), 404

class SAS(Report):
	__tablename__ = 'sas_reports'
	id = db.Column(db.Integer, db.ForeignKey('reports.id'), primary_key = True)

	losses = db.Column(db.Integer)
	ammunition = db.Column(db.Integer)
	equipment = db.Column(db.String(64))

	__mapper_args__ = {
		'polymorphic_identity': 'sas'
	}

@app.route('/sas_reports', methods=['GET'])
def get_sas_reports():
	sas_reports = SAS.query.all()
	return jsonify([{
		'id': sas.id, 
		'losses': sas.losses,
		'ammunition': sas.ammunition,
		'equipment': sas.equipment
	} for sas in sas_reports])

@app.route('/sas/<int:id>', methods=['GET'])
def get_sas(id):
	sas = SAS.query.get(id)
	if sas:
		return jsonify({
			'id': sas.id, 
			'losses': sas.losses,
			'ammunition': sas.ammunition,
			'equipment': sas.equipment
		})
	else:
		return jsonify({'error': 'SAS not found'}), 404
	
class SLLS(Report):
	__tablename__ = 'slls_reports'
	id = db.Column(db.Integer, db.ForeignKey('reports.id'), primary_key=True)
	stop = db.Column(db.String(64))
	listen = db.Column(db.String(64))
	look = db.Column(db.String(64))
	smell = db.Column(db.String(64))

	__mapper_args__ = {
		'polymorphic_identity': 'slls'
	}

@app.route('/slls_reports', methods=['GET'])
def get_slls_reports():
	slls_reports = SLLS.query.all()
	return jsonify([{
		'id': slls.id, 
		'stop': slls.stop,
		'listen': slls.listen,
		'look': slls.look,
		'smell': slls.smell
	} for slls in slls_reports])

@app.route('/slls/<int:id>', methods=['GET'])
def get_slls(id):
	slls = SLLS.query.get(id)
	if slls:
		return jsonify({
			'id': slls.id, 
			'stop': slls.stop,
			'listen': slls.listen,
			'look': slls.look,
			'smell': slls.smell
		})
	else:
		return jsonify({'error': 'SLLS not found'}), 404

@app.route('/')
def index():
    endpoints = {
        'points': url_for('get_points', _external=True),
        'point': url_for('get_point', id=1, _external=True),  # Example with id
        'allies': url_for('get_allies', _external=True),
        'ally': url_for('get_ally', id=1, _external=True),  # Example with id
        'enemies': url_for('get_enemies', _external=True),
        'enemy': url_for('get_enemy', id=1, _external=True),  # Example with id
        'evacuations': url_for('get_evacuations', _external=True),
        'evacuation': url_for('get_evacuation', id=1, _external=True),  # Example with id
        'reports': url_for('get_reports', _external=True),
        'report': url_for('get_report', id=1, _external=True),  # Example with id
        'gotwa_reports': url_for('get_gotwa_reports', _external=True),
        'gotwa': url_for('get_gotwa', id=1, _external=True),  # Example with id
        'lace_reports': url_for('get_lace_reports', _external=True),
        'lace': url_for('get_lace', id=1, _external=True),  # Example with id
        'saltr_reports': url_for('get_saltr_reports', _external=True),
        'saltr': url_for('get_saltr', id=1, _external=True),  # Example with id
        'salute_reports': url_for('get_salute_reports', _external=True),
        'salute': url_for('get_salute', id=1, _external=True),  # Example with id
        'sas_reports': url_for('get_sas_reports', _external=True),
        'sas': url_for('get_sas', id=1, _external=True),  # Example with id
        'slls_reports': url_for('get_slls_reports', _external=True),
        'slls': url_for('get_slls', id=1, _external=True)  # Example with id
    }
    html_links = ''.join([f'<a href="{url}">{name}</a><br>' for name, url in endpoints.items()])
    return html_links
	
if __name__ == '__main__':
	app.run(host='0.0.0.0')
	with app.app_context():
		...
		# Fetch and print all reports
		print("REPORT")
		reports = get_reports().get_json()
		print(reports)
		for r in reports:
			report = get_report(r['id'])
			print(report.get_json())

		# Fetch and print all points
		print("POINT")
		points = get_points().get_json()
		print(points)
		for p in points:
			point = get_point(p['id'])
			print(point.get_json())

		# Fetch and print all allies
		print("ALLY")
		allies = get_allies().get_json()
		print(allies)
		for a in allies:
			ally = get_ally(a['id'])
			print(ally.get_json())

		# Fetch and print all enemies
		print("ENEMY")
		enemies = get_enemies().get_json()
		print(enemies)
		for e in enemies:
			enemy = get_enemy(e['id'])
			print(enemy.get_json())

		# Fetch and print all evacuations
		print("EVACUATION")
		evacuations = get_evacuations().get_json()
		print(evacuations)
		for e in evacuations:
			evacuation = get_evacuation(e['id'])
			print(evacuation.get_json())

		# Fetch and print all GOTWA reports
		print("GOTWA")
		gotwa_reports = get_gotwa_reports().get_json()
		print(gotwa_reports)
		for g in gotwa_reports:
			gotwa = get_gotwa(g['id'])
			print(gotwa.get_json())

		# Fetch and print all LACE reports
		print("LACE")
		lace_reports = get_lace_reports().get_json()
		print(lace_reports)
		for l in lace_reports:
			lace = get_lace(l['id'])
			print(lace.get_json())

		# Fetch and print all SALTR reports
		print("SALTR")
		saltr_reports = get_saltr_reports().get_json()
		print(saltr_reports)
		for s in saltr_reports:
			saltr = get_saltr(s['id'])
			print(saltr.get_json())

		# Fetch and print all SALUTE reports
		print("SALUTE")
		salute_reports = get_salute_reports().get_json()
		print(salute_reports)
		for s in salute_reports:
			salute = get_salute(s['id'])
			print(salute.get_json())

		# Fetch and print all SAS reports
		print("SAS")
		sas_reports = get_sas_reports().get_json()
		print(sas_reports)
		for s in sas_reports:
			sas = get_sas(s['id'])
			print(sas.get_json())

		# Fetch and print all SLLS reports
		print("SLLS")
		slls_reports = get_slls_reports().get_json()
		print(slls_reports)
		for s in slls_reports:
			slls = get_slls(s['id'])
			print(slls.get_json())
