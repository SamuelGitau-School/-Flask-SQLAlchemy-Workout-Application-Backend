import os

from flask import Flask, make_response, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import *
from schemas import (
    workout_schema, workouts_schema,
    exercise_schema, exercises_schema,
    workout_exercise_schema,
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


def error(message, status, details=None):
    body = {'error': message}
    if details:
        body['details'] = details
    return make_response(body, status)


def get_or_404(model, record_id):
    return db.session.get(model, record_id)


# Error handlers

@app.errorhandler(ValidationError)
def handle_schema_error(e):
    return error('Validation failed', 422, e.messages)


@app.errorhandler(ValueError)
def handle_model_error(e):
    db.session.rollback()
    return error(str(e), 422)


@app.errorhandler(IntegrityError)
def handle_integrity_error(e):
    db.session.rollback()
    return error('Database constraint violated (duplicate or invalid data).', 409)


@app.errorhandler(404)
def handle_404(e):
    return error('Resource not found', 404)


#Routes

@app.route('/')
def index():
    return make_response({'message': 'Workout API'}, 200)


@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.order_by(Workout.date.desc()).all()
    return make_response(workouts_schema.dump(workouts), 200)


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = get_or_404(Workout, id)
    if not workout:
        return error(f'Workout {id} not found', 404)
    return make_response(workout_schema.dump(workout), 200)


@app.route('/workouts', methods=['POST'])
def create_workout():
    data = workout_schema.load(request.get_json(silent=True) or {})
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return make_response(workout_schema.dump(workout), 201)


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = get_or_404(Workout, id)
    if not workout:
        return error(f'Workout {id} not found', 404)
    db.session.delete(workout)  # cascades to WorkoutExercises
    db.session.commit()
    return make_response('', 204)


@app.route('/exercises', methods=['GET'])
def get_exercises():
    exercises = Exercise.query.order_by(Exercise.name).all()
    return make_response(exercises_schema.dump(exercises), 200)


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    exercise = get_or_404(Exercise, id)
    if not exercise:
        return error(f'Exercise {id} not found', 404)
    return make_response(exercise_schema.dump(exercise), 200)


@app.route('/exercises', methods=['POST'])
def create_exercise():
    data = exercise_schema.load(request.get_json(silent=True) or {})
    exercise = Exercise(**data)
    db.session.add(exercise)
    db.session.commit()
    return make_response(exercise_schema.dump(exercise), 201)


@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = get_or_404(Exercise, id)
    if not exercise:
        return error(f'Exercise {id} not found', 404)
    db.session.delete(exercise)  # cascades to WorkoutExercises
    db.session.commit()
    return make_response('', 204)


@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises', methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):
    workout = get_or_404(Workout, workout_id)
    if not workout:
        return error(f'Workout {workout_id} not found', 404)
    exercise = get_or_404(Exercise, exercise_id)
    if not exercise:
        return error(f'Exercise {exercise_id} not found', 404)

    data = workout_exercise_schema.load(request.get_json(silent=True) or {})
    workout_exercise = WorkoutExercise(workout=workout, exercise=exercise, **data)
    db.session.add(workout_exercise)
    db.session.commit()
    return make_response(workout_exercise_schema.dump(workout_exercise), 201)


if __name__ == '__main__':
    app.run(port=5555, debug=True)