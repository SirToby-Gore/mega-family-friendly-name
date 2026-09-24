import os
from sys import argv

path = './'

if len(argv) == 2:
    path = argv[1]


def explore_dir(path: str):
    for item in os.listdir(path):
        if os.path.isdir(f'{path}/{item}'):
            explore_dir(f'{path}/{item}')
        else:
            try:
                with open(f'{path}/{item}', 'r') as file:
                    file.read()
            except:
                continue

            print(f'```{path}/{item}')
            with open(f'{path}/{item}', 'r') as file:
                print(file.read())
            print(f'```')


explore_dir(path)
