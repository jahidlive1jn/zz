#!/usr/bin/env python3
"""
GitHub YouTube Streamer - Fully Automatic Setup Tool
তোমার PC বন্ধ থাকলেও YouTube Live চলবে!
100% Automatic - কোনো manual কাজ নেই!
"""

import os
import sys
import subprocess
import time
import json
import requests
import base64
from pathlib import Path

# Import nacl only when needed
try:
    from nacl import encoding, public
    NACL_AVAILABLE = True
except ImportError:
    NACL_AVAILABLE = False

class GitHubAutoSetup:
    def __init__(self):
        self.print_banner()
        
        # File paths
        self.setup_file = "setup_github.txt"
        self.streamer_file = "streamer.py"
        self.requirements_file = "requirements.txt"
        self.workflow_template = ".githubworkflowsyoutube-live.yml.txt"
        
        # Config variables
        self.stream_key = None
        self.video_url = None
        self.quality = None
        self.aspect_ratio = None
        self.github_token = None
        self.repo_name = None
        self.username = None
        self.base_dir = os.getcwd()
        
    def print_banner(self):
        print("\n" + "=" * 70)
        print("🚀 GitHub YouTube Streamer - 100% Automatic Setup")
        print("=" * 70)
        print("✅ Multiple GitHub accounts supported!")
        print("✅ সব কিছু automatic - কোনো manual কাজ নেই!")
        print("✅ তোমার PC বন্ধ থাকলেও stream চলবে!")
        print("=" * 70 + "\n")
    
    def check_files(self):
        """প্রয়োজনীয় files check করো"""
        print("📁 Checking required files...")
        
        files_needed = {
            self.streamer_file: "Streamer script",
            self.requirements_file: "Python dependencies",
        }
        
        # Check for workflow template with multiple possible names
        workflow_found = False
        possible_workflow_names = [
            '.githubworkflowsyoutube-live.yml.txt',
            'youtube-live.yml.txt',
            'youtube-live.yml',
            'workflow.yml'
        ]
        
        for wf_name in possible_workflow_names:
            wf_path = os.path.join(self.base_dir, wf_name)
            if os.path.exists(wf_path):
                self.workflow_template = wf_name
                workflow_found = True
                print(f"  ✅ {wf_name} - Workflow template")
                break
        
        if not workflow_found:
            print(f"  ❌ Workflow template MISSING!")
            print(f"     Looking for: {', '.join(possible_workflow_names)}")
            return False
        
        missing = []
        for file, desc in files_needed.items():
            file_path = os.path.join(self.base_dir, file)
            if os.path.exists(file_path):
                print(f"  ✅ {file} - {desc}")
            else:
                print(f"  ❌ {file} - {desc} MISSING!")
                missing.append(file)
        
        if missing:
            print(f"\n❌ Error: {len(missing)} file(s) missing!")
            print("💡 Make sure all files are in the same folder:")
            for f in missing:
                print(f"   - {f}")
            return False
        
        print(f"\n✅ All required files found!")
        print(f"   Note: setup_github.txt not needed in repo (only for local config)\n")
        return True
    
    def read_setup_config(self):
        """setup_github.txt থেকে config পড়ো"""
        print("📖 Reading configuration from setup_github.txt...")
        
        try:
            config_path = os.path.join(self.base_dir, self.setup_file)
            with open(config_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            if len(lines) < 6:
                print("❌ Error: setup_github.txt needs 6 lines:")
                print("   Line 1: YouTube Stream Key")
                print("   Line 2: Video URL")
                print("   Line 3: Quality (720p, 1080p, etc.)")
                print("   Line 4: Aspect Ratio (16:9, 9:16, etc.)")
                print("   Line 5: GitHub Personal Access Token")
                print("   Line 6: Repository Name")
                print("\n💡 How to get GitHub Token:")
                print("   1. Go to: https://github.com/settings/tokens")
                print("   2. Generate new token (classic)")
                print("   3. Select: repo, workflow, admin:repo_hook")
                print("   4. Copy token and paste in setup_github.txt")
                return False
            
            self.stream_key = lines[0]
            self.video_url = lines[1]
            self.quality = lines[2]
            self.aspect_ratio = lines[3]
            self.github_token = lines[4]
            self.repo_name = lines[5]
            
            print(f"  ✅ Stream Key: {self.stream_key[:8]}...{self.stream_key[-4:]}")
            print(f"  ✅ Video URL: {self.video_url[:50]}...")
            print(f"  ✅ Quality: {self.quality}")
            print(f"  ✅ Aspect Ratio: {self.aspect_ratio}")
            print(f"  ✅ GitHub Token: {self.github_token[:8]}...{self.github_token[-4:]}")
            print(f"  ✅ Repo Name: {self.repo_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error reading setup file: {e}")
            return False
    
    def verify_github_token(self):
        """GitHub token verify করো"""
        print("\n🔐 Verifying GitHub token...")
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                self.username = user_data['login']
                print(f"  ✅ Token valid for user: {self.username}")
                return True
            else:
                print(f"  ❌ Invalid token! Status: {response.status_code}")
                print("  💡 Generate new token at: https://github.com/settings/tokens")
                return False
                
        except Exception as e:
            print(f"  ❌ Error verifying token: {e}")
            return False
    
    def check_git_installed(self):
        """Git installed আছে কিনা check করো"""
        print("\n🔍 Checking Git installation...")
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                print(f"  ✅ {result.stdout.strip()}")
                return True
        except:
            pass
        
        print("❌ Git is not installed!")
        print("💡 Please install Git first:")
        print("   Windows: https://git-scm.com/download/win")
        return False
    
    def create_github_repo(self):
        """GitHub API দিয়ে repo create করো"""
        print("\n🏗️  Creating GitHub repository...")
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Check if repo exists
        check_url = f'https://api.github.com/repos/{self.username}/{self.repo_name}'
        try:
            response = requests.get(check_url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"  ⚠️  Repository '{self.repo_name}' already exists!")
                print(f"  ℹ️  Will update existing repository")
                return True
        except:
            pass
        
        # Create new repo
        data = {
            'name': self.repo_name,
            'description': 'Automated content streaming',
            'private': True,  # Private repo
            'auto_init': True
        }
        
        try:
            response = requests.post(
                'https://api.github.com/user/repos',
                headers=headers,
                json=data,
                timeout=15
            )
            
            if response.status_code == 201:
                print(f"  ✅ Repository created successfully!")
                time.sleep(3)  # Wait for repo to be ready
                return True
            else:
                print(f"  ❌ Failed to create repository")
                print(f"  Status: {response.status_code}")
                print(f"  Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error creating repository: {e}")
            return False
    
    def upload_file_to_github(self, file_path, content, message):
        """GitHub API দিয়ে file upload করো"""
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Encode content to base64
        content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        # Check if file already exists
        get_url = f'https://api.github.com/repos/{self.username}/{self.repo_name}/contents/{file_path}'
        
        sha = None
        try:
            response = requests.get(get_url, headers=headers, timeout=10)
            if response.status_code == 200:
                sha = response.json().get('sha')
        except:
            pass
        
        # Upload or update file
        data = {
            'message': message,
            'content': content_encoded,
            'branch': 'main'
        }
        
        if sha:
            data['sha'] = sha
        
        try:
            response = requests.put(get_url, headers=headers, json=data, timeout=15)
            
            if response.status_code in [200, 201]:
                return True
            else:
                # Try with master branch
                data['branch'] = 'master'
                response = requests.put(get_url, headers=headers, json=data, timeout=15)
                return response.status_code in [200, 201]
                
        except Exception as e:
            print(f"    Error uploading {file_path}: {e}")
            return False
    
    def upload_files_to_repo(self):
        """সব files GitHub এ upload করো"""
        print("\n📤 Uploading files to GitHub...")
        
        files_to_upload = []
        
        # Read streamer.py
        streamer_path = os.path.join(self.base_dir, self.streamer_file)
        if os.path.exists(streamer_path):
            with open(streamer_path, 'r', encoding='utf-8') as f:
                files_to_upload.append(('streamer.py', f.read(), 'Add streamer.py'))
        
        # Read requirements.txt
        req_path = os.path.join(self.base_dir, self.requirements_file)
        if os.path.exists(req_path):
            with open(req_path, 'r', encoding='utf-8') as f:
                files_to_upload.append(('requirements.txt', f.read(), 'Add requirements.txt'))
        
        # Read workflow template
        workflow_path = os.path.join(self.base_dir, self.workflow_template)
        if os.path.exists(workflow_path):
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_content = f.read()
                files_to_upload.append(('.github/workflows/youtube-live.yml', workflow_content, 'Add workflow'))
        
        # Create README (minimal, no details)
        readme_content = f"""# 24/7 Live Stream

Automated streaming service.

Quality: {self.quality}
"""
        files_to_upload.append(('README.md', readme_content, 'Add README'))
        
        # Upload all files
        success_count = 0
        for file_path, content, message in files_to_upload:
            print(f"  📤 Uploading {file_path}...", end=' ')
            if self.upload_file_to_github(file_path, content, message):
                print("✅")
                success_count += 1
            else:
                print("❌")
        
        print(f"\n  ✅ Uploaded {success_count}/{len(files_to_upload)} files successfully!")
        return success_count > 0
    
    def encrypt_secret(self, public_key: str, secret_value: str) -> str:
        """Encrypt a secret using the repository's public key"""
        if not NACL_AVAILABLE:
            raise ImportError("PyNaCl not available")
        
        from nacl import encoding, public as nacl_public
        
        public_key_bytes = base64.b64decode(public_key)
        public_key_obj = nacl_public.PublicKey(public_key_bytes)
        sealed_box = nacl_public.SealedBox(public_key_obj)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")
    
    def set_github_secrets(self):
        """GitHub API দিয়ে secrets set করো"""
        global NACL_AVAILABLE
        
        print("\n🔐 Setting GitHub secrets...")
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        secrets = {
            'YOUTUBE_STREAM_KEY': self.stream_key,
            'VIDEO_URL': self.video_url,
            'VIDEO_QUALITY': self.quality,
            'ASPECT_RATIO': self.aspect_ratio
        }
        
        # Check if PyNaCl is available
        if not NACL_AVAILABLE:
            print("  ⚠️  PyNaCl not installed. Installing now...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pynacl'], 
                             check=True, capture_output=True, timeout=60)
                print("  ✅ PyNaCl installed!")
                
                # Reload the module
                try:
                    from nacl import encoding, public
                    NACL_AVAILABLE = True
                    print("  ✅ PyNaCl loaded successfully!")
                except:
                    print("  ⚠️  Please restart the script")
                    return self.set_secrets_alternative()
                    
            except Exception as e:
                print(f"  ⚠️  Could not install PyNaCl: {e}")
                return self.set_secrets_alternative()
        
        # Get public key for encryption
        key_url = f'https://api.github.com/repos/{self.username}/{self.repo_name}/actions/secrets/public-key'
        
        try:
            key_response = requests.get(key_url, headers=headers, timeout=10)
            if key_response.status_code != 200:
                print(f"  ⚠️  Could not get public key. Trying alternative method...")
                return self.set_secrets_alternative()
            
            key_data = key_response.json()
            public_key = key_data['key']
            key_id = key_data['key_id']
            
            # Set each secret
            success_count = 0
            for secret_name, secret_value in secrets.items():
                try:
                    print(f"  🔐 Setting {secret_name}...", end=' ')
                    
                    # Encrypt the secret
                    encrypted_value = self.encrypt_secret(public_key, secret_value)
                    
                    # Set the secret
                    secret_url = f'https://api.github.com/repos/{self.username}/{self.repo_name}/actions/secrets/{secret_name}'
                    data = {
                        'encrypted_value': encrypted_value,
                        'key_id': key_id
                    }
                    
                    response = requests.put(secret_url, headers=headers, json=data, timeout=10)
                    
                    if response.status_code in [201, 204]:
                        print("✅")
                        success_count += 1
                    else:
                        print(f"❌ (Status: {response.status_code})")
                        
                except Exception as e:
                    print(f"❌ ({str(e)[:30]}...)")
            
            if success_count == len(secrets):
                print(f"\n  ✅ All {success_count} secrets set successfully!")
                return True
            else:
                print(f"\n  ⚠️  Set {success_count}/{len(secrets)} secrets")
                return success_count > 0
            
        except Exception as e:
            print(f"  ❌ Error setting secrets: {e}")
            return self.set_secrets_alternative()
    
    def set_secrets_alternative(self):
        """Alternative method using gh CLI"""
        print("  ℹ️  Trying GitHub CLI method...")
        
        secrets = {
            'YOUTUBE_STREAM_KEY': self.stream_key,
            'VIDEO_URL': self.video_url,
            'VIDEO_QUALITY': self.quality,
            'ASPECT_RATIO': self.aspect_ratio
        }
        
        success_count = 0
        for secret_name, secret_value in secrets.items():
            try:
                cmd = [
                    'gh', 'secret', 'set', secret_name,
                    '--body', secret_value,
                    '--repo', f'{self.username}/{self.repo_name}'
                ]
                
                env = os.environ.copy()
                env['GH_TOKEN'] = self.github_token
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, env=env)
                
                if result.returncode == 0:
                    print(f"  ✅ Set secret: {secret_name}")
                    success_count += 1
                else:
                    print(f"  ⚠️  Could not set: {secret_name}")
                    
            except:
                print(f"  ⚠️  Could not set: {secret_name}")
        
        if success_count == 0:
            print("\n  ⚠️  Secrets not set automatically!")
            print(f"  💡 Please set them manually at:")
            print(f"     https://github.com/{self.username}/{self.repo_name}/settings/secrets/actions")
            print("\n  📋 Secrets to add:")
            for name, value in secrets.items():
                print(f"     {name} = {value[:30]}...")
        
        return success_count > 0
    
    def trigger_workflow(self):
        """Workflow manually trigger করো"""
        print("\n🚀 Triggering workflow...")
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f'https://api.github.com/repos/{self.username}/{self.repo_name}/actions/workflows/youtube-live.yml/dispatches'
        
        # Try main branch first
        for branch in ['main', 'master']:
            data = {'ref': branch}
            
            try:
                response = requests.post(url, headers=headers, json=data, timeout=10)
                
                if response.status_code == 204:
                    print(f"  ✅ Workflow triggered successfully on {branch} branch!")
                    return True
            except:
                pass
        
        print(f"  ⚠️  Could not trigger workflow automatically")
        print(f"  💡 Trigger manually from:")
        print(f"     https://github.com/{self.username}/{self.repo_name}/actions")
        return True
    
    def run(self):
        """Main execution"""
        
        # Step 1: Check files
        if not self.check_files():
            return False
        
        # Step 2: Read config
        if not self.read_setup_config():
            return False
        
        # Step 3: Verify GitHub token
        if not self.verify_github_token():
            return False
        
        # Step 4: Check Git
        if not self.check_git_installed():
            return False
        
        # Step 5: Create GitHub repo
        if not self.create_github_repo():
            return False
        
        # Step 6: Upload files
        if not self.upload_files_to_repo():
            print("  ⚠️  Some files failed to upload")
        
        # Step 7: Set secrets
        self.set_github_secrets()
        
        # Step 8: Trigger workflow
        self.trigger_workflow()
        
        # Success message
        print("\n" + "=" * 70)
        print("🎉 SUCCESS! Your automated stream is ready!")
        print("=" * 70)
        print(f"📺 Repository: https://github.com/{self.username}/{self.repo_name}")
        print(f"🚀 Actions: https://github.com/{self.username}/{self.repo_name}/actions")
        print(f"🔒 Repository is PRIVATE (only you can see)")
        print("\n✅ Stream will start automatically!")
        print("✅ Your PC can be OFF now!")
        print("=" * 70 + "\n")
        
        return True

def main():
    """Main function"""
    
    try:
        setup = GitHubAutoSetup()
        success = setup.run()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()