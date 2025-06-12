from imutils import paths
import numpy as np
import imutils
import cv2


# 图片拼接函数
def stitch_images(images, output_path="output.png"):
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
        
        cv2.imshow("Stitched", resized)
        cv2.waitKey(0)
        return True
    else:
        print("[INFO] 图片拼接失败 ({})".format(status))
        return False


# 视频处理函数
def process_video(video_path, interval=0.3):
    """
    处理视频流，定期截取帧
    :param video_path: 视频文件路径
    :param interval: 截取帧的时间间隔（秒）
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("[ERROR] 无法打开视频文件")
        return
    
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
        stitch_images(images)
    else:
        print("[INFO] 截取的帧数不足，无法拼接")


# 图片目录处理函数
def process_images(input_dir):
    """
    处理图片目录中的图片
    :param input_dir: 图片目录路径
    """
    print("[INFO] 正在加载图片...")
    imagePaths = sorted(list(paths.list_images(input_dir)))
    images = [cv2.imread(imagePath) for imagePath in imagePaths]
    
    if len(images) >= 2:
        stitch_images(images)
    else:
        print("[INFO] 图片数量不足，无法拼接")


# 主程序
if __name__ == "__main__":
    # 选择输入源
    print("请选择输入源:")
    print("1 - 图片目录")
    print("2 - 视频文件")
    choice = input("请输入选项(1或2): ")
    
    if choice == "1":
        input_dir = "images/img1"  # 图片目录
        process_images(input_dir)
    elif choice == "2":
        video_path = "images/video/demo.mp4"  # 视频目录
        process_video(video_path, interval=0.3)  # 截取视频时间间隔
    else:
        print("无效选项")