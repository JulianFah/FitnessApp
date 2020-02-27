import os, sys, pickle, datetime

# Prevent kivy from using arguments by saving and overriding them
ARGUMENTS = sys.argv
sys.argv = sys.argv[:1]

# Deactivate kivy console logging
os.environ['KIVY_NO_CONSOLELOG'] = '1'

# Import kivy modules
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
BACKUP_PATH = (DIR_PATH + 
    f'/backups/{datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.pickle')
MAIN_STORE_PATH = DIR_PATH + '/store.pickle'
VALID_ARGUMENTS = ['--help', '-upper', '-lower', '-push', '-pull', '-leg']

UPPER_EXERCISES = [
    'Bench Press', 
    'Chest Supported Row',
    'Overhead Press',
    'Lat Pulldown',
    'Hight To Low Cable Flies',
    'Lying Face Pulls',
    ]
LOWER_EXERCISES = [
    'Front Squad',
    'Deadlift',
    'Barbell Hip Thrust',
    'Single Leg Weighted Calf Raise',
    'Leg Press Calf Raise'
]
PUSH_EXERCISES = [
    'Incline Dumbbell Press',
    'Flat Dumbbell Press',
    'Lateral Raises',
    'Banded Push Ups',
    'Overhead Rope Extensions',
    'Bar Triceps Pushdowns'
]
PULL_EXERCISES = [
    'Weighted Pull Ups',
    'Seated Row',
    'Reverse Pec Dec',
    'Kneeling Face Pulls',
    'Incline Dumbbell Curls',
    'Hammer Curls',
    'Scapular Pull Ups'
]
LEG_EXERCISES = [
    'Back Squad',
    'Bulgarian Split Squad',
    'Glute Ham Raise',
    'Smith Machine Calf Raises',
    'Seated Weighted Calf Raise'
]
EXERCISES_FOR_ARGUMENT = {
    '-upper': UPPER_EXERCISES,
    '-lower': LOWER_EXERCISES,
    '-push':  PUSH_EXERCISES,
    '-pull':  PULL_EXERCISES,
    '-leg':   LEG_EXERCISES
}


class DataHandler:
    def __init__(self, main_filename, backup_filename):
        self.main_filename = main_filename
        self.backup_filename = backup_filename

    def save_object(self, object):
        with open(self.main_filename, mode='wb') as output:
            pickle.dump(object, output, pickle.HIGHEST_PROTOCOL)

    def make_backup_of_object(self, object):
        # Check if the folder and backup file exist, else create them
        if (not os.path.exists(self.backup_filename) and 
            not os.path.exists(os.path.dirname(self.backup_filename))):
                os.mkdir(os.path.dirname(self.backup_filename))
        
        with open(self.backup_filename, mode='wb') as backup:
            pickle.dump(object, backup, pickle.HIGHEST_PROTOCOL)

    def load_object(self):
        with open(self.main_filename, mode='rb') as input:
            return pickle.load(input)


class Exercise:
    def __init__(self, name, set_count=None, weights=None, 
                 reps=None, next_time_decision=None):
        self.name = name
        self.set_count = set_count
        self.weights = weights
        self.reps = reps
        self.next_time_decision = next_time_decision

    def __eq__(self, obj):
        if not isinstance(obj, Exercise):
            return NotImplemented
        
        return (self.name == obj.name and 
                self.set_count == obj.set_count and
                self.weights == obj.weights and 
                self.reps == obj.reps and
                self.next_time_decision == obj.next_time_decision)

    def __str__(self):
        string = ''
        string += f'Name:       {self.name}\n'
        string += f'Weights:    {self.weights}\n'
        string += f'Reps:       {self.reps}\n'
        string += f'Next time:  {self.next_time_decision}\n'
        return string

    def clone(self):
        return Exercise(self.name, self.set_count, self.weights,
            self.reps, self.next_time_decision)


class Workout:
    def __init__(self, exercise_names):
        self.exercises = []
        for name in exercise_names:
            self.add_exercise(Exercise(name=name))

    def __eq__(self, obj):
        if not isinstance(obj, Workout):
            return NotImplemented
        
        for idx in range(len(self.exercises)):
            if not self.exercises[idx] == obj.exercises[idx]:
                return False

        return True

    def __str__(self):
        string = '\n____________WORKOUT_______________\n'
        for exercise in self.exercises:
            string += exercise.__str__() + '\n'
        return string

    def add_exercise(self, exercise):
        self.exercises.append(exercise)

    def get_exercise(self, exercise_name):
        for exercise in self.exercises:
            if exercise.name == exercise_name:
                return exercise
        else:
            return -1

    def remove_exercise(self, exercise_to_rm):
        for exercise in self.exercises:
            if exercise == exercise_to_rm:
                self.exercises.remove(exercise)

    def replace_exercise(self, old_exercise_name, new_exercise):
        for index, exercise in enumerate(self.exercises):
            if exercise.name == old_exercise_name:
                self.exercises[index] = new_exercise

    def get_exercise_names(self):
        names = []
        for exercise in self.exercises:
            names.append(exercise.name)
        return names


class GUI(GridLayout):
    def __init__(self, app, workout, **kwargs):
        super().__init__(**kwargs)

        self.app = app
        self.workout = workout
        self.exercise_names = workout.get_exercise_names()
        self.current_exercise = workout.exercises[0]

        # Build up the GUI itself
        self.cols = 1
        self._build_exercise_heading()
        self._build_exercise_grid()
        self._build_next_time_decision_grid()
        self._build_submit_button()


    def _build_exercise_heading(self):
        ''' Sets up the header label with the current exercises name
            at the top of the window. SHould be called in constructor '''
        self.exercise_label = Label(
            text=self.current_exercise.name, font_size=45)
        self.add_widget(self.exercise_label)

    def _build_exercise_grid(self):
        ''' Sets up the weight and rep input fields for the GUI using
            an inner GridLayout. Should be called in constructor '''
        self.exercise_input_grid = GridLayout()
        self.exercise_input_grid.cols = 5
        def _add(widget):
            ''' Shorter version to add a widget to the inner GridLayout '''
            self.exercise_input_grid.add_widget(widget)

        self.weight_inputs = [
            TextInput(multiline=False),
            TextInput(multiline=False),
            TextInput(multiline=False),
            TextInput(multiline=False)
        ]
        self.reps_inputs = [
            TextInput(multiline=False),
            TextInput(multiline=False),
            TextInput(multiline=False),
            TextInput(multiline=False)
        ]

        # Add all weight and rep inputs to the inner GridLayout
        for i in range(4):
            _add(Label(text=f'Set {i + 1}'))
            _add(Label(text='Weight'))
            _add(self.weight_inputs[i])
            _add(Label(text='Reps'))
            _add(self.reps_inputs[i])

        # Add the inner GridLayout to the whole GUI
        self.add_widget(self.exercise_input_grid)

    def _build_next_time_decision_grid(self):
        ''' Sets up 3 Checkboxes at the bottom of the Window using an 
            inner GridLayout. Should be called in constructor '''        
        self.next_time_grid = GridLayout()
        self.next_time_grid.cols = 6
        def _add(widget):
            ''' Shorter version to add widget to the inner GridLayout '''
            self.next_time_grid.add_widget(widget)

        self.next_time_decision_checkboxes = [
            CheckBox(), CheckBox(), CheckBox()
        ]

        def _on_checkbox_ticked(checkbox, value):
            ''' Should be called when a checkbox is ticked. Checks for which
                one it was and updates next time decision accordingly. '''
            if not value:
                self.next_time_decision = None
                return
            
            for idx, box in enumerate(self.next_time_decision_checkboxes):
                if box == checkbox:
                    self.next_time_decision = ['more', 'same', 'less'][idx]
                else:
                    # Uncheck all other boxes
                    box.active = False

        # Add checkboxes and their labels to the inner GridLayout
        for idx, checkbox in enumerate(self.next_time_decision_checkboxes):
            checkbox.bind(active=_on_checkbox_ticked)
            _add(checkbox)
            _add(Label(text=['more', 'same', 'less'][idx]))

        # Add the header label and the inner GridLayout to the GUI
        self.add_widget(Label(text='Weight to choose next time:'))
        self.add_widget(self.next_time_grid)

    def _build_submit_button(self):
        ''' Sets up the submit button at the bottom of the window.
            Should be called in constructor. '''
        self.submit_button = Button(text='SUBMIT', font_size= 25)
        self.submit_button.bind(on_press=self._submit)
        self.add_widget(self.submit_button)

    def _submit(self, instance):
        ''' Transfers the data that the user entered to the current exercise
            and adds that exercise to the workout. Validates data before. '''
        if not self._is_input_valid():
            return -1
        
        self.current_exercise.set_count = self._get_set_count()
        self.current_exercise.weights   = self._get_weights()[:self._get_set_count()]
        self.current_exercise.reps      = self._get_reps()[:self._get_set_count()]
        self.current_exercise.next_time_decision = self.next_time_decision

        # Set up GUI for next exercise
        self._clear_input()
        idx = self.exercise_names.index(self.current_exercise.name) + 1
        try:
            self.current_exercise = self.workout.exercises[idx]
        except IndexError:
            # All exercises have been handled
            self.app.shutdown()
        
        self.exercise_label.text = self.current_exercise.name
        
    def _is_input_valid(self):
        return not (self._get_set_count() == 0 or self.next_time_decision == None)

    def _clear_input(self):
        for input in self.weight_inputs:
            input.text = ''
        for input in self.reps_inputs:
            input.text = ''

        for checkbox in self.next_time_decision_checkboxes:
            checkbox.active = False

    def _get_set_count(self):
        count = 0
        for idx in range(4):
            if self.weight_inputs[idx].text != '' and self.reps_inputs[idx] != '':
                count += 1
        return count

    def _get_weights(self):
        return [input.text for input in self.weight_inputs]

    def _get_reps(self):
        return [input.text for input in self.reps_inputs]


class Application(App):
    def __init__(self, data_handler, current_workout):
        self.workouts = []
        self.data_handler = data_handler
        self.current_workout = current_workout
        super().__init__()

    def build(self):
        return GUI(self, self.current_workout)

    def setup(self):
        self._load_stored_workouts()
        return self
    
    def shutdown(self):
        self.workouts.append(self.current_workout)
        self.data_handler.save_object(self.workouts)
        self.data_handler.make_backup_of_object(self.workouts)

        for workout in self.workouts:
            print(workout)

        sys.exit(1)

    def _load_stored_workouts(self):
        try:
            self.workouts.extend(self.data_handler.load_object())
        except:
            open(MAIN_STORE_PATH, mode='w+').close()     # Create the file for next time
            print(f'[INFO] Failed to load workouts from file {MAIN_STORE_PATH}')
            print(f'[INFO] Creating empty file {MAIN_STORE_PATH}')
            self.workouts = []

    def _restore_data(self, *args):
        for pickle_file in args:
            restore_handler = DataHandler(pickle_file, None)
            restored_workouts = restore_handler.load_object()
            self.workouts.extend(restored_workouts)


def print_help():
    print('Valid arguments:')
    print('--help    See this info page')
    print('-upper    Upper body workout documentation')
    print('-lower    Lower body workout documentation')
    print('-push     Push workout documentation')
    print('-pull     Pull workout documentation')
    print('-leg      Leg workout documentation')

def print_invalid_arguments():
    print('Invalid arguments!')
    print('Use --help for more details!')


def main(arg1):
    data_handler = DataHandler(MAIN_STORE_PATH, BACKUP_PATH)
    current_workout = Workout(EXERCISES_FOR_ARGUMENT[arg1])

    Application(data_handler, current_workout).setup().run()


if __name__ == '__main__':
    if len(ARGUMENTS) != 2 or ARGUMENTS[1] not in VALID_ARGUMENTS:
        print_invalid_arguments()
        sys.exit(-1)
    elif ARGUMENTS[1] == '--help':
        print_help()
        sys.exit(1)
    else:
        main(ARGUMENTS[1])
        