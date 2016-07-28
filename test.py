import sys
import subprocess
import ast
def obtain_view(entity, date, debug=False):
    """

    >>> obtain_view('France', '2015-07-01')
    8920

    """
    result = 0

    for element, replace in [('(', '\('),
                             (')', '\)'),
                             ('&', '\&'),
                             ("'", "")]:
        entity = entity.replace(element, replace)

    date_for_command = date.replace('-', '')
    command = 'node get_views.js {entity} {date_for_command} {date_for_command}'.format(
        **locals())

    try:
        output = subprocess.check_output(command, shell=True)
        output = output.decode('utf-8')
        views = ast.literal_eval(output)
    except subprocess.CalledProcessError:
        print('ERROR', command)
        views = {}

    if date in views:
        result = sum(views.values())

    if debug:
        print()
        print(command)
        print(result)
        input('continue?')

    return result

print(obtain_view(sys.argv[1], '2008-01-01'))
