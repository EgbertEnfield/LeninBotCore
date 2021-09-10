# LeninBotCore Ver. 1.2.910,1717

## Twitter Bot using Twitter API → [Follow @Lenin_Bot_1917](https://twitter.com/Lenin_Bot_1917?ref_src=twsrc%5Etfw)

---

## 変更ログ

+ 2021/9/5 初期版作成
+ 2021/9/6
  + Bot開始
  + オブジェクト指向的構文から変更
  + 関数名、変数名の変更
  + デバッグモード、おはツイ、おやツイモード追加
+ 2021/9/7
  + ログの状態の出力を詳細化
  + ツイートデータベースをcsvからjsonの配列に変更
  + 設定ファイルとプログラムを追加
+ 2021/9/8
  + ログメッセージのスペルミスを修正
  + バージョン確認、ヘルプ表示の引数を追加
+ 2021/9/10
  + settings.jsonにデバッグモード、ログ出力確認モードのキー追加
  + ログ出力にスタックトレースを追加する機能を追加
  + ログ出力の日付、時刻表示を変更するキーを追加
  + ログ出力の場所を変更するキーを追加

---

動作に必要なファイルやディレクトリなど

+ botcore.py
+ logmgr.py
+ keys.json
+ settings.json
+ tweets.json
  + (dir) log

---

### settings.json

| 主キー | サブキー          | 値の型 | 規定値            | 内容                                       |
| ------ | ----------------- | ------ | ----------------- | ------------------------------------------ |
| main   | ignoreError       | bool   | True              | エラーが発生しても処理を止めない           |
| log    | maxLogSize        | int    | 51200             | ログファイルの最大サイズ 単位:B            |
|        | logDirectory      | str    | f'{CWD}/log'      | ログファイルの場所                         |
|        | isLogStacktrace   | bool   | False             | エラーのスタックトレースも記録する         |
|        | logDatetimeFormat | str    | %y-%m-%d-%H-%M-%S | ログファイルの日付、時刻表示のフォーマット |

### keys.json(必須)

| 主キー  | サブキー    | 値の型 | 規定値       | 内容                             |
| ------- | ----------- | ------ | ------------ | -------------------------------- |
| twitter | apiKey      | str    | - (省略不可) | Twitter APIのAPI Key             |
|         | apiSecret   | str    | - (省略不可) | Twitter APIのAPI Secret          |
|         | token       | str    | - (省略不可) | Twitter APIのAccess Token        |
|         | tokenSecret | str    | - (省略不可) | Twitter APIのAccess Token Secret |

### tweets.json

適宜変更

constants

| 定数名 |                                          |
| ------ | ---------------------------------------- |
| CWD    | 本体ファイルがあるディレクトリの絶対パス |
