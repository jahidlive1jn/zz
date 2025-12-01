#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import json
import requests
import base64
from pathlib import Path

try:
    from nacl import encoding, public
    NACL_AVAILABLE = True
except ImportError:
    NACL_AVAILABLE = False


class GitHubAutoSetup:
    def __init__(self):
        self.print_banner()

        self.setup_file = "setup_github.txt"
        self.streamer_file = "streamer.py"
        self.requirements_file = "requirements.txt"

        # 🔥 FINAL FIXED WORKFLOW PATH
        self.workflow_template = ".github/workflows/youtube-live.yml"

        self.stream_key = None
        self.video_url = None
        self.quality = None
        self.aspect_ratio = None
        self.github_token = None
        self.repo_name = None
        self.username = None
        self.base_dir = os.getcwd()

    def print_banner(self):
        print("\n===============================================")
        print("🚀 GitHub 24/7 YouTube Auto Streamer")
        print("===============================================\n")

    def check_files(self):
        print("📁 Checking required files...\n")

        # must exist
        must_files = [
            self.streamer_file,
            self.requirements_file,
            self.workflow_template
        ]

        missing = []
        for f in must_files:
            if not os.path.exists(f):
                print(f"❌ Missing: {f}")
                missing.append(f)
            else:
                print(f"✅ Found: {f}")

        if missing:
            print("\n❌ ERROR: Required workflow / files missing!")
            return False

        print("\n✅ All necessary files OK!\n")
        return True

    def read_setup_config(self):
        print("📖 Reading setup_github.txt...")

        try:
            with open(self.setup_file, "r") as f:
                lines = [x.strip() for x in f.readlines() if x.strip()]

            if len(lines) < 6:
                print("❌ setup_github.txt must have 6 lines!")
                return False

            self.stream_key = lines[0]
            self.video_url = lines[1]
            self.quality = lines[2]
            self.aspect_ratio = lines[3]
            self.github_token = lines[4]
            self.repo_name = lines[5]

            print("✅ Config loaded successfully!\n")
            return True

        except Exception as e:
            print(f"❌ Error reading setup file: {e}")
            return False

    def verify_github_token(self):
        print("🔐 Verifying GitHub token...")

        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        try:
            r = requests.get("https://api.github.com/user", headers=headers)
            if r.status_code == 200:
                self.username = r.json()["login"]
                print(f"✅ Valid token for user: {self.username}")
                return True
            else:
                print("❌ Invalid GitHub token!")
                return False

        except Exception as e:
            print("❌ Token verify failed:", e)
            return False

    def create_github_repo(self):
        print("\n🏗 Creating repository...")

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        check = f"https://api.github.com/repos/{self.username}/{self.repo_name}"
        r = requests.get(check, headers=headers)

        if r.status_code == 200:
            print("⚠️ Repo already exists. Using existing repo.")
            return True

        data = {
            "name": self.repo_name,
            "private": False,
            "description": "24/7 YouTube Auto Streamer",
            "auto_init": True
        }

        r = requests.post("https://api.github.com/user/repos", headers=headers, json=data)
        if r.status_code == 201:
            print("✅ Repository created!")
            time.sleep(2)
            return True
        else:
            print("❌ Repo create failed!", r.text)
            return False

    def upload_file(self, path, content):
        url = f"https://api.github.com/repos/{self.username}/{self.repo_name}/contents/{path}"

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        content_b64 = base64.b64encode(content.encode()).decode()

        # check exists
        r = requests.get(url, headers=headers)
        sha = None
        if r.status_code == 200:
            sha = r.json()["sha"]

        data = {
            "message": f"Upload {path}",
            "content": content_b64,
            "branch": "main"
        }

        if sha:
            data["sha"] = sha

        r = requests.put(url, headers=headers, json=data)
        return r.status_code in [200, 201]

    def upload_all_files(self):
        print("\n📤 Uploading files...")

        # upload streamer.py
        with open("streamer.py", "r") as f:
            self.upload_file("streamer.py", f.read())

        # upload requirements
        with open("requirements.txt", "r") as f:
            self.upload_file("requirements.txt", f.read())

        # upload workflow
        with open(".github/workflows/youtube-live.yml", "r") as f:
            self.upload_file(".github/workflows/youtube-live.yml", f.read())

        print("✅ All files uploaded!\n")

    def set_secrets(self):
        print("🔐 Adding GitHub Secrets...")

        secrets = {
            "YOUTUBE_STREAM_KEY": self.stream_key,
            "VIDEO_URL": self.video_url,
            "VIDEO_QUALITY": self.quality,
            "ASPECT_RATIO": self.aspect_ratio
        }

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # GET public key
        url = f"https://api.github.com/repos/{self.username}/{self.repo_name}/actions/secrets/public-key"
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            print("❌ Cannot fetch repo secret key")
            return False

        key = r.json()
        public_key = key["key"]
        key_id = key["key_id"]

        from nacl import public as nacl_public

        def encrypt(public_key: str, value: str) -> str:
            pk = nacl_public.PublicKey(base64.b64decode(public_key))
            box = nacl_public.SealedBox(pk)
            encrypted = box.encrypt(value.encode())
            return base64.b64encode(encrypted).decode()

        # upload each secret
        for name, value in secrets.items():
            encrypted = encrypt(public_key, value)

            secret_url = f"https://api.github.com/repos/{self.username}/{self.repo_name}/actions/secrets/{name}"
            r = requests.put(secret_url, headers=headers, json={
                "encrypted_value": encrypted,
                "key_id": key_id
            })

            if r.status_code in [201, 204]:
                print(f"✅ Secret added: {name}")
            else:
                print(f"❌ Failed to add secret: {name}")

        return True

    def run(self):
        if not self.check_files(): return
        if not self.read_setup_config(): return
        if not self.verify_github_token(): return
        if not self.create_github_repo(): return
        self.upload_all_files()
        self.set_secrets()

        print("\n🎉 SETUP COMPLETE!")
        print("Go to GitHub → Actions → Run Workflow\n")


def main():
    setup = GitHubAutoSetup()
    setup.run()


if __name__ == "__main__":
    main()
