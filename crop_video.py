import os
import cv2
import ffmpeg

def convert_to_video_note(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.endswith(('.mp4', '.mov', '.avi')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_video_note.mp4")
            cap = cv2.VideoCapture(input_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            
            size = min(width, height)
            
            ffmpeg.input(input_path).filter(
                'crop', size, size
            ).filter(
                'scale', 640, 640
            ).filter(
                'format', 'yuv420p'
            ).output(
                output_path, vcodec='libx264', preset='fast', movflags='+faststart'
            ).run(overwrite_output=True)
            
            print(f"Обработано: {output_path}")

input_folder = ""
output_folder = ""
convert_to_video_note(input_folder, output_folder)
