import cv2
import os
import numpy as np

def extract_frames(video_path, output_folder, num_frames=150):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created folder: {output_folder}")

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames == 0:
        print("Error: Could not read video file.")
        return

    # Calculate step to get evenly spaced frames
    step = max(1, total_frames // num_frames)
    
    count = 0
    saved_count = 0
    
    print(f"Starting frame extraction from {video_path}...")
    print(f"Total video frames: {total_frames}, target: {num_frames}")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or saved_count >= num_frames:
            break
            
        if count % step == 0:
            # Resize for performance if needed (e.g., 1080p to 720p or similar)
            # frame = cv2.resize(frame, (1280, 720))
            
            frame_name = f"frame_{saved_count:04d}.webp"
            output_path = os.path.join(output_folder, frame_name)
            
            # Save as WebP with high quality
            cv2.imwrite(output_path, frame, [cv2.IMWRITE_WEBP_QUALITY, 85])
            saved_count += 1
            if saved_count % 10 == 0:
                print(f"Extracted {saved_count}/{num_frames} frames...")
                
        count += 1

    cap.release()
    print(f"Done! Extracted {saved_count} frames to {output_folder}")

if __name__ == "__main__":
    # Updated to use new video file
    video_path = "o:/python/clients/equila-demo/static/videos/equila-home-video.mp4"
    output_folder = "o:/python/clients/equila-demo/static/images/hero-frames"
    extract_frames(video_path, output_folder, num_frames=192)
