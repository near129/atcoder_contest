import sys
from pathlib import Path
import pickle
import requests
from bs4 import BeautifulSoup

PYTEST_TEMPLATE = [
    'import sys',
    'from io import StringIO',
    'import pytest',
    'import Main',
    '',
    'params = {',
    '}',
    '',
    '@pytest.mark.parametrize("IN, OUT",',
    '                         list(params.values()), ids=list(params.keys()))',
    'def test_1(IN, OUT):',
    '    sys.stdin = StringIO(IN)',
    '    answer = str(Main.solve()) + "\\n"',
    '    assert answer == OUT',
    ''
]
MAIN_TEMPLATE = [
    'def solve():',
    '    pass',
    '',
    '',
    'if __name__ == "__main__":',
    '    answer = solve()',
    '    print(answer)',
    ''
]
ATCODER_URL = 'https://atcoder.jp/'
CONTEST_INFO = {}
CURRENT_PATH = Path(__file__).parent


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
    # pickle化
    with open(CURRENT_PATH / Path('cookie.pkl'), 'wb') as f:
        pickle.dump(res.cookies, f)


def is_login(cookies):
    # cookiesが有効どうか確認する
    res = requests.get(ATCODER_URL + 'settings', cookies=cookies)
    setting_url = ATCODER_URL + 'settings'
    return res.url == setting_url


def get_contest_info(contest_id):
    CONTEST_INFO['contest_id'] = contest_id
    # 保存したcookieの取得
    if not (CURRENT_PATH / Path('cookie.pkl')).exists():
        login()
    with open(CURRENT_PATH / Path('cookie.pkl'), 'rb') as f:
        cookies = pickle.load(f)
    if not (is_login(cookies)):
        print('cookies is invalid \nPlease login again')
        login()
    # atcoderの印刷用問題のページから取得
    res = requests.get(ATCODER_URL + f'contests/{contest_id}/tasks_print',
                       cookies=cookies)
    soup = BeautifulSoup(res.text, 'lxml')
    title = soup.title.text
    if title == '404 Not Found - AtCoder':
        print(title)
        exit()
    CONTEST_INFO['name'] = title.replace(' ', '')
    problem_names = soup.select('span.h2')
    CONTEST_INFO['problem_names'] = list(map(lambda x: x.text.replace(' ', ''),
                                             problem_names))
    for name, io in zip(CONTEST_INFO['problem_names'],
                        soup.select('.lang-ja')):
        CONTEST_INFO[name] = {}
        examples = io.select('.io-style ~ div')
        # しっかりサンプルケースを取得しているか確認
        if not ('例' in list(map(lambda x: x.h3.text[2], examples))):
            print('Could not get test cases!')
            exit()
        CONTEST_INFO[name]['IN'] = [e.pre.text for e in examples[::2]]
        CONTEST_INFO[name]['OUT'] = [e.pre.text for e in examples[1::2]]
    print('-' * 32, title, *['\t' + pn.text for pn in problem_names],
          '-' * 32, sep='\n')


# デバックなど用に入力例のテキストファイルを作成する(リダイレクション)
def make_testcase_text(directory, problem_name):
    directory /= Path('IN')
    directory.mkdir()
    for num, IN in enumerate(CONTEST_INFO[problem_name]['IN']):
        with open(directory / Path(f'{num+1:03}'), 'w') as f:
            f.write(IN)


def make_test_file_directory():
    contest_id = CONTEST_INFO['contest_id']
    contest_dir = Path(contest_id)
    print(contest_dir.absolute())
    contest_dir.mkdir()
    for i, name in enumerate(CONTEST_INFO['problem_names']):
        directory = contest_dir / Path(chr(97 + i))
        directory.mkdir(parents=True)
        example = []
        for n, (In, Out) in enumerate(zip(CONTEST_INFO[name]['IN'],
                                          CONTEST_INFO[name]['OUT'])):
            example.append(f'{" " * 4}"ex.{n}": ("""{In}""", """{Out}""")')
        with open(directory / Path(f'test_{chr(97 + i)}.py'), 'w') as f:
            f.write('\n'.join(PYTEST_TEMPLATE[:6] + [',\n'.join(example)] +
                              PYTEST_TEMPLATE[6:]))
        with open(directory / Path('Main.py'), 'w') as f:
            f.write('\n'.join(MAIN_TEMPLATE))
        make_testcase_text(directory, name)
    print('Files created successfully!!')


def main():

    contest_name = sys.argv[1]
    get_contest_info(contest_name)
    make_test_file_directory()


if __name__ == '__main__':
    main()
