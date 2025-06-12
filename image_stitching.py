from imutils import paths
import numpy as np
import argparse
import imutils
import cv2

# 直接指定输入图片目录和输出路径
input_dir = "images/newimages"
output_path = "output.png"

# 获取输入图片路径并初始化图片列表
print("[INFO] 正在加载图片...")
imagePaths = sorted(list(paths.list_images(input_dir)))
images = []

# 遍历图片路径，加载每张图片并添加到拼接图片列表
for imagePath in imagePaths:
	image = cv2.imread(imagePath)
	images.append(image)

# 初始化OpenCV的图像拼接对象并执行图片拼接
print("[INFO] 正在拼接图片...")
stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()
(status, stitched) = stitcher.stitch(images)

# 如果状态为'0'，表示OpenCV成功完成了图片拼接
if status == 0:
	# 将拼接后的图片保存
	cv2.imwrite(output_path, stitched)

	# 在屏幕上显示拼接后的图片
	cv2.imshow("Stitched", stitched)
	cv2.waitKey(0)

# 拼接失败，可能是由于没有检测到足够的关键点
else:
	print("[INFO] image stitching failed ({})".format(status))