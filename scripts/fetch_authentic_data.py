import urllib.request
import os
import sys
import json

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

def download_file(url, dest_path):
    print(f"Downloading {url} -> {dest_path}...")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            with open(dest_path, 'wb') as f:
                f.write(data)
            print(f"SUCCESS: Saved {len(data):,} bytes to {dest_path}")
            return True
    except Exception as e:
        print(f"ERROR downloading {url}: {e}")
        return False

if __name__ == "__main__":
    test_urls = [
        ("https://raw.githubusercontent.com/Aryan-Pardeshi/gov-myscheme-dataset/main/gov_myscheme_data.csv", "data/1_policy_and_schemes/myscheme_central_state_schemes.csv"),
        ("https://raw.githubusercontent.com/Sshanu/civic_issue_dataset/master/pothole_coco.json", "data/2_civic_grievance/civic_infrastructure_damage/pothole_damage_coco.json"),
        ("https://raw.githubusercontent.com/Sshanu/civic_issue_dataset/master/garabage_coco.json", "data/2_civic_grievance/civic_infrastructure_damage/garbage_dump_coco.json"),
        ("https://raw.githubusercontent.com/Sshanu/civic_issue_dataset/master/road_coco.json", "data/2_civic_grievance/civic_infrastructure_damage/road_damage_coco.json"),
        ("https://raw.githubusercontent.com/danielpreotiuc/complaints-social-media/master/complaints-data.csv", "data/2_civic_grievance/citizen_complaints_logs/citizen_complaints_dataset.csv"),
    ]
    for url, path in test_urls:
        download_file(url, path)

