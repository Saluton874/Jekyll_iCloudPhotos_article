import datetime, re, os, glob
from osxphotos import PhotosAlbum
from PIL import Image

path  = os.path.abspath(os.path.dirname(__file__))+'/'
img_url = 'assets/images/posts/'

if __name__ == "__main__":

	# 写真に埋め込むロゴ画像の指定
	logo = Image.open(path+img_url+'mail.png')

	# PIL：写真中央で切り抜き
	def crop_center(pil_img, crop_width, crop_height):
		img_width, img_height = pil_img.size
		return pil_img.crop(((img_width - crop_width) // 2,
							(img_height - crop_height) // 2,
							(img_width + crop_width) // 2,
							(img_height + crop_height) // 2))

	# PIL：4対3の写真に切り抜く
	def crop_max_4tai3(pil_img):
		w = pil_img.size[0]
		return crop_center(pil_img, w, w*0.7)

	# PIL：写真の幅基準でリサイズ
	def scale_to_width(img, width):
		height = round(img.height * width / img.width)
		return img.resize((width, height))

	# 写真のリストを読み込み
	save_photos = []
	for filename in  glob.glob(path+img_url+'*.jpeg'):
		save_photos.append(os.path.basename(filename))

	# 「日記」アルバムの写真を取得
	photos = PhotosAlbum("日記").photos()
	title_list = [] # 書き出し対象のタイトルの保存場所
	photo_list = [] # 書き出し対象の写真ファイル名の保存場所
	for photo in photos:
		# 写真のキーワード（カテゴリ）が設定されているもののみ処理
		if len(photo.keywords) > 0:
			photo_filename = os.path.splitext(photo.filename)[0]+'.jpeg'
			# 書き出されていない写真を書き出す
			if not photo_filename in save_photos:
				# 実寸大でそのまま書き出し
				photo.export(path+img_url)
				# PILで読み込み編集
				img = Image.open(path+img_url+photo_filename)
				img = crop_max_4tai3(img) # 4:3の写真にする
				img = scale_to_width(img, 800) # 最大幅を800pxにする
				img.paste(logo, (0, 0), logo) # ロゴ画像を埋め込む
				img.save(path+img_url+photo_filename, quality=95) # 上書き保存
			# 写真の日時＋写真のタイトル.mdをファイル名にする
			title = photo.date.strftime('%Y-%m-%d')+'-'+photo.title+'.md'
			# 書き出し対象のタイトル、写真ファイル名を保存する
			title_list.append(title)
			photo_list.append(photo_filename)
			# .mdファイルのヘッダの書き出し
			# ---
			# layout: posts
			# date:   写真の投稿時間 +0900
			# categories: 写真のキーワード
			# ---
			head  = '---\nlayout: posts\ndate:   '+photo.date.strftime('%Y-%m-%d %H:%M:%S +0900')+'\ncategories: '+photo.keywords[0]+'\n---\n'
			# 本文は写真表示と、写真のキャプションを書き出し
			text  = head+'!['+photo.title+'の写真]('+'/'+img_url+photo_list[-1]+')'+photo.description
			# postsフォルダへ書き出し
			with open(path+'_posts/'+title, 'w') as f:
				f.write(text)

	# 書き出されていないタイトルのmdファイルは削除する
	for filename in  glob.glob(path+'_posts/*.md'):
		basename = os.path.basename(filename)
		if not basename in title_list:
			os.remove(filename)
			os.remove(photo_list)

	# 書き出しに該当しなかった写真を削除する
	for filename in  glob.glob(path+img_url+'*.jpeg'):
		basename = os.path.basename(filename)
		if not basename in photo_list:
			os.remove(filename)