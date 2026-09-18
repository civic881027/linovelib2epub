```diff
+ 🚀 真白萌小說站 https://masiro.me 已經得到支援 🚀
+ 🚩 輕小說文庫 https://www.wenku8.net/login.php 已經得到支援 🚩
```

# linovelib2epub

Crawl light novel from some websites and convert it to epub.

| 指標分類             | 指標集                                                                                                                                                                                                                                                                                                                                                          |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Software Version | [![Python Version](https://img.shields.io/badge/python>=3.10-blue)]()[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg?style=flat)](https://github.com/pypa/hatch)                                                                                                                                                          |
| Code Style       | [![flake8](https://img.shields.io/badge/linter-flake8-brightgreen)](https://github.com/PyCQA/flake8)                                                                                                                                                                                                                                                         |
| Code Statistics  | ![Lines of code](https://www.aschey.tech/tokei/github/lightnovel-center/linovelib2epub) ![PyPI - Downloads](https://img.shields.io/pypi/dm/linovelib2epub?color=blue&label=PyPI%20Download)                                                                                                                                                                  |
| Code Activity    | [![Hits-of-Code](https://hitsofcode.com/github/lightnovel-center/linovelib2epub?branch=main)](https://hitsofcode.com/github/lightnovel-center/linovelib2epub/view?branch=main) ![GitHub commit activity](https://img.shields.io/github/commit-activity/y/lightnovel-center/linovelib2epub)                                                                   |
| Code Quality     | [![Maintainability](https://api.codeclimate.com/v1/badges/c1a9eb78a26e8ffb1fdf/maintainability)](https://codeclimate.com/github/lightnovel-center/linovelib2epub/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/c1a9eb78a26e8ffb1fdf/test_coverage)](https://codeclimate.com/github/lightnovel-center/linovelib2epub/test_coverage) |
| CI Status        | [![Build and Publish](https://github.com/lightnovel-center/linovelib2epub/actions/workflows/build-and-publish.yml/badge.svg?branch=main)](https://github.com/lightnovel-center/linovelib2epub/actions/workflows/build-and-publish.yml)                                                                                                                       |

！該專案可能會用到OCR引擎來識別網頁上混淆的文字片段，但是目前市面上很多OCR引擎對python新版本的跟進非常滯後，因此推薦取下限而不是上限。
對於該專案，推薦鎖定**python 3.10**版本。

## preview

> A picture is worth a thousand words. Talk is cheap, show me the real effect.

![preview](./preview.gif)

> This demo uses [this screen recorder tool](https://github.com/faressoft/terminalizer) to record.

## Features

- [x] flexible `has_illustration` and `divide_volume` option for epub output
- [x] support downloading a certain volume of a novel
- [x] built-in http request retry mechanism to improve network fault tolerance
- [x] built-in random browser user_agent through fake_useragent library
- [x] built-in strict integrity check about image download
- [x] built-in mechanism for saving temporary book data by pickle library
- [x] use asyncio/multiprocessing to download images
- [x] support adding custom css styles to epub
- [x] 繁體中文網頁操作介面，關閉分頁後會自行結束
- [x] 單一執行檔，點兩下即可使用，不需安裝 Python

## 使用注意事項

在愉快的自動化爬蟲之前，有必要進行宣告。
網頁 Web
端總會存在請求錯誤，請求延遲，還需要不斷手動來點選【下一頁】按鈕來瀏覽閱讀，這無疑打斷了正常的閱讀 [心流](https://zh.wikipedia.org/wiki/
心流理論 )。
此專案的初衷正是為了 ** 構造良好流暢、不間斷的輕小說本地閱讀體驗 **。

但是，這不應該成為加重目標網站執行負載的理由。請正常使用本專案，請勿用於線性探測下載，或無限遍歷下載。

免責宣告：此專案不能保證它不會遭到濫用，對於有可能引發的不良後果，本專案概不負責。

## Supported  Websites (plan)

| 序號 | 網站名稱                                         | 語言    | 爬蟲難度 | 支援進度                                         | 備註                           | 技術難點                                                     |
|----|----------------------------------------------|-------|------|----------------------------------------------|------------------------------|----------------------------------------------------------|
| 1  | [嗶哩輕小說（Mobile）](https://www.bilinovel.com/) | 簡 / 繁 | 中😰  | <img src="./merrli.png" width="36">          | ` 不用登入 ` ` 一章多頁 `            | `JS 文字混淆 ` `JS 檔案隨機 ` ` 章節連結破損 ` `Cloudflare 保護 ` ` 限流 ` |
| 2  | [嗶哩輕小說（Web）](https://www.linovelib.com/)   | 簡 / 繁 | 中😰  | <img src="./merrli.png" width="36">          | ` 不用登入 ` ` 一章多頁 ` ` 網頁介面預設 ` | ` 字型混淆 ` ` 簡繁切換由前端 JS 完成 ` ` 瀏覽器語言為 zh-TW 時會被導向手機版 ` ` 限流 ` |
| 3  | ~~[輕之國度](https://www.lightnovel.us/)~~       | 簡 / 繁 | 高🤣  | <img src="./tearlaments-ban.png" width="36"> | ` 需要登入 `                     | ` 輕幣門檻 ` ` 導航混亂 `                                        |
| 4  | ~~[無限輕小說](https://www.8novel.com/)~~         | 繁     | 中😰  | <img src="./tearlaments-ban.png" width="36"> | ` 不用登入 ` ` 一章多頁 `            | N/A                                                      |
| 5  | [輕小說文庫](https://www.wenku8.net/)             | 簡 / 繁 | 低😆  | <img src="./merrli.png" width="36">          | ` 不用登入 ` ` 一章一頁 `            | 無                                                        |
| 6  | ~~[輕小說百科](https://lnovel.org/)~~             | 簡 / 繁 | 低😆  | <img src="./tearlaments-ban.png" width="36"> | ` 不用登入 ` ` 一章一頁 ` ` 插圖清晰度低 ` | N/A                                                      |
| 7  | [真白萌](https://masiro.me/admin/novels)        | 簡 / 繁 | 中😰  | <img src="./merrli.png" width="36">          | ` 一章一頁 `                     | ` 需要登入 ` ` 積分購買 ` ` 等級限制 ` `CF turnstile` ` 限流 `         |
| 8  | [百合會新站](https://www.yamibo.com/site/novel)   | 簡 / 繁 | 中😰  | 擱置                                           | ` 可選 [登入]` ` 一章一頁 `          | ` 付費章節需要登入 ` ` coin 購買 `                                 |

> 本分支的實測範圍：只有 **嗶哩輕小說（Web）** 經過完整實測，涵蓋繁體轉換、分卷輸出、圖片下載與網頁介面。
> 其餘網站沿用上游標示的支援狀態，本分支未加驗證。手機版在部分企業網路會被憑證攔截而連不上，屆時請改用 Web 版。

爬蟲友好度有兩個重要指標：

1. 訪問門檻。是否需要登陸、積分 / 代幣購買，等級限制。
2. 頁面結構。一章多頁，或者一章一頁。

優質的輕小說目標源標準：資源豐富，更新迅速，插圖清晰，爬蟲門檻合理。可以在 issue 發起補充。

## 快速開始（不需安裝 Python）

1. 到 [Releases](https://github.com/civic881027/linovelib2epub/releases) 下載對應作業系統的檔案。Windows 下載 `.exe`，Linux 下載 `.tar.gz` 後解開。
2. 點兩下執行，瀏覽器會自動開啟操作介面。
3. 填入書籍編號後按「開始下載」。關閉分頁或按「停止並結束程式」即可結束。

執行的電腦需要先安裝 Chrome 或 Edge 等 Chromium 系瀏覽器，程式靠它讀取網站。Windows 內建 Edge，通常不必另外安裝。

### 網頁介面

介面欄位全為繁體中文。預設來源是嗶哩輕小說電腦版繁體，章節與分頁間隔都預設 5 秒。

| 欄位 | 說明 |
|---|---|
| 書籍編號 | 網址 `novel/2978.html` 中間的那串數字 |
| 小說網站 | 預設嗶哩輕小說（電腦版・繁體），另有簡體、手機版、真白萌、輕小說文庫 |
| 章節間隔、分頁間隔 | 每次請求之間等待的秒數。太短容易被網站限流 |
| 輸出資料夾 | EPUB、圖片與執行紀錄的存放位置 |
| 瀏覽器路徑 | 留空會自動尋找已安裝的瀏覽器 |
| 每卷各存一個檔案 | 分卷輸出，檔名為 `NN.卷名.epub` |
| 自選卷數 | 先列出全部卷，勾選之後才開始下載 |

介面只監聽 `127.0.0.1`，而且每次啟動都會產生一組隨機權杖，避免其他網頁或程式操控爬蟲。網頁每秒回報一次狀態，關閉分頁約 12 秒後程式會自行結束，不會留下背景程序。

### 命令列

同一個執行檔帶上參數就是命令列模式：

```bash
# 下載某本書，分卷輸出
linovelib2epub 2978 --site linovelib_pc_traditional --chapter-crawl-delay 5 --page-crawl-delay 5 --divide-volume

# 看全部選項
linovelib2epub --help

# 指定網頁介面的連接埠
linovelib2epub gui --port 8000
```

從原始碼安裝時另有兩個固定入口：`linovelib2epub-gui` 只開網頁介面，`linovelib2epub-cli` 只走命令列。

### 自行打包

```bash
uv run --with pyinstaller pyinstaller linovelib2epub.spec
```

產物在 `dist/`。推送 `v` 開頭的標籤時，GitHub Actions 會自動建置雙平台執行檔並發布 Release。

## Installation

### install from source

1. clone this repo

```bash
git clone https://github.com/lightnovel-center/linovelib2epub.git
```

2. set up a clean local python venv

> See also: [creating-virtual-environments](https://docs.python.org/3/library/venv.html#creating-virtual-environments)

replace `py` with your real python command if needed. e.g. `python` or `python3`.

```bash
# Make sure you are under this project root folder: linovelib2epub/
# The following instructions are based on Windows 10.
# If you use a different os, please adjust it according to the actual situation.

# new a venv
py -m venv .venv

# activate venv
.\.venv\Scripts\activate

# install dependencies
py -m pip install -r requirements.txt

# install this package in local
python -m pip install -e .
```

## Some issues you might encounter during installation

> Microsoft Visual C++ 14.0 or greater is required

See this
link: [Which Microsoft Visual C++ compiler to use with a specific Python version ?](https://wiki.python.org/moin/WindowsCompilers#Which_Microsoft_Visual_C.2B-.2B-_compiler_to_use_with_a_specific_Python_version_.3F)

| **Visual C++** | **CPython**          |
|----------------|----------------------|
| 14.x           | 3.5 - 3.12+          |
| 10.0           | 3.3 - 3.4            |
| 9.0            | 2.6 - 2.7, 3.0 - 3.2 |

The key point is:

- Install [Microsoft Build Tools for Visual Studio 2019](https://visualstudio.microsoft.com/vs/older-downloads/). The
  version greater than 2019 may also can work.
- In Build tools, install `C++ build tools` and ensure the latest versions of
  `MSVCv142 - VS 2019 C++ x64/x86 build tools` and `Windows 10 SDK` are checked.
- The `setuptools` Python package version must be at least 34.4.0.

---

> Could not find function xmlCheckVersion in library libxml2. Is libxml2 installed?

Rollback python version to 3.10.X can work. The exact root cause is unknown now.

## Usage

### Linovelib

> target site: https://www.linovelib.com （Web）、https://www.bilinovel.com （Mobile）

> 2024-3-19 Update: Now linovelib also has a cloudflare access protection and requests rate limit.
> In order to decrease the probability of being banned by Linovelib, it is highly recommended to set the delay
> parameters as follows.
> You can tune the delay parameters to fit your actual network environment.
>
> The Linovelib target requires OCR technique to recognize some paragraphs in html. You need
> to install [tesseract](https://github.com/UB-Mannheim/tesseract) on your local pc. Make sure the `tesseract` command
> works
> in your pc by appending its location to system/user variables.

LinovelibMobile has two language versions(`zh/zh-CN` or `zh-TW/zh-HK`)  and two UI version(PC or mobile).

So the target website has 2 x 2 = 4 choices.

| website version                    | visit method                                                      | support status | target_site                               |
|------------------------------------|-------------------------------------------------------------------|----------------|-------------------------------------------|
| [PC](www.linovelib.com)  簡體        | browser set `zh/zh-CN` lang + click [簡體化]                         | ✅(recommend)   | `TargetSite.LINOVELIB_PC`                 |
| [PC](www.linovelib.com)  繁體        | browser set `zh/zh-CN` lang + click [繁體化]                         | ✅              | `TargetSite.LINOVELIB_PC_TRADITIONAL`     |
| ~~[Mobile 簡體](www.bilinovel.com)~~ | ~~browser set `zh/zh-CN` lang~~                                   | ❌              | `TargetSite.LINOVELIB_MOBILE`             |
| [Mobile](www.bilinovel.com)  繁體    | browser set `zh-TW/zh-HK` lang or not in Chinese Mainland network | ✅*(recommend)  | `TargetSite.LINOVELIB_MOBILE_TRADITIONAL` |

> 1.❌*: [2024-10-29]Now drission page library can only visit [mobile traditional version](www.bilinovel.com).
>
> 2.The Button "簡體化" in mobile traditional version does not work. So `TargetSite.LINOVELIB_MOBILE` target doesn't
> work. No workaround now.

Create a python file(e.g. `usage_demo.py`) and edit the content as follows:

Example usages:

- Specify target_site:

The code below takes PC + `zh/zh-CN` version as an example, adjust as needed if your target version is different.

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=2356, target_site=TargetSite.LINOVELIB_PC)

    # linovelib_epub = Linovelib2Epub(book_id=2356,target_site=TargetSite.LINOVELIB_PC_TRADITIONAL)

    # linovelib_epub = Linovelib2Epub(book_id=2356,target_site=TargetSite.LINOVELIB_MOBILE_TRADITIONAL)
    linovelib_epub.run()
```

- Set delay-related parameters[**mandatory**]

```python
from linovelib2epub import Linovelib2Epub

if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=2356, target_site=TargetSite.LINOVELIB_PC)
    linovelib_epub.run()
```

The default value of `chapter_crawl_delay` and `page_crawl_delay` are None. You MUST set them to reasonable values.

The example code is as follows to set the value of all delay parameters.

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=3721, target_site=TargetSite.LINOVELIB_PC,
                                    chapter_crawl_delay=5, page_crawl_delay=5)
    linovelib_epub.run()
```

- download only selected volume(s)[**optional**]

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == "__main__":
    linovelib_epub = Linovelib2Epub(book_id=2356, target_site=TargetSite.LINOVELIB_PC,
                                    select_volume_mode=True
                                    )
    linovelib_epub.run()
```

- disable network proxy[**optional**]

This project will disable any proxy settings when crawling. So you should manually activate it by `disable_proxy=False`
if you want to use your local proxy.

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == "__main__":
    linovelib_epub = Linovelib2Epub(book_id=2356, target_site=TargetSite.LINOVELIB_PC,
                                    disable_proxy=False,
                                    )
    linovelib_epub.run()
```

- view more details about crawling[**optional**]

Due to time sensitivity or environmental differences, web crawlers are very prone to failure. You can view more of the
underlying details if turn on debug mode.

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == "__main__":
    linovelib_epub = Linovelib2Epub(book_id=2356, target_site=TargetSite.LINOVELIB_PC,
                                    log_level="DEBUG",
                                    )
    linovelib_epub.run()
```

For more options, see the `Options` chapter below.

---

The following is a common crawler configuration that can be used as a reference.

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == "__main__":
    linovelib_epub = Linovelib2Epub(book_id=2356, target_site=TargetSite.LINOVELIB_PC,
                                    chapter_crawl_delay=5, page_crawl_delay=5,
                                    select_volume_mode=True,
                                    # disable_proxy=False,
                                    # log_level="DEBUG",
                                    )
    linovelib_epub.run()
```

If it finished without errors, you can see the epub file is under the folder where your python file is located.

### Masiro

> target site: https://masiro.me

> 2024-02-22 Update: Now Masiro has a very strict cloudflare turnstile protection and requests rate limit. The code has
> been
> refactored to bypass the [cloudflare turnstile](https://www.cloudflare.com/zh-cn/products/turnstile/) using a python
> library called [DrissionPage](https://github.com/g1879/DrissionPage). DrissionPage will auto-detect and use Chrome
> browser.
> If you encounter a path error of Chrome browser, please set the `browser_path` parameter to `Linovelib2Epub()`.

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=1039, target_site=TargetSite.MASIRO)
    linovelib_epub.run()
```

Or specify browser path:

```python
from linovelib2epub import Linovelib2Epub, TargetSite

# Chromium-based browser is ok
browser_path = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=1039, target_site=TargetSite.MASIRO, browser_path=browser_path)
    linovelib_epub.run()
```

Masiro is not the default target site, so you MUST specify `target_site` parameter as above.

And Masiro website need user login credential to view novel. You also MUST to create a config file named `.secrets.toml`
beside your python file `usage_demo.py`. For better explanation, Here's a reasonable directory organization:

```
linovelib2epub/
  ......
  .secrets.toml
  usage_demo.py
```

Then edit your `.secrets.toml` file:

```
MASIRO_LOGIN_USERNAME = '<your-masiro-username>'
MASIRO_LOGIN_PASSWORD = '<your-masiro-password>'
```

🚨 Don't leak your private account info!!! Be careful.

> Masiro 某些小說存在使用者等級限制，程式執行會發生什麼？

程式會給出提示，並直接退出。

> Masiro 某些小說的章節需要積分購買才能檢視，程式會如何處理？

登陸後，程式會記住你的當前積分餘額：

- 如果當前挑選的所有章節都是免費積分，或者你之前已經全部購買過，那麼程式會直接往下執行。
- 如果當前挑選的所有章節存在需要積分購買的情況，程式會再次提示，要求做出選擇，此時可以選擇退出或者選擇繼續。

### Wenku8

> target site: https://www.wenku8.net

```python
from linovelib2epub import Linovelib2Epub, TargetSite

if __name__ == '__main__':
    linovelib_epub = Linovelib2Epub(book_id=2961, target_site=TargetSite.WENKU8)
    linovelib_epub.run()
```

Don't need login, no threshold.

## Options

| Parameters                | type    | required | default        | description                                                                                                  |
|---------------------------|---------|----------|----------------|--------------------------------------------------------------------------------------------------------------|
| book_id                   | number  | YES      | None           | 書籍 ID。                                                                                                       |
| target_site               | Enum    | YES      | None           | 參閱 TargetSite python 列舉類以及使用文件。                                                                              |
| chapter_crawl_delay       | number  | YES*     | None           | 爬取每個章的延遲秒數 (s)。合理設定此引數可以降低被限流系統限制的頻率。目標是 linovelib 時必須設定此引數。                                                 |
| page_crawl_delay          | number  | YES*     | None           | 對於特定章，爬取每個頁面的延遲秒數 (s)。合理設定此引數可以降低被限流系統限制的頻率。目標是 linovelib 時必須設定此引數 。                                         |
| divide_volume             | boolean | NO       | False          | 是否分卷                                                                                                         |
| select_volume_mode        | boolean | NO       | False          | 選擇卷模式，它為 True 時 divide_volume 強制為 True。                                                                      |
| has_illustration          | boolean | NO       | True           | 是否下載插圖                                                                                                       |
| image_download_folder     | string  | NO       | "novel_images" | 圖片下載臨時資料夾. 不允許以相對路徑../ 開頭。                                                                                   |
| pickle_temp_folder        | string  | NO       | "pickle"       | pickle 臨時資料儲存的資料夾。                                                                                           |
| clean_artifacts           | boolean | NO       | True           | 是否刪除臨時資料 / 工件，指的是 pickle 和下載的圖片檔案。                                                                           |
| crawling_contentid        | string  | NO       | None           | 使用者自定義的正文內容的 id，用於快速響應網頁結構變化，[如何獲取?](docs/inspect-linovelib-contentid-as-a-regular-user.md)。目前僅適用於 linovelib。 |
| custom_style_cover        | string  | NO       | ''             | 自定義 cover.xhtml 的樣式                                                                                          |
| custom_style_nav          | string  | NO       | ''             | 自定義 nav.xhtml 的樣式                                                                                            |
| custom_style_chapter      | string  | NO       | ''             | 自定義每章 (?.xhtml) 的樣式                                                                                          |
| disable_proxy             | boolean | NO       | True           | 是否禁用所在的代理環境，預設禁用。如果你在本地使用網路代理，請務必留意是否應該設定該引數。                                                                |
| image_download_strategy   | string  | NO       | 'ASYNCIO'      | 列舉值："ASYNCIO"、"MULTIPROCESSING"、"MULTITHREADING"（未實現）                                                        |
| image_download_max_epochs | number  | NO       | 10             | 圖片下載的最大嘗試輪數。超過這個值則認為是網路中斷或者源圖片缺失，自動放棄。                                                                       |
| browser_path              | string  | NO       | None           | 瀏覽器的本地絕對路徑。                                                                                                  |
| headless                  | boolean | NO       | False          | 是否顯示瀏覽器視窗，預設為 False，即預設顯示。目前僅嗶哩輕小說支援該引數。                                                                     |
| http_timeout              | number  | NO       | 10             | 一個 HTTP 請求的超時等待時間 (秒)。代表 connect 和 read timeout。目前僅應用於 linovelib 頁面。                                         |
| http_retries              | number  | NO       | 10             | 當一個 HTTP 請求失敗後，重試的最大次數。 目前僅應用於 linovelib 頁面。                                                                 |

## Todo

- [] feat: add GOT-OCR2.0 engine alternative for linovelib site, support disable ocr(keep encrypted text.)
- [] feat: [option]add epubcheck for output files.
  see https://epubcheck.readthedocs.io/en/latest/readme.html#using-epubcheck-as-a-python-library
- [ ] quality: setup pytest and codecov
- [ ] quality: setup more formatter and linter for maintainability

## Under the hood

Here are some description about internal mechanism of this project.

| Target Site          | pages downloading | page success condition | challenge CloudFlare when page downloading | images downloading | use browser? |
|----------------------|-------------------|------------------------|--------------------------------------------|--------------------|--------------|
| Bilinovel(linovelib) | serial[^1]        | desired tag found      | No[^2]                                     | parallel           | DrissionPage |
| Masiro               | parallel[^3]      | desired tag found      | Yes                                        | parallel           | DrissionPage |
| Wenku8               | parallel          | simple status `200`    | N/A                                        | parallel           | aiohttp      |

[^1]: Bilinovel pages downloading is serial because its some chapter urls are broken, and we need to fix them.

[^2]: Bilinovel doesn't challenge CF when downloading one page, maybe it will stagnate into a endless loop.

[^3]: Masiro pages downloading is parallel but the actual effect is equal to serial because its strict requests rate
limit.

## Contributors

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-11-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/GOUKOU007"><img src="https://avatars.githubusercontent.com/u/40916324?v=4?s=60" width="60px;" alt="GokouRuri"/><br /><sub><b>GokouRuri</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3AGOUKOU007" title="Bug reports">🐛</a> <a href="https://github.com/lightnovel-center/linovelib2epub/commits?author=GOUKOU007" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/xxxfhy"><img src="https://avatars.githubusercontent.com/u/40598925?v=4?s=60" width="60px;" alt="xxxfhy"/><br /><sub><b>xxxfhy</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3Axxxfhy" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://foxlesbiao.github.io/"><img src="https://avatars.githubusercontent.com/u/41581909?v=4?s=60" width="60px;" alt="lesfox"/><br /><sub><b>lesfox</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3Afoxlesbiao" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://dongliteahouse.wordpress.com"><img src="https://avatars.githubusercontent.com/u/56831381?v=4?s=60" width="60px;" alt="Holence"/><br /><sub><b>Holence</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/commits?author=Holence" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://en.blog.nyaame.moe"><img src="https://avatars.githubusercontent.com/u/135048882?v=4?s=60" width="60px;" alt="Nikaidou Haruki"/><br /><sub><b>Nikaidou Haruki</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3Aharuki-nikaidou" title="Bug reports">🐛</a> <a href="https://github.com/lightnovel-center/linovelib2epub/commits?author=haruki-nikaidou" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://hitorinbc.com/"><img src="https://avatars.githubusercontent.com/u/33192552?v=4?s=60" width="60px;" alt="kaho"/><br /><sub><b>kaho</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3Akahosan" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Papersman"><img src="https://avatars.githubusercontent.com/u/58485012?v=4?s=60" width="60px;" alt="Papersman"/><br /><sub><b>Papersman</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3APapersman" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/inkroom"><img src="https://avatars.githubusercontent.com/u/27911304?v=4?s=60" width="60px;" alt="inkroom"/><br /><sub><b>inkroom</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3Ainkroom" title="Bug reports">🐛</a> <a href="https://github.com/lightnovel-center/linovelib2epub/commits?author=inkroom" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Kuan-Lun"><img src="https://avatars.githubusercontent.com/u/33048725?v=4?s=60" width="60px;" alt="Kuan-Lun"/><br /><sub><b>Kuan-Lun</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3AKuan-Lun" title="Bug reports">🐛</a> <a href="https://github.com/lightnovel-center/linovelib2epub/commits?author=GOUKOU007" title="Code">💻</a> </td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/CutyIMoDo"><img src="https://avatars.githubusercontent.com/u/59514546?v=4?s=60" width="60px;" alt="CutyIMoDo"/><br /><sub><b>CutyIMoDo</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3ACutyIMoDo" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/sweetnotice"><img src="https://avatars.githubusercontent.com/u/106159757?v=4?s=60" width="60px;" alt="Neco_arc"/><br /><sub><b>Neco_arc</b></sub></a><br /><a href="https://github.com/lightnovel-center/linovelib2epub/issues?q=author%3Asweetnotice" title="Bug reports">🐛</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## Acknowledgements

- [biliNovel2Epub](https://github.com/fangxx3863/biliNovel2Epub) => 嗶哩輕小說參考。
- [lightnovel-pydownloader](https://github.com/ilusrdbb/lightnovel-pydownloader) => 真白萌 / 輕之國度 / 百合會舊站參考。
- [bili_novel_packer](https://github.com/Montaro2017/bili_novel_packer) => 嗶哩輕小說 /wenku8 參考。
