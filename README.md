# atcoder_contest

AtCoderのサイトから情報を取得し、Pythonのユニットテストを作る。

## 必要なライブラリ

- beautifulsoup4
- lxml
- requests
- pytest(ユニットテストを実行するときに必要)

## 使い方

```
$python atcoder_contest.py [コンテスト名]
```

コンテスト名はコンテストページのURLの最後にある名前

```
https://atcoder.jp/contests/コンテスト名
```

- ログインして参加登録をしないと、開催中の問題が見れないため最初にログインする画面が表示される。
- 入力してログインに成功するとcookieをpickleを使い保存して次回以降利用する。
そして下のようなディレクトリとファイルを作る

```
AtCoderBeginnerContest151
├── A-NextAlphabet
│   ├── Main.py
│   └── test_a.py
├── B-AchievetheGoal
│   ├── Main.py
│   └── test_b.py
├── C-WelcometoAtCoder
│   ├── Main.py
│   └── test_c.py
├── D-MazeMaster
│   ├── Main.py
│   └── test_d.py
├── E-Max-MinSums
│   ├── Main.py
│   └── test_e.py
└── F-EncloseAll
    ├── Main.py
    └── test_f.py
```

`Main.py`に問題の回答を作り、問題のディレクトリを指定するか、そのディレクトリ内に入り、

```
$pytest
```
を実行し確認する。

