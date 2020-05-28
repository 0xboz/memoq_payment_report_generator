import ntpath
import os

RAT_PER_WORD = 0.08
DISCOUNT_100 = 0.9
DISCOUNT_95_99 = 0.7
DISCOUNT_85_94 = 0.5

DATA_DIR = './data'
REPORT_DIR = './report'
PROJECTS = {
    'Total Fee': 0,
    'Total': 0,
    'Effective Rate Per Word': 0,
}


def get_stats():
    """
    Fetch project code, name and stats from a directory.
    Remove all duplicates.
    Calculate the fees
    return: Python Dictionary
        {
            'Total Fee': ,
            'Total': ,
            'Effective Rate Per Word': ,
            'E00XX1 Effective Rate Per Word': ,
            'E00XX1 Total Fee': , 
            'E00XX1': [
                {
                    'name': 'project 1',
                    'stats': {
                        'X-translated': ,
                        'X-translated Fee': ,
                        '101%': ,
                        '101% Fee': ,
                        'Repetitions': ,
                        'Repetitions Fee': ,
                        '100%': ,
                        '100% Fee': ,
                        '95% ~ 99%': ,
                        '95% ~ 99% Fee': ,
                        '85% ~ 94%': ,
                        '85% ~ 94% Fee': ,
                        '75% ~ 84%': ,
                        '75% ~ 84% Fee': ,
                        '50% ~ 74%': ,
                        '50% ~ 74% Fee': ,
                        'No Match': ,
                        'No Match Fee': ,
                        'Fragments': ,
                        'Total': ,
                        'Total Fee': ,
                        'Effective Rate Per Word': ,
                    },
                },
                {
                    'name': 'project 2',
                    'stats': {...},
                },
                ...
            ],
            'E00XX2': [
                ...
            ],
            ...
        }

    """

    # https://stackoverflow.com/a/3964691/11461544
    for file in os.listdir(DATA_DIR):
        with open(os.path.join(DATA_DIR, file), 'r') as f:
            for index, line in enumerate(f.readlines()):

                if index == 2:

                    info = line.split(';')

                    # Get project code and name
                    path = info[0].replace('"', '')
                    # https://stackoverflow.com/a/8384788/11461544
                    name = ntpath.basename(path).replace(',', '')

                    stats = {
                        'X-translated': int(info[3]),
                        'X-translated Fee': int(info[3]) * RAT_PER_WORD * (1 - DISCOUNT_100),
                        '101%': int(info[11]),
                        '101% Fee': int(info[11]) * RAT_PER_WORD * (1 - DISCOUNT_100),
                        'Repetitions': int(info[19]),
                        'Repetitions Fee': int(info[19]) * RAT_PER_WORD * (1 - DISCOUNT_100),
                        '100%': int(info[27]),
                        '100% Fee': int(info[27]) * RAT_PER_WORD * (1 - DISCOUNT_100),
                        '95% ~ 99%': int(info[35]),
                        '95% ~ 99% Fee': int(info[35]) * RAT_PER_WORD * (1 - DISCOUNT_95_99),
                        '85% ~ 94%': int(info[43]),
                        '85% ~ 94% Fee': int(info[43]) * RAT_PER_WORD * (1 - DISCOUNT_85_94),
                        '75% ~ 84%': int(info[51]),
                        '75% ~ 84% Fee': int(info[51]) * RAT_PER_WORD,
                        '50% ~ 74%': int(info[59]),
                        '50% ~ 74% Fee': int(info[59]) * RAT_PER_WORD,
                        'No Match': int(info[67]),
                        'No Match Fee': int(info[67]) * RAT_PER_WORD,
                        'Fragments': int(info[75]),
                        'Total': int(info[83]),
                        'Total Fee': RAT_PER_WORD * ((int(info[3]) + int(info[11]) + int(info[19]) + int(info[27])) * (1 - DISCOUNT_100) + int(info[35]) * (1 - DISCOUNT_95_99) + int(info[43]) * (1 - DISCOUNT_85_94) + int(info[51]) + int(info[59]) + int(info[67])),
                        'Effective Rate Per Word': RAT_PER_WORD * ((int(info[3]) + int(info[11]) + int(info[19]) + int(info[27])) * (1 - DISCOUNT_100) + int(info[35]) * (1 - DISCOUNT_95_99) + int(info[43]) * (1 - DISCOUNT_85_94) + int(info[51]) + int(info[59]) + int(info[67])) / int(info[83]),
                    }

                    project = {
                        'name': name,
                        'stats': stats,
                    }

                    for e in ntpath.dirname(path).replace('\\', ' ').split():
                        if 'E00' in e:
                            code = e
                            break

                    if PROJECTS.get(code):
                        PROJECTS[code].append(project)
                    else:
                        PROJECTS[code] = [project, ]
                        PROJECTS[f'{code} Total Fee'] = 0
                        PROJECTS[f'{code} Total'] = 0
                        PROJECTS[f'{code} Effective Rate Per Word'] = 0

                    # Remove duplicates
                    # https://stackoverflow.com/a/11092590/11461544
                    PROJECTS[code] = list(
                        {v['name']: v for v in PROJECTS[code]}.values())

    # Calculate total fee and effective rate per word
    for key in PROJECTS.keys():
        if isinstance(PROJECTS[key], list):
            for project in PROJECTS[key]:
                PROJECTS[f'{key} Total Fee'] += project['stats']['Total Fee']
                PROJECTS[f'{key} Total'] += project['stats']['Total']

                PROJECTS['Total Fee'] += project['stats']['Total Fee']
                PROJECTS['Total'] += project['stats']['Total']

            PROJECTS[f'{key} Effective Rate Per Word'] = PROJECTS[f'{key} Total Fee'] / \
                PROJECTS[f'{key} Total']

    PROJECTS['Effective Rate Per Word'] = PROJECTS['Total Fee'] / \
        PROJECTS['Total']


def create_report():
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

    with open(os.path.join(REPORT_DIR, 'report.csv'), 'w') as f:
        f.write('Effective Rate Per Word,{}\n'.format(
            PROJECTS['Effective Rate Per Word']))
        f.write('Total Fee,{}\n'.format(PROJECTS['Total Fee']))
        f.write('Total,{}\n\n\n'.format(PROJECTS['Total']))

        for key in PROJECTS.keys():
            if isinstance(PROJECTS[key], list):
                f.write('{} Effective Rate Per Word,{}\n'.format(
                    key, PROJECTS[f'{key} Effective Rate Per Word']))
                f.write('{} Total Fee,{}\n'.format(
                    key, PROJECTS[f'{key} Total Fee']))
                f.write('{} Total,{}\n'.format(key, PROJECTS[f'{key} Total']))
                f.write('{} Details,'.format(key) + 'X-translated,X-translated Fee,101%,101% Fee,Repetitions,Repetitions Fee,100%,100% Fee,95% ~ 99%,95% ~ 99% Fee,85% ~ 94%,85% ~ 94% Fee,75% ~ 84%,75% ~ 84% Fee,50% ~ 74%,50% ~ 74% Fee,No Match,No Match Fee,Fragments,Total,Total Fee,Effective Rate Per Word\n')

                for project in PROJECTS[key]:
                    f.write(project['name'] + ',' + ','.join([str(e)
                                                              for e in project['stats'].values()]) + '\n')

                f.write('\n\n')


if __name__ == "__main__":
    get_stats()
    create_report()
