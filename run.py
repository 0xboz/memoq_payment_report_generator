from datetime import datetime as dt
import logging
import ntpath
import os
import platform

RAT_PER_WORD = 0.08
DISCOUNT_100 = 0.9
DISCOUNT_95_99 = 0.7
DISCOUNT_85_94 = 0.5
DISCOUNT_75_84 = 0
DISCOUNT_50_74 = 0

DATA_DIR = './data'
REPORT_DIR = './report'

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)


def creation_date(path_to_file):  # https://stackoverflow.com/a/39501288/11461544
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def get_stats():
    """
    Fetch project code, name and stats from a directory.
    Remove all duplicates.
    Calculate the fees.
    :Return: 
        2 Python Dictionaries
        One is all projects' stats, the other is monthly projects' stats
    """

    all_stats = {
        'Total Fee': 0,
        'Total': 0,
        'Effective Rate Per Word': 0,
    }

    monthly_stats = {}

    # https://stackoverflow.com/a/3964691/11461544

    try:
        for file in os.listdir(DATA_DIR):
            with open(os.path.join(DATA_DIR, file), 'r') as f:
                epoch = creation_date(os.path.join(DATA_DIR, file))
                date = dt.fromtimestamp(epoch)

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
                            '75% ~ 84% Fee': int(info[51]) * RAT_PER_WORD * (1 - DISCOUNT_75_84),
                            '50% ~ 74%': int(info[59]),
                            '50% ~ 74% Fee': int(info[59]) * RAT_PER_WORD * (1 - DISCOUNT_50_74),
                            'No Match': int(info[67]),
                            'No Match Fee': int(info[67]) * RAT_PER_WORD,
                            'Fragments': int(info[75]),
                            'Total': int(info[83]),
                            'Total Fee': RAT_PER_WORD * ((int(info[3]) + int(info[11]) + int(info[19]) + int(info[27])) * (1 - DISCOUNT_100) + int(info[35]) * (1 - DISCOUNT_95_99) + int(info[43]) * (1 - DISCOUNT_85_94) + int(info[51]) * (1 - DISCOUNT_75_84) + int(info[59]) * (1 - DISCOUNT_50_74) + int(info[67])),
                            'Effective Rate Per Word': RAT_PER_WORD * ((int(info[3]) + int(info[11]) + int(info[19]) + int(info[27])) * (1 - DISCOUNT_100) + int(info[35]) * (1 - DISCOUNT_95_99) + int(info[43]) * (1 - DISCOUNT_85_94) + int(info[51]) * (1 - DISCOUNT_75_84) + int(info[59]) * (1 - DISCOUNT_50_74) + int(info[67])) / int(info[83]),
                        }

                        project = {
                            'name': name,
                            'stats': stats,
                            'date': date,
                        }

                        for e in ntpath.dirname(path).replace('\\', ' ').split():
                            if 'E00' in e:
                                code = e
                                break

                        # Create all projects' stats - all_stats
                        if all_stats.get(code):
                            all_stats[code].append(project)
                        else:
                            all_stats[code] = [project, ]
                            all_stats[f'{code} Total Fee'] = 0
                            all_stats[f'{code} Total'] = 0
                            all_stats[f'{code} Effective Rate Per Word'] = 0

                        # Remove duplicates in all_stats
                        # https://stackoverflow.com/a/11092590/11461544
                        all_stats[code] = list(
                            {v['name']: v for v in all_stats[code]}.values())

                        # Create monthly projects' stats - monthly_stats
                        year_month = date.strftime('%Y%m')
                        if monthly_stats.get(year_month):
                            if monthly_stats[year_month].get(code):
                                monthly_stats[year_month][code].append(project)
                            else:
                                monthly_stats[year_month][code] = [project, ]
                                monthly_stats[year_month][f'{code} Total Fee'] = 0
                                monthly_stats[year_month][f'{code} Total'] = 0
                                monthly_stats[year_month][f'{code} Effective Rate Per Word'] = 0

                        else:
                            monthly_stats[year_month] = {}
                            monthly_stats[year_month][code] = [project, ]
                            monthly_stats[year_month][f'{code} Total Fee'] = 0
                            monthly_stats[year_month][f'{code} Total'] = 0
                            monthly_stats[year_month][f'{code} Effective Rate Per Word'] = 0

                        # Remove duplicates in monthly_stats
                        # https://stackoverflow.com/a/11092590/11461544
                        monthly_stats[year_month][code] = list(
                            {v['name']: v for v in all_stats[code]}.values())

    except FileNotFoundError as e:
        logger.critical(
            'Download csv files first and save them to `data/` directory.')
        exit(1)

    # Calculate extra metrics in all_stats
    # Such as `Total Fee`, `Total`, `Effective Rate Per Word` for each project code (E00XXX) and all projects
    for key in all_stats.keys():
        if isinstance(all_stats[key], list):
            for project in all_stats[key]:
                all_stats[f'{key} Total Fee'] += project['stats']['Total Fee']
                all_stats[f'{key} Total'] += project['stats']['Total']

                all_stats['Total Fee'] += project['stats']['Total Fee']
                all_stats['Total'] += project['stats']['Total']

            all_stats[f'{key} Effective Rate Per Word'] = all_stats[f'{key} Total Fee'] / \
                all_stats[f'{key} Total']

    all_stats['Effective Rate Per Word'] = all_stats['Total Fee'] / \
        all_stats['Total']

    # Calculate extra metrics in monthly_stats
    # Such as monthly-based `Total Fee`, `Total`, `Effective Rate Per Word` for each project code (E00XXX) and all projects
    for month in monthly_stats.keys():
        monthly_stats[month]['Total Fee'] = 0
        monthly_stats[month]['Total'] = 0
        monthly_stats[month]['Effective Rate Per Word'] = 0

        for code in monthly_stats[month]:
            if isinstance(monthly_stats[month][code], list):
                for project in monthly_stats[month][code]:

                    monthly_stats[month][f'{code} Total Fee'] += project['stats']['Total Fee']
                    monthly_stats[month][f'{code} Total'] += project['stats']['Total']
                    monthly_stats[month][f'{code} Effective Rate Per Word'] = monthly_stats[
                        month][f'{code} Total Fee'] / monthly_stats[month][f'{code} Total']

                    monthly_stats[month]['Total Fee'] += project['stats']['Total Fee']
                    monthly_stats[month]['Total'] += project['stats']['Total']

        monthly_stats[month]['Effective Rate Per Word'] = monthly_stats[month]['Total Fee'] / \
            monthly_stats[month]['Total']

    return all_stats, monthly_stats


def convert(monthly_stats):
    """
    Convert monthly stats to all stats
    """
    all_stats = {}

    for stats in monthly_stats.values():        
        all_stats.update(stats)

    return all_stats


def create_report(stats):
    """
    Generate a report for all compoleted projects.
    :param stats
        Python Dictionary
        {
            'Total Fee': ,
            'Total': ,
            'Effective Rate Per Word': ,
            'E00XX1 Effective Rate Per Word': ,
            'E00XX1 Total Fee': , 
            'E00XX1': [
                {
                    'date': ,
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

    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

    with open(os.path.join(REPORT_DIR, 'report.csv'), 'w') as f:
        f.write('Effective Rate Per Word,{}\n'.format(
            stats['Effective Rate Per Word']))
        f.write('Total Fee,{}\n'.format(stats['Total Fee']))
        f.write('Total,{}\n\n\n'.format(stats['Total']))

        for key in stats.keys():
            if isinstance(stats[key], list):
                f.write('{} Effective Rate Per Word,{}\n'.format(
                    key, stats[f'{key} Effective Rate Per Word']))
                f.write('{} Total Fee,{}\n'.format(
                    key, stats[f'{key} Total Fee']))
                f.write('{} Total,{}\n'.format(key, stats[f'{key} Total']))
                f.write('{} Details,'.format(key) + 'X-translated,X-translated Fee,101%,101% Fee,Repetitions,Repetitions Fee,100%,100% Fee,95% ~ 99%,95% ~ 99% Fee,85% ~ 94%,85% ~ 94% Fee,75% ~ 84%,75% ~ 84% Fee,50% ~ 74%,50% ~ 74% Fee,No Match,No Match Fee,Fragments,Total,Total Fee,Effective Rate Per Word\n')

                for project in stats[key]:
                    f.write(project['name'] + ',' + ','.join([str(e)
                                                              for e in project['stats'].values()]) + '\n')

                f.write('\n\n')


def create_monthly_report(stats):
    """
    Generate monthly reports for all compoleted projects.
    :param stats
        Python Dictionary
        {
            '202005': {
                'Total Fee': ,
                'Total': ,
                'Effective Rate Per Word': ,
                'E00XX1 Effective Rate Per Word': ,
                'E00XX1 Total Fee': , 
                'E00XX1': [
                    {
                        'date': ,
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
        }
    """

    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

    for year_month in stats.keys():
        year_month_dir = os.path.join(REPORT_DIR, year_month)

        if not os.path.exists(year_month_dir):
            os.makedirs(year_month_dir)

        if len(os.listdir(year_month_dir)) != 0:
            print('existing report ! update report?')
            exit(0)
        else:
            with open(os.path.join(year_month_dir, f'report{year_month}.csv'), 'w') as f:
                f.write('{} Monthly Report,\n'.format(year_month))
                f.write('Effective Rate Per Word,{}\n'.format(
                    stats[year_month]['Effective Rate Per Word']))
                f.write('Total Fee,{}\n'.format(
                    stats[year_month]['Total Fee']))
                f.write('Total,{}\n\n\n'.format(stats[year_month]['Total']))

                for key in stats[year_month].keys():
                    if isinstance(stats[year_month][key], list):
                        f.write('{} Effective Rate Per Word,{}\n'.format(
                            key, stats[year_month][f'{key} Effective Rate Per Word']))
                        f.write('{} Total Fee,{}\n'.format(
                            key, stats[year_month][f'{key} Total Fee']))
                        f.write('{} Total,{}\n'.format(
                            key, stats[year_month][f'{key} Total']))
                        f.write('{} Details,'.format(key) + 'X-translated,X-translated Fee,101%,101% Fee,Repetitions,Repetitions Fee,100%,100% Fee,95% ~ 99%,95% ~ 99% Fee,85% ~ 94%,85% ~ 94% Fee,75% ~ 84%,75% ~ 84% Fee,50% ~ 74%,50% ~ 74% Fee,No Match,No Match Fee,Fragments,Total,Total Fee,Effective Rate Per Word\n')

                        for project in stats[year_month][key]:
                            f.write(project['name'] + ',' + ','.join([str(e)
                                                                      for e in project['stats'].values()]) + '\n')

                        f.write('\n\n')


if __name__ == "__main__":

    all_projects_stats, projects_stats_by_month = get_stats()
    create_report(all_projects_stats)
    create_monthly_report(projects_stats_by_month)
