#!/usr/bin/env python3

from datetime import date

from app import app
from models import *

with app.app_context():

    print('Clearing existing data...')
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    print('Creating exercises...')
    squat = Exercise(name='Barbell Squat', category='Strength', equipment_needed=True)
    pushup = Exercise(name='Push-up', category='Strength', equipment_needed=False)
    plank = Exercise(name='Plank', category='Core', equipment_needed=False)
    row = Exercise(name='Rowing Machine', category='Cardio', equipment_needed=True)
    db.session.add_all([squat, pushup, plank, row])

    print('Creating workouts...')
    w1 = Workout(date=date(2025, 1, 6), duration_minutes=45, notes='Lower body focus')
    w2 = Workout(date=date(2025, 1, 8), duration_minutes=30, notes='Quick core and cardio')
    w3 = Workout(date=date(2025, 1, 10), duration_minutes=60, notes='Full body')
    db.session.add_all([w1, w2, w3])

    print('Linking exercises to workouts...')
    db.session.add_all([
        WorkoutExercise(workout=w1, exercise=squat, reps=8, sets=4),
        WorkoutExercise(workout=w1, exercise=plank, duration_seconds=60, sets=3),
        WorkoutExercise(workout=w2, exercise=plank, duration_seconds=90, sets=2),
        WorkoutExercise(workout=w2, exercise=row, duration_seconds=600),
        WorkoutExercise(workout=w3, exercise=squat, reps=10, sets=3),
        WorkoutExercise(workout=w3, exercise=pushup, reps=15, sets=3),
        WorkoutExercise(workout=w3, exercise=row, duration_seconds=900),
    ])

    db.session.commit()
    print('Done seeding!')