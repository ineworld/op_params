from common.op_params import opParams
import time
import ast


class opEdit:  # use by running `python /data/openpilot/op_edit.py`
  def __init__(self):
    self.op_params = opParams()
    self.params = None
    self.sleep_time = 1.25
    self.run_loop()

  def run_loop(self):
    print('Welcome to the opParams command line editor!')
    print('Here are your parameters:\n')
    while True:
      self.params = self.op_params.get(force_update=True)
      values_list = [self.params[i] if len(str(self.params[i])) < 20 else '{} ... {}'.format(str(self.params[i])[:30], str(self.params[i])[-15:]) for i in self.params]
      live = [' (live!)' if i in self.op_params.default_params and 'live' in self.op_params.default_params[i] and self.op_params.default_params[i]['live'] else '' for i in self.params]

      to_print = ['{}. {}: {} {}'.format(idx + 1, i, values_list[idx], live[idx]) for idx, i in enumerate(self.params)]
      to_print.append('\n{}. Add new parameter!'.format(len(self.params) + 1))
      to_print.append('{}. Delete parameter!'.format(len(self.params) + 2))
      print('\n'.join(to_print))
      print('\nChoose a parameter to explore (by integer index): ')
      choice = input('>> ').strip()
      parsed, choice = self.parse_choice(choice)
      if parsed == 'continue':
        continue
      elif parsed == 'add':
        self.add_parameter()
      elif parsed == 'change':
        self.change_parameter(choice)
      elif parsed == 'delete':
        self.delete_parameter()
      elif parsed == 'error':
        return

  def parse_choice(self, choice):
    if choice.isdigit():
      choice = int(choice)
      choice -= 1
    elif choice == '':
      print('Exiting opEdit!')
      return 'error', choice
    else:
      self.message('Not an integer!')
      return 'retry', choice
    if choice not in range(0, len(self.params) + 2):  # three for add/delete parameter
      self.message('Not in range!')
      return 'continue', choice

    if choice == len(self.params):  # add new parameter
      return 'add', choice

    if choice == len(self.params) + 1:  # delete parameter
      return 'delete', choice

    return 'change', choice

  def change_parameter(self, choice):
    while True:
      chosen_key = list(self.params)[choice]
      has_description = False
      has_allowed_types = False
      live = False
      if chosen_key in self.op_params.default_params:
        has_description = 'description' in self.op_params.default_params[chosen_key]
        has_allowed_types = 'allowed_types' in self.op_params.default_params[chosen_key]
        live = 'live' in self.op_params.default_params[chosen_key] and self.op_params.default_params[chosen_key]['live']

      old_value = self.params[chosen_key]
      print('Chosen parameter: {}'.format(chosen_key))
      print('Current value: {} (type: {})'.format(old_value, str(type(old_value)).split("'")[1]))

      to_print = []
      if has_description:
        to_print.append('>>  Description: {}'.format(self.op_params.default_params[chosen_key]['description'].replace('\n', '\n     ')))
      if has_allowed_types:
        allowed_types = self.op_params.default_params[chosen_key]['allowed_types']
        to_print.append('>>  Allowed types: {}'.format(', '.join([str(i).split("'")[1] for i in allowed_types])))
      if live:
        to_print.append('>>  This parameter supports live tuning! Updates should take affect within 5 seconds.\n')
        to_print.append('Try out opTune! It\'s designed to help you live tune parameters quicker.')
        to_print.append('Just exit out of this and type: \'python op_tune.py\'')

      if to_print:
        print('\n{}\n'.format('\n'.join(to_print)))

      print('Enter your new value:')
      new_value = input('>> ').strip()
      if new_value == '':
        self.message('Exiting this parameter...')
        return

      status, new_value = self.parse_input(new_value)

      if not status:
        continue

      if has_allowed_types and not any([isinstance(new_value, typ) for typ in allowed_types]):
        self.message('The type of data you entered ({}) is not allowed with this parameter!'.format(str(type(new_value)).split("'")[1]))
        continue

      print('\nOld value: {} (type: {})'.format(old_value, str(type(old_value)).split("'")[1]))
      print('New value: {} (type: {})'.format(new_value, str(type(new_value)).split("'")[1]))
      print('Do you want to save this?')
      choice = input('[Y/n]: ').lower().strip()
      if choice == 'y':
        self.op_params.put(chosen_key, new_value)
        self.message('Saved!')
      else:
        self.message('Not saved!')
      return

  def parse_input(self, dat):
    try:
      dat = ast.literal_eval(dat)
    except:
      try:
        dat = ast.literal_eval('"{}"'.format(dat))
      except ValueError:
        self.message('Cannot parse input, please try again!')
        return False, dat
    return True, dat

  def delete_parameter(self):
    while True:
      print('Enter the name of the parameter to delete:')
      key = input('>> ').lower()
      status, key = self.parse_input(key)
      if key == '':
        return
      if not status:
        continue
      if not isinstance(key, str):
        self.message('Input must be a string!')
        continue
      if key not in self.params:
        self.message("Parameter doesn't exist!")
        continue

      value = self.params.get(key)
      print('Parameter name: {}'.format(key))
      print('Parameter value: {} (type: {})'.format(value, str(type(value)).split("'")[1]))
      print('Do you want to delete this?')

      choice = input('[Y/n]: ').lower().strip()
      if choice == 'y':
        self.op_params.delete(key)
        self.message('Deleted!')
      else:
        self.message('Not saved!')
      return

  def add_parameter(self):
    while True:
      print('Type the name of your new parameter:')
      key = input('>> ').strip()
      if key == '':
        return

      status, key = self.parse_input(key)

      if not status:
        continue
      if not isinstance(key, str):
        self.message('Input must be a string!')
        continue

      print("Enter the data you'd like to save with this parameter:")
      value = input('>> ').strip()
      status, value = self.parse_input(value)
      if not status:
        continue

      print('Parameter name: {}'.format(key))
      print('Parameter value: {} (type: {})'.format(value, str(type(value)).split("'")[1]))
      print('Do you want to save this?')

      choice = input('[Y/n]: ').lower().strip()
      if choice == 'y':
        self.op_params.put(key, value)
        self.message('Saved!')
      else:
        self.message('Not saved!')
      return

  def message(self, msg):
    print('--------\n{}\n--------'.format(msg), flush=True)
    time.sleep(self.sleep_time)
    print()


opEdit()
