import os
import requests

# The list of image URLs provided
urls = [
    "https://images.pexels.com/photos/37190240/pexels-photo-37190240.jpeg?_gl=1*1m4xgne*_ga*NTUxMjQ1MjgxLjE3Nzg4Mzg3MDU.*_ga_8JE65Q40S6*czE3Nzg4Mzg3MDQkbzEkZzEkdDE3Nzg4Mzg3MTQkajUwJGwwJGgw",
    
    "https://images.pexels.com/photos/27352802/pexels-photo-27352802.png?_gl=1*o9slr5*_ga*NTUxMjQ1MjgxLjE3Nzg4Mzg3MDU.*_ga_8JE65Q40S6*czE3Nzg4Mzg3MDQkbzEkZzEkdDE3Nzg4Mzg4NjUkajM3JGwwJGgw",
    
    "https://images.pexels.com/photos/27063075/pexels-photo-27063075.jpeg?_gl=1*khii61*_ga*NTUxMjQ1MjgxLjE3Nzg4Mzg3MDU.*_ga_8JE65Q40S6*czE3Nzg4Mzg3MDQkbzEkZzEkdDE3Nzg4Mzg5MzYkajUxJGwwJGgw",
    
    "https://images.pexels.com/photos/7202773/pexels-photo-7202773.jpeg?_gl=1*txo4kd*_ga*NTUxMjQ1MjgxLjE3Nzg4Mzg3MDU.*_ga_8JE65Q40S6*czE3Nzg4Mzg3MDQkbzEkZzEkdDE3Nzg4MzkwMjQkajI2JGwwJGgw",
    
    "https://images.pexels.com/photos/8306365/pexels-photo-8306365.jpeg?_gl=1*b8l5rq*_ga*NTUxMjQ1MjgxLjE3Nzg4Mzg3MDU.*_ga_8JE65Q40S6*czE3Nzg4Mzg3MDQkbzEkZzEkdDE3Nzg4MzkwNjYkajU5JGwwJGgw",
    
    "https://images.pexels.com/photos/11830673/pexels-photo-11830673.jpeg?_gl=1*15raxxg*_ga*NTUxMjQ1MjgxLjE3Nzg4Mzg3MDU.*_ga_8JE65Q40S6*czE3Nzg4Mzg3MDQkbzEkZzEkdDE3Nzg4MzkxMDAkajI1JGwwJGgw",
    
    "https://images.pexels.com/photos/5264910/pexels-photo-5264910.jpeg?_gl=1*1qky0se*_ga*NTUxMjQ1MjgxLjE3Nzg4Mzg3MDU.*_ga_8JE65Q40S6*czE3Nzg4Mzg3MDQkbzEkZzEkdDE3Nzg4MzkxMjAkajUkbDAkaDA.",
    
    "https://images.pexels.com/photos/5828579/pexels-photo-5828579.jpeg?_gl=1*1f8z2wv*_ga*NTUxMjQ1MjgxLjE3Nzg4Mzg3MDU.*_ga_8JE65Q40S6*czE3Nzg4Mzg3MDQkbzEkZzEkdDE3Nzg4MzkxODYkajI4JGwwJGgw",
    
    "https://images.pexels.com/photos/35336381/pexels-photo-35336381.jpeg?_gl=1*1y62fs4*_ga*NTUxMjQ1MjgxLjE3Nzg4Mzg3MDU.*_ga_8JE65Q40S6*czE3Nzg4Mzg3MDQkbzEkZzEkdDE3Nzg4MzkyMzIkajQyJGwwJGgw",
    
    "https://images.pexels.com/photos/3876574/pexels-photo-3876574.jpeg?_gl=1*1p0hkzt*_ga*NTUxMjQ1MjgxLjE3Nzg4Mzg3MDU.*_ga_8JE65Q40S6*czE3Nzg4Mzg3MDQkbzEkZzEkdDE3Nzg4MzkyODUkajU0JGwwJGgw",
    
    "https://images.pexels.com/photos/3925956/pexels-photo-3925956.jpeg?_gl=1*dloro1*_ga*NTUxMjQ1MjgxLjE3Nzg4Mzg3MDU.*_ga_8JE65Q40S6*czE3Nzg4Mzg3MDQkbzEkZzEkdDE3Nzg4MzkzNTQkajU5JGwwJGgw",
    
    "https://images.pexels.com/photos/34591081/pexels-photo-34591081.jpeg?_gl=1*84w17*_ga*NTUxMjQ1MjgxLjE3Nzg4Mzg3MDU.*_ga_8JE65Q40S6*czE3Nzg4Mzg3MDQkbzEkZzEkdDE3Nzg4MzkzOTgkajE1JGwwJGgw"
]

# Define the directory path
save_dir = "static/images/enhanced-images"

# Create the directory if it doesn't exist
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
    print(f"Created directory: {save_dir}")

def download_images():
    for index, url in enumerate(urls, start=1):
        try:
            # Strip Pexels tracking parameters for a clean request
            clean_url = url.split('?')[0]
            
            # Determine extension (png or jpeg)
            extension = "png" if ".png" in clean_url else "jpeg"
            filename = f"img{index}.{extension}"
            file_path = os.path.join(save_dir, filename)

            print(f"Downloading {filename}...")
            
            # Send GET request
            response = requests.get(url, stream=True)
            response.raise_for_status() # Check for request errors

            # Write the file in binary mode
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Successfully saved to {file_path}")

        except Exception as e:
            print(f"Failed to download image {index}: {e}")

if __name__ == "__main__":
    download_images()
    print("\nDownload process complete.")