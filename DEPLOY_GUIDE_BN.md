# Notice to Action: GitHub থেকে public app

এই repository-এর `app.py` হলো Streamlit app। GitHub-এ code রাখা আর app-এর public URL পাওয়া দুটি আলাদা কাজ। Streamlit Community Cloud-এ deploy সম্পন্ন হলে share করার মতো URL পাওয়া যায়। Localhost URL অন্যের কম্পিউটারে কাজ করবে না।

## ১. GitHub-এ project upload

1. ZIP Extract All করো। `app.py` যেখানে আছে, সেটিই project folder। `.venv` বা নিজের notice/image এই folder-এর বাইরে রাখো।
2. GitHub-এ **New repository** → নাম `notice-to-action` → **Public** → **Create repository**। নিজের account-এ আগে থেকে একই নামের repository থাকলে নতুন নাম দাও।
3. খালি repository-র **uploading an existing file** link চাপো। `app.py`, `extractor.py`, `notice_parser.py`, `requirements.txt`, `packages.txt`, `.gitignore`, `README.md`, `DEPLOY_GUIDE_BN.md`, `check_extractor.py`, `check_parser.py`, `assets` folder-এর SVG এবং `.streamlit/config.toml` upload করো। GitHub browser upload-এ nested folder ধরে রাখা কঠিন হলে নিচের command-line বিকল্প ব্যবহার করো।
4. File list-এ `assets/notice-illustration.svg` এবং `.streamlit/config.toml` ঠিক জায়গায় আছে কি না দেখো। ZIP নিজে upload করলে Cloud app খুঁজে পাবে না। `upload/`, ব্যক্তিগত ছবি/notice, `.venv`, `.streamlit/secrets.toml` upload কোরো না।

### Windows PowerShell command-line বিকল্প

Git for Windows ইনস্টল করা থাকলে VS Code-এ **File → Open Folder** দিয়ে extracted project folder খুলে Terminal → New Terminal। প্রতিটি command আলাদা করে চালাও; `YOUR_USERNAME` নিজের GitHub username দিয়ে বদলাও:

```powershell
git init
git add .
git status
git commit -m "Add Notice to Action public demo"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/notice-to-action.git
git push -u origin main
```

`git status`-এ নিজের notice, ছবি, `.venv` দেখালে commit/push-এর আগে সেগুলো বাদ দাও। GitHub login চাইলে browser-এ নির্দেশনা অনুসরণ করো।

## ২. Free public link তৈরি

1. [share.streamlit.io](https://share.streamlit.io/) খুলে GitHub দিয়ে sign in করো।
2. **Create app / Deploy an app** চাপো; নিজের repository এবং `main` branch বেছে নাও। **Main file path:** `app.py`। Deploy setup-এ Python version বেছে নেওয়ার সুযোগ থাকলে **3.11** বেছে নাও (local development-ও 3.11)।
3. **Deploy** চাপো। Python dependencies `requirements.txt` থেকে এবং Linux Tesseract OCR ও English/Bengali language data `packages.txt` থেকে install হবে। Build log-এ কোনো dependency error থাকলে সেই error দেখে ঠিক করতে হবে; deploy সফল হয়েছে ধরে নিও না।
4. যে `https://...streamlit.app` URL পাওয়া যাবে, সেটি অন্য browser বা incognito window-তে খুলে **Paste text**, text PDF এবং স্পষ্ট English ও Bengali ছবি পরীক্ষা করো। উপরে image-language dropdown ঠিক করে দাও। প্রতিটি তারিখ ও সংখ্যা মূল notice-এর সঙ্গে যাচাই করো। তারপর সেই URL share করো।

## সীমা

- Free hosting ব্যবহার করা যায়, তবে platform-এর resource limit, sleep বা service availability তোমার নিয়ন্ত্রণে নেই। অনেক ব্যবহারকারী একসঙ্গে এলে ধীর হতে পারে।
- App-এর code আলাদাভাবে upload করা notice file disk-এ সংরক্ষণ করে না। তবে browser থেকে file hosting provider-এর server-এ যায়; ব্যক্তিগত পরিচয়পত্র বা গোপন notice upload করতে বলা যাবে না।
- এই app সবার জন্য পরীক্ষামূলক: কোনো notice-এর সত্যতা, আবেদনযোগ্যতা, deadline বা OCR accuracy নিশ্চিত করে না। `Text read` tab ও মূল প্রকাশকের notice মিলিয়ে দেখো।
