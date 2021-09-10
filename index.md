# LeninBotCore
### settings.json
| 主キー | サブキー          | 値の型 | 規定値            | 内容                                       |
| ------ | ----------------- | ------ | ----------------- | ------------------------------------------ |
| main   | ignoreError       | bool   | True              | エラーが発生しても処理を止めない           |
| log    | maxLogSize        | int    | 51200             | ログファイルの最大サイズ 単位:B            |
|        | logDirectory      | str    | f'{CWD}/log'      | ログファイルの場所                         |
|        | isLogStacktrace   | bool   | False             | エラーのスタックトレースも記録する         |
|        | logDatetimeFormat | str    | %y-%m-%d-%H-%M-%S | ログファイルの日付、時刻表示のフォーマット |

### keys.json(必須)
| 主キー  | サブキー    | 値の型 | 規定値   | 内容                             |
| ------- | ----------- | ------ | -------- | -------------------------------- |
| twitter | apiKey      | str    | - (必須) | Twitter APIのAPI Key             |
|         | apiSecret   | str    | - (必須) | Twitter APIのAPI Secret          |
|         | token       | str    | - (必須) | Twitter APIのAccess Token        |
|         | tokenSecret | str    | - (必須) | Twitter APIのAccess Token Secret |

### 定数など
| 定数名 | 内容                                     |
| ------ | ---------------------------------------- |
| CWD    | 本体ファイルがあるディレクトリの絶対パス |
