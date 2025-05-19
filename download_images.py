import os

# Script to download images for the ENSEA Data Science Club platform

import requests

# URLs of assets to download
assets = {
    "hero-data.jpg": "https://unsplash.com/photos/DZpc4UY8ZtY/download?force=true",
    "data-points.svg": "https://www.svgrepo.com/download/303740/data-points.svg",
    "data-analytics.svg": "https://www.svgrepo.com/download/303741/data-analytics.svg",
    "dots-pattern.svg": "https://www.svgrepo.com/download/10097449/seamless-pattern-with-dots-stitches.svg"
}

# Ensure the target directory exists
output_dir = "static/images"
os.makedirs(output_dir, exist_ok=True)

# Download each asset
for filename, url in assets.items():
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(output_dir, filename), "wb") as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download {filename}: HTTP {response.status_code}")

# Inform the user
print("\nAll done! The images are in static/images/")
