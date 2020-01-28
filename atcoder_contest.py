import sys
import os
import pathlib
import pickle
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
ATCODER_URL = 'https://atcoder.jp/'
CONTEST_INFO = {}
PATH = os.path.dirname(__file__)


def login():
    login_data = {
        'username': input('username: '),
        'password': input('password: ')
    }
    s = requests.session()
    # csrf_token は毎回変わるので取得する
    res = s.get(ATCODER_URL + 'login')
    soup = BeautifulSoup(res.text, 'lxml')
    csrf_token = soup.select('input[name=csrf_token]')[0].get('value')
    login_data['csrf_token'] = csrf_token
    # cookie も必要なので取得する
    response_cookie = res.cookies
    # ログイン
    res = s.post(ATCODER_URL + 'login', data=login_data,
                 cookies=response_cookie)
    res.raise_for_status()  # 失敗した場合例外を出す
    if res.url != 'https://atcoder.jp/home':
        print('Login failed!')
        exit()
    print(BeautifulSoup(res.text, 'lxml').select('div.alert')[0].text)
    with open(os.path.join(PATH, 'cookie.pkl'), 'wb') as f:
        pickle.dump(res.cookies, f)


def is_login(cookies):  # cookiesが有効どうか確認する
    res = requests.get(ATCODER_URL+'settings', cookies=cookies)
    setting_url = ATCODER_URL + 'settings'
    return res.url == setting_url


def get_contest_info(contest_name):
    if not os.path.isfile(os.path.join(PATH, 'cookie.pkl')):
        login()
    with open(os.path.join(PATH, 'cookie.pkl'), 'rb') as f:
        cookies = pickle.load(f)
    if not(is_login(cookies)):
        print('cookies is invalid \nPlease login again')
        login()
    # atcoderの印刷用問題のページから取得
    res = requests.get(ATCODER_URL+f'contests/{contest_name}/tasks_print',
                       cookies=cookies)
    soup = BeautifulSoup(res.text, 'lxml')
    title = soup.title.text
    if title == '404 Not Found - AtCoder':
        print(title)
        exit()
    CONTEST_INFO['name'] = title.replace(' ', '')
    problem_names = soup.select('span.h2')
    CONTEST_INFO['problem_names'] = list(map(lambda x: x.text.replace(' ', '')
                                             , problem_names))
    for name in CONTEST_INFO['problem_names']:
        CONTEST_INFO[name] = {}
    problem_io_styles = soup.select('.lang-ja > .io-style')
    # for name, io in zip(problem_names, problem_io_styles):
    for name, io in zip(problem_names, soup.select('.lang-ja')):
        examples = io.select('.io-style ~ div')
        name = name.text.replace(' ', '')
        if not('例' in list(map(lambda x: x.h3.text[2], examples))):
            print('Could not get test cases!')
            exit()
        CONTEST_INFO[name]['IN'] = [e.pre.text for e in examples[::2]]
        CONTEST_INFO[name]['OUT'] = [e.pre.text for e in examples[1::2]]
    print(title)
    print(*['\t' + pn.text for pn in problem_names], sep='\n')


def make_test_file_directory():
    contest_name = CONTEST_INFO['name']
    pathlib.Path(contest_name).mkdir()
    for i, name in enumerate(CONTEST_INFO['problem_names']):
        directory = f'{contest_name}/{name}'
        pathlib.Path(directory).mkdir(parents=True)
        param = ',\n'.join([f'{" "*8}("""{i}""", """{o}""")'for i, o in
                            zip(CONTEST_INFO[name]['IN'],
                                CONTEST_INFO[name]['OUT'])])
        with open(directory + f'/test_{chr(97 + i)}.py', 'w') as f:
            f.write('\n'.join(PYTEST_TEMPLATE[:6] + [param] +
                              PYTEST_TEMPLATE[6:]))
        with open(directory + '/Main.py', 'w'):
            pass


def main():
    contest_name = sys.argv[1]
    get_contest_info(contest_name)
    make_test_file_directory()


if __name__ == '__main__':
    main()
