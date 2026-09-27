# Notice to Action

**Public deployment:** See [বাংলা GitHub ও Streamlit Cloud guide](DEPLOY_GUIDE_BN.md). The project is deployable from a public GitHub repository; a working public URL requires a successful deployment and a separate live check.

A local Streamlit prototype that reads pasted text, text PDFs, or PNG/JPG notices. The user selects University notice, Scholarship, Job circular, or Other notice; the app displays matching source lines under that type's relevant fields, and separates labelled deadlines from publication and event dates. It does not decide eligibility, extract all information, or verify the issuing organisation. No paid model, external AI API, database, account registration, or automatic application submission. Rules can miss valid facts or return distracting lines; **always verify the original issuing organization's document**.

## Run locally

```cmd
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Run each command separately from the extracted folder; open the Local URL that appears. Keep `.streamlit/config.toml` beside `app.py` in the `.streamlit` folder so the light colors remain legible on machines using dark mode. For image OCR on Windows, install the separate Tesseract OCR executable with both English and Bengali language data. Pasted text and text PDFs work without it. `packages.txt` requests those executable packages when deploying to Streamlit Community Cloud.

### Image OCR on Windows (one-time setup)

`pip install pytesseract` installs a Python bridge, **not** the Tesseract OCR Windows program. Tesseract's [installation guide](https://tesseract-ocr.github.io/tessdoc/Installation.html) points Windows users to the [UB Mannheim installer](https://github.com/UB-Mannheim/tesseract/wiki). Install the 64-bit Windows build from that page, select **English** and **Bengali** in its additional language data choices, and keep the default location `C:\Program Files\Tesseract-OCR` (or add a custom location to Windows PATH). Do not extract the installer into your app folder. The app detects the default Windows program location even if that location is not yet on PATH.

In a fresh VS Code PowerShell terminal, verify the executable and the language data:

```powershell
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
```

The second command must list `eng` **and** `ben`. If the program is installed elsewhere, replace the path in both commands with the real `tesseract.exe` path. If `ben` is missing, add Bengali through the installer or get the official [`ben.traineddata`](https://github.com/tesseract-ocr/tessdata/blob/main/ben.traineddata) and place it in Tesseract's `tessdata` directory. Then stop Streamlit with Ctrl+C, open a new terminal if PATH was changed, and restart the app. Try a clear public PNG or JPG; inspect the extracted text shown in the app and verify all detected fields against the original.

If updating an earlier local demo: extract the new ZIP and copy all its files and folders into the existing project folder, replacing matching files. Keep the existing `.venv` folder. Stop Streamlit with Ctrl+C, then run `.venv\Scripts\python.exe -m streamlit run app.py` again. A fresh install of the Python dependencies is unnecessary when only the visual design changes.

### What each selected notice type shows

- University: audience and exceptions, student action, supporting documents, and place/channel.
- Scholarship: programme, conditions, funding that is actually stated, documents, and how to apply.
- Job: position, qualification, pay if stated, documents, application method, and workplace or next step.
- Other: subject, affected people, actions, payments if stated, and where to find further information. This covers notices such as a review or appeal that do not belong to the three application types.

All four show dates by **stated purpose** and let the user inspect the exact text read from the file. A matching source line is a candidate, not a corrected or confirmed answer. An absent field says "Not clearly found", not "Not required". Scanned PDFs are not OCRed; upload a clear PNG/JPG of the page. Images run through Tesseract in the selected OCR language, which can misread characters, columns, amounts, and dates. A warning asks the user to compare the OCR text against the original image. No image-recognition accuracy is claimed.

For image uploads, choose **English** for predominantly English notices and **English + Bengali** for Bengali or mixed notices. When the image's shorter side is under 900 pixels, the app enlarges it in memory and applies grayscale auto-contrast before OCR. This helped on one supplied 447×447 English job poster, but cannot recover details absent from a compressed original and must not be interpreted as general OCR accuracy. Short headings such as `Deadline:` may have the date on the next extracted line. The original image resolution is shown and the app still warns on small images.

For example, a 426×719 pixel scan of a dense Bengali Bar Council review notice produced heavily corrupted OCR. The prototype warns on images with either dimension below 900 pixels. It cannot reconstruct unreadable words or dates from that scan; provide an original text PDF, a clearer scan, or corrected pasted text. Selecting Other notice fixes a category mismatch but does not repair OCR.

Offline checks: `python check_extractor.py` and `python check_parser.py`. The parser checks use synthetic paraphrases of three notice types, including bilingual dates and an institution-dependent deadline. They do not constitute an evaluation on actual scanned notices.

## Publish a free public link

1. Create a **new** GitHub repository for this project. Upload `app.py`, `extractor.py`, `notice_parser.py`, `check_extractor.py`, `check_parser.py`, `requirements.txt`, `packages.txt`, this `README.md`, `assets/notice-illustration.svg`, and `.streamlit/config.toml`, keeping both folders intact. Do not include `.venv`, private notices or uploaded files.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub. Choose **Create app**, select the repository, `main` branch, and entry point `app.py`.
3. Deploy and open the generated `*.streamlit.app` link from a different browser or a private window. Test pasted text, a text PDF, and one clear English/Bangla image. Check that the image packages install successfully and no upload data is saved to GitHub.
4. Set visibility to **public** and share the app URL. Availability and resource limits are controlled by the hosting platform; free hosting does not guarantee uninterrupted service or performance under heavy traffic.

## Checks and boundaries

- File limit: 8 MB; PDF limit: 15 pages; image limit: 20 megapixels; extracted text limit: 300,000 characters.
- No file is deliberately saved to disk or submitted to a third-party AI API; the hosting service receives uploaded file bytes to run the app. Avoid private identifiers or confidential documents.
- Dates need an explicit role cue on the same line; for short headings the immediately following line may provide a full date. The app does not assign an unlabeled date to an application. Parsed numeric dates assume DD/MM/YYYY; ambiguous date formats still need human verification.
- The category-specific details are matching **source lines**, not a verified summarized checklist. Missing results mean “not clearly found,” never that the notice contains no requirements.
- Scanned PDFs may need page images for OCR. OCR accuracy, Bangla text extraction, PDF layout and live public deployment have **not** been benchmarked. The 52-record source index assembled separately consists of listing metadata, not labeled training data and is not required to run the app.
