import sys
import time
import json
import anthropic
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import ANTHROPIC_API_KEY, CHROME_BINARY_PATH, CHROME_DRIVER_PATH, DEBUG

def get_page_source(url):
    """
    ChromeDriverを使用してページにアクセスし、JavaScriptが実行された後のソースを取得
    """
    # Chromeのオプション設定
    options = Options()
    options.headless = True
    options.binary_location = CHROME_BINARY_PATH
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--enable-logging')
    options.add_argument('--log-level=1')
    options.add_argument("--headless")

    # ChromeDriverの設定
    service = Service(executable_path=CHROME_DRIVER_PATH)  # ChromeDriverのパスを指定

    driver = webdriver.Chrome(service=service, options=options)

    try:
        # ページにアクセス
        driver.get(url)
        
        # ページの最下部までスクロール
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # 最下部までスクロール
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # 新しいコンテンツがロードされるのを待つ
            time.sleep(2)
            
            # 新しい高さを取得
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # スクロールしても高さが変わらなければ終了
            if new_height == last_height:
                break
            last_height = new_height
        
        # 最終的なページソースを取得
        page_source = driver.page_source
        return page_source
    finally:
        driver.quit()

def analyze_wcag_1_1_1(html_content):
    """
    ClaudeにHTMLを解析させ、WCAG 1.1.1の評価対象を抽出
    """
    # HTMLコンテンツを制限（約100000トークンに制限）
    max_length = 200000
    html_content = html_content[:max_length] if len(html_content) > max_length else html_content
    
    client = anthropic.Anthropic(
        api_key=ANTHROPIC_API_KEY,
    )    

    # フォーマット例を別の変数として定義
    format_example = '''{
  "Non-text Contents": [
    {
      "xpath": "//main//figure[contains(@class, 'hero')]//img",
      "description": "トップページのメインビジュアル画像"
    },
    {
      "xpath": "//form//input[@type='image']",
      "description": "フォーム送信用の画像ボタン"
    }
  ]
}'''
    
    prompt = f"""# あなたは日本語を使うWebアクセシビリティテストのプロです。以下のページ内について、WCAG1.1.1で判定対象とする、非テキストコンテンツ（画像、動画、音声）を全て抽出するタスクを持っています。
# 以下のフォーマット例に参考に、エリアごとに、ターゲットhtmlのbody部を、上部から個々（例えば個別の画像単位、個別の動画単位）に抽出し、xpathで提示してください。
# 必ず有効なJSONフォーマットのみで回答してください。説明文は不要です。コードブロックも不要です。
# 必ずダブルクォート(")を使用してください。シングルクォート(')は使用しないでください。

フォーマット例###
{format_example}

ターゲットhtml###
{html_content}"""

    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=8192,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    try:
        # レスポンスから直接JSON文字列を取得
        response_text = str(message.content)
        if DEBUG:
            print("=== Claudeからの応答 ===")
            print(response_text)
            print("=====================")
        
        # 最初の { から最後の } までを抽出
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx]
            if DEBUG:
                print("=== 抽出したJSON文字列 ===")
                print(json_str)
                print("=====================")
            
            # シングルクォートをダブルクォートに置換
            json_str = json_str.replace("'", '"')
            # 改行文字を実際の改行に置換
            json_str = json_str.replace('\\n', '\n')
            # 余分な空白を削除
            json_str = json_str.strip()
            
            if DEBUG:
                print("=== 整形後のJSON文字列 ===")
                print(json_str)
                print("=====================")
            
            return json.loads(json_str)
        else:
            if DEBUG:
                print("JSONが見つかりませんでした")
            return None
            
    except Exception as e:
        if DEBUG:
            print(f"Error parsing JSON: {e}")
            print("=== 問題のJSON文字列 ===")
            print(json_str)
            print("=====================")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python check_wcag1_1_1.py url")
        sys.exit(1)

    url = sys.argv[1]
    
    try:
        # ページソースの取得
        page_source = get_page_source(url)
        
        # WCAG 1.1.1の解析
        result = analyze_wcag_1_1_1(page_source)
        
        # 結果の出力
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("Analysis failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
