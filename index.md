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
| 主キー  | サブキー    | 値の型 | 規定値       | 内容                             | 
| ------- | ----------- | ------ | ------------ | -------------------------------- | 
| twitter | apiKey      | str    | - (省略不可) | Twitter APIのAPI Key             | 
|         | apiSecret   | str    | - (省略不可) | Twitter APIのAPI Secret          | 
|         | token       | str    | - (省略不可) | Twitter APIのAccess Token        | 
|         | tokenSecret | str    | - (省略不可) | Twitter APIのAccess Token Secret | 

### constants
| 特殊文字 |                                          | 
| -------- | ---------------------------------------- | 
| CWD      | 本体ファイルがあるディレクトリの絶対パス | 
