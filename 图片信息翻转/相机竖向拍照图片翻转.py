# -*- coding: utf8 -*-
from PIL import Image
from os import getcwd, path, makedirs
from glob import glob
from time import sleep,time
from concurrent.futures import ThreadPoolExecutor,as_completed
import piexif
from pathlib import Path


# 程序默认进行了一定的压缩，设置为95的比例
# 新增对时间的限制 1798680290(2026-12-31 09:24:50) 结束
# 转为exe程序：pyinstaller -F -n 相机图片翻转1.3.2 -i peng.ico  深圳米兰相机竖向拍照图片翻转.py
# 新增保存图片的exif信息和添加多线程，默认仅使用4线程，再多也会受到io的影响
# 1.3  修改图片运行的条件，宽大高就执行
# 1.3.2  不改变原来的文件，直接新建复制到当前目录的 转后。

# 获取当前工作目录
current_dir = getcwd()
save_path = f"{current_dir}\转后"
if not path.exists(save_path):
    makedirs(save_path)  # 如果不存在，则创建文件夹


def process_image(input_file):
    """旋转图片并保留EXIF信息"""
    try:
        rotate_image_if_ratio_matches(input_file)
    except Exception as e:
        print(f"处理图片 {input_file} 时发生错误: {e}")


def process_images(jpg_files, max_threads=4):
    """使用多线程处理图片列表"""
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(process_image, file_path): file_path for file_path in jpg_files}
        for future in as_completed(futures):
            file_path = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"处理图片 {file_path} 时发生错误: {e}")


def rotate_image_if_ratio_matches(input_file):
    # 读取jpg图片
    with Image.open(input_file) as img:
        # 获取图片原始尺寸
        original_width, original_height = img.size
        # 检查宽高是否符合横屏的比例
        if original_width > original_height:
            try:
                exif_bytes = img.info.get('exif')  # 获取原图片的二进制EXIF数据
                if exif_bytes is not None:
                    exif_data = piexif.load(exif_bytes)  # 解析二进制EXIF数据为字典
                    if '0th' in exif_data and 274 in exif_data['0th']:
                        exif_data['0th'][274] = 0  # 设置EXIF Orientation属性为正常
                        # 使用piexif将修改后的EXIF字典编码为二进制
                        exif_bytes = piexif.dump(exif_data)
                    else:
                        print(f"图片 {input_file} 的EXIF数据中缺少必要的键，无法设置为竖向")
                        exif_bytes = None
                else:
                    print(f"图片 {input_file} 无EXIF数据，无法设置为竖向")
                    exif_bytes = None
            except Exception as e:
                print(f"获取或修改图片 {input_file} 的EXIF信息时发生错误: {e}")
                exif_bytes = None  # 如果获取或修改EXIF失败，设为None

            # 如果符合，进行旋转操作（实际上是上下翻转，因为宽高对调）
            rotated_img = img.rotate(90, expand=True)
            save_file = f"{save_path}/{Path(input_file).name}"
            # 直接保存旋转后的图片覆盖原图
            rotated_img.save(
                save_file,
                quality=95,
                dpi=(300, 300),
                exif=exif_bytes,  # 保存修改后的EXIF信息（二进制形式）
            )
        else:
            print(f"{input_file} 不需要转换")


end = 1798680290   # 2026-12-31 09:24:50
if int(time()) < end:
    # 使用glob查找当前目录下所有jpg文件
    jpg_files = glob(path.join(current_dir, "*.jpg"))

    # 启动多线程处理图片
    process_images(jpg_files)

    print('完成！退出！')
    sleep(1)
    exit('退出！')
else:
    print('时间过期了，请联系 鹏！')
    sleep(10)
    exit('退出！')