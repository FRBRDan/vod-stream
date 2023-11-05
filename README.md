# vod-stream


## Don't forget - Mapping of video names to file paths inside "gui.py"

```    
def get_video_url(self, video_name):
        # Mapping of video names to file paths
        video_urls = {
            "Movie 1": "/path/to/your/video/sample.mp4",
            "Movie 2": "/path/to/your/video/test.mp4",
            "Movie 3": "/path/to/your/video/test2.mp4",
        }
        return video_urls.get(video_name)
```

#### Make sure to replace the placeholders in the video_urls dictionary with the correct paths to your video files 