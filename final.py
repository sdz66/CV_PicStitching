from imutils import paths
import numpy as np
import imutils
import cv2
import os


# 图片拼接函数（弃用）
def stitch_images1(images, output_path="output.png"):
    """
    拼接多张图片为全景图
    :param images: 图片列表
    :param output_path: 输出文件路径
    :return: 是否成功拼接
    """
    print("[INFO] 正在拼接图片...")
    stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()
    (status, stitched) = stitcher.stitch(images)
    
    if status == 0:
        cv2.imwrite(output_path, stitched)
        
        # 获取屏幕宽度
        screen_width = 1920  # 屏幕宽度值
        try:
            import tkinter as tk
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            root.destroy()
        except:
            pass
        
        # 调整图片大小以适应屏幕宽度，同时保持宽高比
        h, w = stitched.shape[:2]
        if w > screen_width:
            ratio = screen_width / float(w)
            resized = cv2.resize(stitched, (screen_width, int(h * ratio)), interpolation=cv2.INTER_AREA)
        else:
            resized = stitched
        
        # 显示拼接后的图像
        # cv2.imshow("Stitched", resized)
        cv2.waitKey(0)
        return stitched
    else:
        print("[INFO] 图片拼接失败 ({})".format(status))
        return None

# 图片拼接函数
def stitch_images(images, output_path="output.png", crop=True, show_result=True):
    """
    拼接多张图片为全景图
    
    :param images: 图片列表，每个元素为numpy数组格式的图像
    :param output_path: 输出文件路径，默认"output.png"
    :param crop: 是否裁剪掉全景图周围的黑边，默认True
    :param show_result: 是否显示拼接结果，默认True
    :return: (status, result_image)
             status: 0-成功, 1-拼接失败, 2-裁剪失败
             result_image: 成功时返回拼接后的图像，失败返回None
    """
    # 初始化拼接器
    stitcher = cv2.Stitcher_create() if hasattr(cv2, 'Stitcher_create') else cv2.createStitcher()
    
    # 执行图像拼接
    status, stitched = stitcher.stitch(images)
    
    # 处理拼接失败的情况
    if status != cv2.Stitcher_OK:
        print(f"[ERROR] 图片拼接失败，错误码: {status}")
        return status, None
    
    # 裁剪处理
    if crop:
        try:
            # 添加边框确保轮廓检测准确
            stitched = cv2.copyMakeBorder(stitched, 2, 2, 2, 2, 
                                          cv2.BORDER_CONSTANT, (0, 0, 0))
            
            # 创建灰度图并二值化
            gray = cv2.cvtColor(stitched, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
            
            # 查找轮廓并获取最大轮廓
            contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(contours)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # 创建最小矩形区域掩码
            mask = np.zeros(thresh.shape, dtype="uint8")
            x, y, w, h = cv2.boundingRect(largest_contour)
            cv2.rectangle(mask, (x, y), (x+w, y+h), 255, -1)
            
            # 通过腐蚀找到最小矩形区域
            min_rect = mask.copy()
            sub_mask = mask.copy()
            
            # 迭代腐蚀直到找到最小矩形
            while cv2.countNonZero(sub_mask) > 0:
                min_rect = cv2.erode(min_rect, None)
                sub_mask = cv2.subtract(min_rect, thresh)
            
            # 获取最小矩形的边界框
            contours = cv2.findContours(min_rect, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(contours)
            x, y, w, h = cv2.boundingRect(contours[0])
            
            # 应用裁剪
            stitched = stitched[y:y+h, x:x+w]
        
        except Exception as e:
            print(f"[WARNING] 裁剪失败: {str(e)}")
            status = 2
    
    # 保存结果
    cv2.imwrite(output_path, stitched)
    print(f"[SUCCESS] 全景图已保存至: {output_path}")
    
    # 显示结果
    if show_result:
        # 获取屏幕尺寸
        screen_width = 1920
        try:
            import tkinter as tk
            root = tk.Tk()
            screen_width = root.winfo_screenwidth() - 100  # 留出边距
            root.destroy()
        except:
            pass
        
        # 调整显示尺寸
        h, w = stitched.shape[:2]
        if w > screen_width:
            ratio = screen_width / float(w)
            display_img = cv2.resize(stitched, (screen_width, int(h * ratio)))
        else:
            display_img = stitched
        
        # 显示拼接结果
        # cv2.imshow("全景图拼接结果", display_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return stitched

# 视频处理函数
def process_video(video_path, interval=0.3):
    """
    处理视频流，定期截取帧
    :param video_path: 视频文件路径
    :param interval: 截取帧的时间间隔（秒）
    :return: 拼接后的图像结果
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("[ERROR] 无法打开视频文件")
        return None
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval)
    count = 0
    images = []
    
    print("[INFO] 正在从视频中截取帧...")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        count += 1
        if count % frame_interval == 0:
            images.append(frame.copy())
            print(f"[INFO] 已截取第 {len(images)} 帧")
            
        # 显示当前帧（可选）
        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if len(images) >= 2:
        return stitch_images(images)
    else:
        print("[INFO] 截取的帧数不足，无法拼接")
        return None


# 图片目录处理函数
def process_images(input_dir):
    """
    处理图片目录中的图片
    :param input_dir: 图片目录路径
    :return: 拼接后的图像
    """
    print("[INFO] 正在加载图片...")
    imagePaths = sorted(list(paths.list_images(input_dir)))
    images = []
    
    for imagePath in imagePaths:
        try:
            with open(imagePath, 'rb') as f:
                img_data = np.frombuffer(f.read(), dtype=np.uint8)
                img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
                if img is not None:
                    images.append(img)
                else:
                    print(f"[WARN] 无法加载图片: {imagePath}")
        except Exception as e:
            print(f"[ERROR] 加载图片 {imagePath} 时出错: {str(e)}")
    
    if len(images) >= 2:
        return stitch_images(images)
    else:
        print("[INFO] 图片数量不足，无法拼接")
        return None


# 主程序
if __name__ == "__main__":
    # 选择输入源
    print("请选择输入源:")
    print("1 - 图片目录")
    print("2 - 视频文件")
    choice = input("请输入选项(1或2): ")
    
    if choice == "1":
        input_dir = "images/img3"  # 图片目录
        process_images(input_dir)
    elif choice == "2":
        video_path = "images/video/demo.mp4"  # 视频目录
        process_video(video_path, interval=0.3)  # 截取视频时间间隔
    else:
        print("无效选项")