from imutils import paths
import numpy as np
import argparse
import imutils
import cv2

# 直接指定输入图片目录和输出路径
input_dir = "images/img2"
output_path = "output.png"
crop = 1

# 获取输入图片路径并初始化图片列表
print("[INFO] loading images...")
imagePaths = sorted(list(paths.list_images(input_dir)))

images = []

# 遍历图像路径，加载每一张图像，并将它们添加到待拼接的图像列表中
for imagePath in imagePaths:
	image = cv2.imread(imagePath)
	images.append(image)
    
# 初始化 OpenCV 的图像拼接器对象，然后执行图像拼接操作
print("[INFO] stitching images...")
stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()
(status, stitched) = stitcher.stitch(images)

# 如果状态码为 '0'，则表明 OpenCV 成功完成了图像拼接
if status == 0:
    # 检查是否需要从拼接图像中裁剪出最大的矩形区域
    if crop > 0:
        # 在拼接图像周围创建10像素的边框
        print("[INFO] cropping...")
        stitched = cv2.copyMakeBorder(stitched, 2, 2, 2, 2,
                                      cv2.BORDER_CONSTANT, (0, 0, 0))

        # 将拼接图像转换为灰度图并进行阈值处理
        # 将所有大于零的像素设为255(前景)
        # 其余像素保持为0(背景)
        gray = cv2.cvtColor(stitched, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]

        # 在阈值图像中查找所有外部轮廓
        # 然后找到最大的轮廓，即拼接图像的轮廓
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        c = max(cnts, key=cv2.contourArea)

        # 为包含拼接图像区域矩形边界框的掩码分配内存
        mask = np.zeros(thresh.shape, dtype="uint8")
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)

        # 创建掩码的两个副本：一个作为实际的最小矩形区域
        # 另一个作为计数器，记录需要移除多少像素才能形成最小矩形区域
        minRect = mask.copy()
        sub = mask.copy()

        # 持续循环直到减去图像中没有非零像素为止
        while cv2.countNonZero(sub) > 0:
            # 腐蚀最小矩形掩码，然后从最小矩形掩码中减去阈值图像
            # 这样我们可以计算是否还有非零像素剩余
            minRect = cv2.erode(minRect, None)
            sub = cv2.subtract(minRect, thresh)

        # 在最小矩形掩码中查找轮廓
        # 然后提取边界框的(x,y)坐标
        cnts = cv2.findContours(minRect.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        c = max(cnts, key=cv2.contourArea)
        (x, y, w, h) = cv2.boundingRect(c)

        # 使用边界框坐标提取最终的拼接图像
        stitched = stitched[y:y + h, x:x + w]

    # 将拼接后的图片保存
    cv2.imwrite(output_path, stitched)

    # display the output stitched image to our screen
    cv2.imshow("Stitched", stitched)
    cv2.waitKey(0)

# 拼接失败，可能是由于检测到的关键点不足
else:
    print("[INFO] 图片拼接失败({})".format(status))
