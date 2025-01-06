## Overview
WCAG Non-Text Content Checker is a Python tool that automatically analyzes web pages for WCAG 1.1.1 compliance by identifying and extracting non-text content (images, videos, audio) using Selenium WebDriver and Claude AI. The tool provides detailed reports in JSON format, including XPath locations and descriptions of non-text elements.

## Installation
1. Clone the repository
```bash
git clone https://github.com/daishir0/wcag_non_text_checker.git
cd wcag_non_text_checker
```

2. Install Chrome and ChromeDriver
For Ubuntu/Debian:
```bash
# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f

# Install ChromeDriver
sudo apt-get install chromium-chromedriver
```

For other operating systems, please download and install:
- Google Chrome: https://www.google.com/chrome/
- ChromeDriver: https://chromedriver.chromium.org/downloads

3. Install Python dependencies
```bash
pip install -r requirements.txt
```

4. Configure the settings
```bash
cp config.sample.py config.py
```
Edit config.py with your settings:
- Set your Anthropic API key
- Adjust Chrome and ChromeDriver paths according to your environment
- Set DEBUG flag if needed

## Usage
Run the script with a target URL:
```bash
python wcag_non_text_checker.py https://example.com
```

The tool will output JSON-formatted results containing:
- XPath locations of non-text content
- Descriptions of each element
- Element types (images, videos, audio)

### Example Output
```bash
$ python wcag_non_text_checker.py https://www.yahoo.co.jp/
{
  "Non-text Contents": [
    {
      "xpath": "//div[contains(@class, \"_7uaWVw_YSgf_GKoctUM12\")]/span/img",
      "description": "記事に関連する全画像サムネイル"
    },
    {
      "xpath": "//div[contains(@class, \"_7uaWVw_YSgf_GKoctUM12\")]/span/picture/img",
      "description": "画像サムネイル（picture要素内）"
    },
    {
      "xpath": "//div[contains(@class, \"_2dkkFdF6iwwsvj59371Trg\")]/span[contains(@class, \"_1I_5hzC8N7rC_DyCqrkXsj\")]",
      "description": "コメント数に関連するアイコン"
    },
    {
      "xpath": "//span[contains(@class, \"_2Uq6Pw5lfFfxr_OD36xHp6\")]",
      "description": "様々なアイコンと画像"
    },
    {
      "xpath": "//div[contains(@class, \"_2MXJ1iB31yVKsR-3VMKR4N\")]/span[contains(@class, \"_2VDw54wcDejORZkozpOysW\")][contains(text(), \"0:\")]",
      "description": "動画の長さが表示されている要素"
    }
  ]
}
```

## Notes
- Requires a valid Anthropic API key for Claude AI analysis
- Ensure proper Chrome and ChromeDriver versions match
- Large pages may be truncated to ~200,000 characters for analysis
- The tool uses headless Chrome for rendering JavaScript-dependent content
- Analysis may take time depending on page size and complexity

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---

# WCAG非テキストコンテンツチェッカー
## 概要
WCAG非テキストコンテンツチェッカーは、SeleniumウェブドライバーとClaude AIを使用して、ウェブページのWCAG 1.1.1準拠を自動的に分析し、非テキストコンテンツ（画像、動画、音声）を特定・抽出するPythonツールです。このツールは、非テキスト要素のXPathロケーションと説明を含む詳細なレポートをJSON形式で提供します。

## インストール方法
1. リポジトリのクローン
```bash
git clone https://github.com/daishir0/wcag_non_text_checker.git
cd wcag_non_text_checker
```

2. ChromeとChromeDriverのインストール
Ubuntu/Debian の場合:
```bash
# Chromeのインストール
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f

# ChromeDriverのインストール
sudo apt-get install chromium-chromedriver
```

その他のOSの場合は、以下からダウンロードしてインストール:
- Google Chrome: https://www.google.com/chrome/
- ChromeDriver: https://chromedriver.chromium.org/downloads

3. Python依存パッケージのインストール
```bash
pip install -r requirements.txt
```

4. 設定の構成
```bash
cp config.sample.py config.py
```
config.pyを編集して設定:
- Anthropic APIキーの設定
- 環境に応じてChromeとChromeDriverのパスを調整
- 必要に応じてDEBUGフラグを設定

## 使い方
対象URLを指定してスクリプトを実行:
```bash
python wcag_non_text_checker.py https://example.com
```

ツールは以下を含むJSON形式の結果を出力します:
- 非テキストコンテンツのXPathロケーション
- 各要素の説明
- 要素タイプ（画像、動画、音声）

### 実行例
```bash
$ python wcag_non_text_checker.py https://www.yahoo.co.jp/
{
  "Non-text Contents": [
    {
      "xpath": "//div[contains(@class, \"_7uaWVw_YSgf_GKoctUM12\")]/span/img",
      "description": "記事に関連する全画像サムネイル"
    },
    {
      "xpath": "//div[contains(@class, \"_7uaWVw_YSgf_GKoctUM12\")]/span/picture/img",
      "description": "画像サムネイル（picture要素内）"
    },
    {
      "xpath": "//div[contains(@class, \"_2dkkFdF6iwwsvj59371Trg\")]/span[contains(@class, \"_1I_5hzC8N7rC_DyCqrkXsj\")]",
      "description": "コメント数に関連するアイコン"
    },
    {
      "xpath": "//span[contains(@class, \"_2Uq6Pw5lfFfxr_OD36xHp6\")]",
      "description": "様々なアイコンと画像"
    },
    {
      "xpath": "//div[contains(@class, \"_2MXJ1iB31yVKsR-3VMKR4N\")]/span[contains(@class, \"_2VDw54wcDejORZkozpOysW\")][contains(text(), \"0:\")]",
      "description": "動画の長さが表示されている要素"
    }
  ]
}
```

## 注意点
- Claude AI分析のために有効なAnthropic APIキーが必要です
- ChromeとChromeDriverのバージョンが一致していることを確認してください
- 大きなページは分析のために約200,000文字に制限される場合があります
- JavaScriptに依存するコンテンツのレンダリングにヘッドレスChromeを使用します
- ページのサイズと複雑さによって分析に時間がかかる場合があります

## ライセンス
このプロジェクトはMITライセンスの下でライセンスされています。詳細はLICENSEファイルを参照してください。
