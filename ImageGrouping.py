from PIL import Image,UnidentifiedImageError
from tqdm import tqdm
import re,os,math,argparse,imagehash,multiprocessing

# 引数を拾う
parser = argparse.ArgumentParser(description='フォルダ内から似た画像を探して自動でフォルダ分けを行うプログラムです。');
parser.add_argument('-t', '--threads', default=8, help="処理を行う際のスレッド数を指定します。(規定値=8)");
parser.add_argument('-s', '--similarity', default=10, help="画像を同一と判定する閾値を指定します。値が低いほど厳密に比較します。(規定値=10)");

args = parser.parse_args();
threads = int(args.threads);
similarity = int(args.similarity);

files = os.listdir();

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


# マルチスレッドでハッシュ生成
pool = multiprocessing.Pool(threads);
imap = pool.imap(hash_gen,files);
file_list = list(filter(None,list(tqdm(imap, bar_format='{l_bar}{bar:50}{r_bar}{bar:-10b}', desc="ImageHash処理中", total=len(files)))));

# ハッシュ比較
src_position = 0;
done = [];
groups = [];
lc = 0;
lc_max = int(math.factorial(len(file_list))/math.factorial(len(file_list)-2)/2);

print();

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

# フォルダ分け
offset = 0;
print('フォルダ分け中',end='');
for i in tqdm(range(len(groups)),bar_format='{l_bar}{bar:50}{r_bar}{bar:-10b}', desc="ファイル移動中"):
    while True:
        dirname = "g"+str(i+offset).zfill(8);
        try:
            os.mkdir(dirname);
        except FileExistsError as e:
            offset = offset + 1;
            pass;
        else :
            break;

    for src in groups[i]:
        dst = dirname + '/' + src;
        os.rename(src,dst);

print();
print('完了');
