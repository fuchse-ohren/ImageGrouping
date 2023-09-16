# ImageGrouping
類似する画像を自動的にフォルダ分けします

## インストール方法
1. [リリースページ](https://github.com/fuchse-ohren/ImageGrouping/releases)から`setup.exe`をダウンロードします
2. `setup.exe`を起動して`...`をクリックして展開場所を選びます
3. `Extract`をクリックして展開します
4. 展開したフォルダにPathを通します  
   参考:[【Windows 11対応】Path環境変数を設定／編集して、独自のコマンドを実行可能にする：Tech TIPS - ＠IT](https://atmarkit.itmedia.co.jp/ait/articles/1805/11/news035.html)

## 使い方
1. 分類したい画像が保存されているフォルダでコマンドプロンプトを立ち上げます
2. `imgroup`と入力します  
   ※Pathが通っていないと動作しません。この場合、展開場所のフルパスを指定してください

### --help
```
> imgroup -h
usage: imgroup.exe [-h] [-t THREADS] [-s SIMILARITY]

フォルダ内から似た画像を探して自動でフォルダ分けを行うプログラムです。

options:
  -h, --help            show this help message and exit
  -t THREADS, --threads THREADS
                        処理を行う際のスレッド数を指定します。(規定値=8)
  -s SIMILARITY, --similarity SIMILARITY
                        画像を同一と判定する閾値を指定します。値が低いほど厳密に比較します。(規定値=10)
```

### 閾値について
閾値は`-s`オプションで指定します。規定値は`10`です。

値が大きければ曖昧に、小さければ性格に分類を行います。

一般的に以下の表の範囲で調整すると、上手くいきます。
| 画像の種類  | 閾値の範囲 |
| ------------- | ------------- |
| 写真  | 10～15  |
| イラスト  | 5～10  |

### スレッド数に関して
スレッド数は`-t`で指定します。規定値は`8`です。  
通常変更の必要はありません。

調整するときはCPUのコア数より少し多いぐらいが最速になります。  
デフォルトではPCがフリーズしてしまう場合、`1`に設定してください。
