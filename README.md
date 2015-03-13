バス路線データ
==========
このプログラムはバスのオープンデータを操作するプログラムです。  

バス路線データ  
http://needtec.sakura.ne.jp/bus_data/kusatu.html  


Pythonで「まめバス」のオープンデータを使ってみよう  
http://qiita.com/mima_ita/items/a962d7a56bd70c600ee6  

依存ファイル  
-------------
easy_install peewee  
easy_install xlrd  
easy_install enum34  
easy_install zenhan  
easy_install grequests  


インストール方法
-----------------
1.application.ini.originをコピーしてappication.iniを作成する。  
下記を修正すること。  

    [database]
    path = ./bus_data.sqlite # データべースのパス
    mod_path = C:\tool\spatialite\mod_spatialite.dll # mod_spatialite.dllへのパス
    sep = ;  # 環境変数PATHの区切り文字　WINDOWSは; LINUXは:とする

2.index.cgiの構築  
/home/username/bus_data/ にapplication.ini,databaseファイルがあるものとする.  
/home/username/www/bus_data/ が公開さきのディレクトリとする  
以下のコマンドを実行

    git clone git://github.com/mima3/bus_data.git 
    rm -rf bus_data/.git

    cp -rf bus_data /home/username/www/
    python /home/username/www/bus_data/create_index_cgi.py "/usr/local/bin/python" "/home/username/bus_data/application.ini" > /home/username/www/bus_data/index.cgi
    chmod +x  /home/username/www/bus_data/index.cgi

3.インポート  
HTTP経由でバスのオープンデータを取得し、DBの構築、更新を行います。  
    
    python import.py application.ini


ライセンス
-------------
当方が作成したコードに関してはMITとします。  
その他、pyshp、jqueryなどに関しては、それぞれにライセンスを参照してください。

    The MIT License (MIT)

    Copyright (c) 2015 m.ita

    Permission is hereby granted, free of charge, to any person obtaining a copy of
    this software and associated documentation files (the "Software"), to deal in
    the Software without restriction, including without limitation the rights to
    use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
    the Software, and to permit persons to whom the Software is furnished to do so,
    subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
    FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
    COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
    IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

