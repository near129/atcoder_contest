import sys
import pathlib
import requests
from bs4 import BeautifulSoup

PYTEST_TEMPLATE = [
    'import pytest',
    'import subprocess',
    '',
    '',
    '@pytest.mark.parametrize(',
    '    "IN, OUT", [',
    '    ]',
    ')',
    'def test_1(IN, OUT):',
    '    cp = subprocess.run(["python", "Main.py"], encoding="utf-8", ',
    '                        input=IN, stdout=subprocess.PIPE)',
    '    assert cp.stdout == OUT',
    ''
]


def get_contest_info(contest_name):
    contest_info = {'name': contest_name}
    # atcoderから印刷用問題のページを取得
    url = f'https://atcoder.jp/contests/{contest_name}/tasks_print'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    # 解析
    problems = soup.select('.col-sm-12')[::2]
    contest_num = len(list(problems))
    contest_info['contest_num'] = contest_num
    contest_info.update({chr(97+i): [] for i in range(contest_num)})
    problems = soup.select('#task-statement > span > span.lang-ja')
    for n, problem in enumerate(problems):
        examples = problem.select('div')[5:]
        for i, o in zip(examples[0::2], examples[1::2]):
            contest_info[chr(97+n)].append((i.pre.text, o.pre.text))

    return contest_info


def make_test_file_directory(contest_info):
    contest_name = contest_info['name']
    pathlib.Path(contest_name).mkdir()
    for i in range(contest_info['contest_num']):
        directory = f'{contest_name}/{chr(97+i)}'
        pathlib.Path(directory).mkdir(
            parents=True)
        param = [f'{" "*8}("""{i}""", """{o}""")' for i, o in contest_info[chr(97+i)]]
        param = ',\n'.join(param)
        with open(directory + f'/test_{chr(97+i)}.py', 'w') as f:
            f.write('\n'.join(PYTEST_TEMPLATE[:6] + [param] +
                              PYTEST_TEMPLATE[6:]))
        pathlib.Path('Main.py').touch()


def main():
    contest_name = sys.argv[1]
    contest_info = get_contest_info(contest_name)
    make_test_file_directory(contest_info)


if __name__ == '__main__':
    main()
