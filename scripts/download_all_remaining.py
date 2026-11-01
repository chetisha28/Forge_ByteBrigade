import urllib.request
import os
import json
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

DOWNLOADS = [
    # Track 1
    ("https://raw.githubusercontent.com/urbanmorph/schemes/main/data/registry.json",
     "data/1_policy_and_schemes/urbanmorph_schemes_master_registry.json"),
    ("https://raw.githubusercontent.com/Aryan-Pardeshi/gov-myscheme-dataset/main/gov_myscheme_data.json",
     "data/1_policy_and_schemes/myscheme_central_state_schemes.json"),

    # Track 2
    ("https://raw.githubusercontent.com/Sshanu/civic_issue_dataset/master/garbage_coco.json",
     "data/2_civic_grievance/civic_infrastructure_damage/garbage_dump_coco.json"),
    ("https://raw.githubusercontent.com/Sshanu/civic_issue_dataset/master/new_images_coco.json",
     "data/2_civic_grievance/civic_infrastructure_damage/new_images_coco.json"),

    # Track 4
    ("https://raw.githubusercontent.com/sonalgarg174/Dataset/main/IFND.csv",
     "data/4_fact_verification/IFND_indian_fact_check_benchmark.csv"),
    ("https://static.pib.gov.in/WriteReadData/specificdocs/documents/2024/feb/doc202422305301.pdf",
     "data/4_fact_verification/pib_factcheck_in_numbers.pdf"),
    ("https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/mar/doc2025324525501.pdf",
     "data/4_fact_verification/pib_fraudulent_websites_registry.pdf"),
]

def download_file(url, dest_path):
    print(f"Downloading {url} -> {dest_path}...")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, 'wb') as f:
                f.write(data)
            print(f"SUCCESS: Saved {len(data):,} bytes to {dest_path}")
            return True
    except Exception as e:
        print(f"ERROR downloading {url}: {e}")
        return False

if __name__ == "__main__":
    success_count = 0
    for url, path in DOWNLOADS:
        if download_file(url, path):
            success_count += 1
        time.sleep(1)
    print(f"\nDownloaded {success_count}/{len(DOWNLOADS)} files.")

