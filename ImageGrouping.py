from PIL import Image,ImageFile,UnidentifiedImageError
from tqdm import tqdm
from sys import exit
import re,os,time,math,argparse,imagehash,multiprocessing

# ハッシュ生成
def hash_gen(file):
    regex_ext = r'.*\.(jpg|jpeg|png)';
    if re.match(regex_ext,file) :
        try:
            hash = imagehash.average_hash(Image.open(file));
        except UnidentifiedImageError as e:
            return None;
        else:
            return {"name":file,"hash":hash};

def reset():
    regex_folder = r'g\d{8}';
    dir = [];
    fail = [];

    for i in tqdm(os.listdir(),bar_format='{l_bar}{bar:50}{r_bar}{bar:-10b}', desc="フォルダ検出中"):
        if os.path.isdir(i) and re.match(regex_folder,i):
            dir.append(i);
    
    for d in tqdm(dir,bar_format='{l_bar}{bar:50}{r_bar}{bar:-10b}', desc="ファイル移動中"):
        files = os.listdir(d);
        for f in files:
            try:
                os.rename(d+"/"+f,f);
            except:
                pass;
    
    for d in tqdm(dir,bar_format='{l_bar}{bar:50}{r_bar}{bar:-10b}', desc="フォルダ削除中"):
        try:
            os.rmdir(d); #rmdirを使うと空のディレクトリだけ消せる
        except:
            fail.append(d);
    
    for f in fail:
        print("次のフォルダが削除できませんでした: %s"%(f));
    exit(1);

if __name__ == "__main__":
    # 大きいサイズの画像を読み込むためのフラグ
    ImageFile.LOAD_TRUNCATED_IMAGES = True;

    # for Windows
    multiprocessing.freeze_support()

    # 引数を拾う
    parser = argparse.ArgumentParser(description='フォルダ内から似た画像を探して自動でフォルダ分けを行うプログラムです。',formatter_class=argparse.RawTextHelpFormatter);
    parser.add_argument('-t', '--threads', default=8, help="処理を行う際のスレッド数を指定します。(規定値=8)");
    parser.add_argument('-s', '--similarity', default=10, help="画像を同一と判定する閾値を指定します。値が低いほど厳密に比較します。(規定値=10)");
    parser.add_argument('-m','--mode',default='move',help=" \n \
    動作モードを指定します。\n \
    test\t・・・\tグループ分けの結果のみ表示\n \
    move\t・・・\tグループごとにフォルダを作成し、ファイルを移動します(規定値)\n \
    rename\t・・・\tグループ名を接頭辞として利用しファイル名を変更します \
    copy\t・・・\t未実装の機能です。グループごとにフォルダを作成し、ファイルを移動します(規定値)\n \
    link\t・・・\tグループごとにフォルダを作成し、フォルダ内にシンボリックリンクを作成します \n \
    reset\t・・・\tグルーピングされたフォルダを元に戻します\n \
    ");

    # 引数の取り出しとチェック
    args = parser.parse_args();
    threads = int(args.threads);
    similarity = int(args.similarity);
    if not (1 <= threads <= 32) or not (0 <= similarity <= 100):
        print("エラー: threadは1以上32以下、similarityは0以上100以下である必要があります。");
        exit(1);
    if not args.mode in ['test','move','rename','copy','link','reset']:
        print("エラー: modeは「test」「move」「rename」「copy」「link」「reset」である必要があります。");
        exit(1);

    # resetの場合
    if args.mode == 'reset':
        reset();

    # ファイル一覧を取得
    files = os.listdir();
    if len(files) <= 2:
        print("エラー: ファイルが二つ以上存在する必要があります。");
        exit(1);
        
    # マルチスレッドでハッシュ生成
    pool = multiprocessing.Pool(threads);
    imap = pool.imap(hash_gen,files);
    file_list = list(filter(None,list(tqdm(imap, bar_format='{l_bar}{bar:50}{r_bar}{bar:-10b}', desc="ImageHash処理中", total=len(files)))));
    if len(file_list) <= 2:
        print("エラー: 比較の対象となるファイルは二つ以上存在する必要があります。");
        exit(1);
    print();


    # ハッシュ比較
    src_position = 0;
    done = [];
    groups = [];
    lc = 0;
    lc_max = int(math.factorial(len(file_list))/math.factorial(len(file_list)-2)/2);

    for src in tqdm(file_list,bar_format='{l_bar}{bar:50}{r_bar}{bar:-10b}', desc="類似判定中"):
        group = [src['name']];
        for dst in file_list[src_position:]:
            lc = lc + 1;
            if src['name'] != dst['name'] and not src['name'] in done and not dst['name'] in done: 
                if(src['hash']-dst['hash'] < similarity):
                    group.append(dst['name']);
                    done.append(dst['name']);
        if(len(group) > 1):
            groups.append(group);
        src_position = src_position + 1;
    print();
    if len(groups) <= 0:
        print("類似画像が見つかりませんでした。閾値を上げて再度お試しください。");
        exit(1);

    # フォルダ分け
    offset = 0;
    output = "";
    for i in tqdm(range(len(groups)),bar_format='{l_bar}{bar:50}{r_bar}{bar:-10b}', desc="仕分処理中"):
        
        while True:
            dirname = "g"+str(i+offset).zfill(8);
            try:
                os.mkdir(dirname);
            except FileExistsError as e:
                offset = offset + 1;
                pass;
            else :
                break;

        dirname = "g"+str(i+offset).zfill(8);
        for src in groups[i]:
            dst = dirname + '/' + src;
            
            if args.mode == 'test':
                output += "%s:\t%s\n"%(dirname,src);
            elif args.mode == 'move':
                os.rename(src,dst);
            elif args.mode == 'copy':
                print("未実装");
                exit(1);
            elif args.mode == 'link':
                os.symlink('..\\'+src,dst);
            elif args.mode == 'rename':
                os.rename(src,dirname + '_' + src);
            
        
        # 後処理
        
        # テストモードの時作成したフォルダを削除する
        if args.mode == 'test' or args.mode == 'rename':
            os.rmdir(dirname);
            
    print(output);
    print('完了');
