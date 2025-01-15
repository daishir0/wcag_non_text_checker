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

    # フォーマット例を更新
    format_example = '''{
  "Non-text Contents": [
    {
      "xpath": "//main//figure[contains(@class, 'hero')]//img",
      "description": "トップページのメインビジュアル画像",
      "situation": "D",
      "reason": "メインビジュアルは感覚的な体験を提供することを主目的としているため",
      "wcag_judgment": "NG",
      "judgment_reason": "alt属性が存在しないため、最低限必要な説明的な識別情報が提供されていない",
      "success_techniques": [
        "ARIA6: オブジェクトのラベルを提供するために aria-label を使用する",
        "H37: img 要素の alt 属性を使用する"
      ]
    },
    {
      "xpath": "//form//input[@type='image']",
      "description": "フォーム送信用の画像ボタン",
      "situation": "A",
      "reason": "ユーザーの入力を受け付けるコントロールとして機能するため",
      "wcag_judgment": "OK",
      "judgment_reason": "aria-label属性で「検索を実行」という目的を説明する名前が提供されている",
      "success_techniques": [
        "ARIA6: オブジェクトのラベルを提供するために aria-label を使用する",
        "H36: 送信ボタンとして用いる画像の alt 属性を使用する"
      ]
    }
  ]
}'''
    
    prompt = f"""# あなたは日本語を使うWebアクセシビリティテストのプロです。以下のページ内について、WCAG1.1.1で判定対象とする、非テキストコンテンツ（画像、動画、音声）を全て抽出し、その状況（Situation）を判定し、テキスト代替の適切性を評価するタスクを持っています。

# Situationの判定基準と要件：
# A (Controls, Input): ボタンやフォーム入力など、ユーザーが操作または入力を行う要素
- 要件：目的を説明する名前（name）が必要
- 判定基準：aria-label、aria-labelledby、alt属性などで目的が明確に説明されているか

# B (Time-Based Media): 動画や音声などの時間依存メディア
- 要件：少なくとも内容を説明する識別情報が必要
- 判定基準：aria-label、figcaption、alt属性などで内容の説明があるか

# C (Test): テキストで提示すると無効になるようなテストや演習
- 要件：少なくとも内容を説明する識別情報が必要
- 判定基準：aria-label、alt属性などでテストの目的や種類が説明されているか

# D (Sensory): 特定の感覚的体験を生み出すことを主目的とするコンテンツ
- 要件：少なくとも内容を説明する識別情報が必要
- 判定基準：aria-label、figcaption、alt属性などで内容の説明があるか

# E (CAPTCHA): 人間とコンピュータを区別するためのCAPTCHA
- 要件：目的の説明と代替のCAPTCHAが必要
- 判定基準：目的の説明があり、かつ代替の手段が提供されているか

# F (Decoration): 純粋な装飾目的、視覚的な整形のみ、またはユーザーに表示されない要素
- 要件：支援技術で無視できるように実装
- 判定基準：alt=""や aria-hidden="true"、role="presentation"などが適切に設定されているか

# 各状況における達成方法：
状況A（Controls, Input）の達成方法:
-   ARIA6: オブジェクトのラベルを提供するために aria-label を使用する
-   ARIA10: 非テキストコンテンツに対してテキストによる代替を提供するために aria-labelledby を使用する
-   G196: 画像のグループにある一つの画像に、そのグループのすべての画像を説明するテキストによる代替を提供する
-   FLASH1: 非テキストオブジェクトに name プロパティを設定する
-   FLASH5: 同じリソースに対して隣接する画像とテキストのボタンを結合する
-   FLASH28: Flash で ASCII アート、顔文字、リート語に対するテキストによる代替を提供する
-   H2: 同じリソースに対して隣接する画像とテキストリンクを結合する
-   H35: applet 要素にテキストによる代替を提供する
-   H37: img 要素の alt 属性を使用する
-   H53: object 要素のボディを使用する
-   H86: ASCII アート、顔文字、及びリート語にテキストによる代替を提供する
-   PDF1: PDF 文書の Alt エントリによって画像にテキストによる代替を適用する
-   SL5: Defining a Focusable Image Class for Silverlight

状況B（Time-Based Media）の達成方法:
**状況 B における短いテキストによる代替の達成方法**:

-   ARIA6: オブジェクトのラベルを提供するために aria-label を使用する
-   ARIA10: 非テキストコンテンツに対してテキストによる代替を提供するために aria-labelledby を使用する
-   G196: 画像のグループにある一つの画像に、そのグループのすべての画像を説明するテキストによる代替を提供する
-   FLASH1: 非テキストオブジェクトに name プロパティを設定する
-   FLASH5: 同じリソースに対して隣接する画像とテキストのボタンを結合する
-   FLASH28: Flash で ASCII アート、顔文字、リート語に対するテキストによる代替を提供する
-   H2: 同じリソースに対して隣接する画像とテキストリンクを結合する
-   H35: applet 要素にテキストによる代替を提供する
-   H37: img 要素の alt 属性を使用する
-   H53: object 要素のボディを使用する
-   H86: ASCII アート、顔文字、及びリート語にテキストによる代替を提供する
-   PDF1: PDF 文書の Alt エントリによって画像にテキストによる代替を適用する
-   SL5: Defining a Focusable Image Class for Silverlight

**状況 B における長いテキストによる代替の達成方法**:

-   ARIA15: 画像の説明を提供するために aria-describedby を使用する
-   G73: 非テキストコンテンツのすぐ隣に別の場所へのリンクを置き、その別の場所で長い説明を提供する
-   G74: 短い説明の中で長い説明のある場所を示して、非テキストコンテンツの近くにあるテキストで長い説明を提供する
-   G92: 非テキストコンテンツに対して、それと同じ目的を果たし、かつ同じ情報を示す長い説明を提供する
-   FLASH2: Flash 内の非テキストオブジェクトに description プロパティを設定する
-   FLASH11: オブジェクトについて長いテキストの説明を提供する
-   H45: longdesc 属性を用いる
-   H53: object 要素のボディを使用する
-   SL8: Displaying HelpText in Silverlight User Interfaces

状況C（Test）の達成方法:
-   ARIA6: オブジェクトのラベルを提供するために aria-label を使用する
-   ARIA9: 複数のテキストノードをつなげて一つのラベルにするために、aria-labelledby を使用する
-   FLASH6: 非表示のボタンを使用してアクセシブルなホットスポットを作成する
-   FLASH25: アクセシブルな名前を設定することによって、フォームコントロールにラベルを付ける
-   FLASH27: ボタンの目的を説明するラベルを提供する
-   FLASH29: フォームコンポーネントに label プロパティを設定する
-   FLASH30: 画像ボタンにアクセシブルな名前を指定する
-   FLASH32: フォームコントロールにテキストラベルを関連付けるために、自動ラベリングを使用する
-   H24: イメージマップの area 要素にテキストによる代替を提供する
-   H30: a 要素のリンクの目的を説明するリンクテキストを提供する
-   H36: 送信ボタンとして用いる画像の alt 属性を使用する
-   H44: テキストラベルとフォームコントロールを関連付けるために、label 要素を使用する
-   H65: label 要素を使用できない場合に、フォームコントロールを特定するために、title 属性を使用する
-   SL18: Providing Text Equivalent for Nontext Silverlight Controls With AutomationProperties.Name
-   SL26: Using LabeledBy to Associate Labels and Targets in Silverlight
-   SL30: Using Silverlight Control Compositing and AutomationProperties.Name

状況D（Sensory）の達成方法:
-   ARIA6: オブジェクトのラベルを提供するために aria-label を使用する
-   ARIA10: 非テキストコンテンツに対してテキストによる代替を提供するために aria-labelledby を使用する
-   G196: 画像のグループにある一つの画像に、そのグループのすべての画像を説明するテキストによる代替を提供する
-   FLASH1: 非テキストオブジェクトに name プロパティを設定する
-   FLASH5: 同じリソースに対して隣接する画像とテキストのボタンを結合する
-   FLASH28: Flash で ASCII アート、顔文字、リート語に対するテキストによる代替を提供する
-   H2: 同じリソースに対して隣接する画像とテキストリンクを結合する
-   H35: applet 要素にテキストによる代替を提供する
-   H37: img 要素の alt 属性を使用する
-   H53: object 要素のボディを使用する
-   H86: ASCII アート、顔文字、及びリート語にテキストによる代替を提供する
-   PDF1: PDF 文書の Alt エントリによって画像にテキストによる代替を適用する
-   SL5: Defining a Focusable Image Class for Silverlight

状況F（Decoration）の達成方法:
-   C9: 装飾目的の画像を付加するために、CSS を使用する
-   FLASH3: 支援技術によって無視されるように Flash のオブジェクトにマークを付ける
-   H67: 支援技術が無視すべき画像に対して、img 要素の alt テキストを空にして、title 属性を付与しない
-   PDF4: PDF 文書の Artifact タグによって装飾的な画像を隠す

# 以下のフォーマット例を参考に、エリアごとに、ターゲットhtmlのbody部を、上部から個々に抽出し、xpathで提示してください。
# 各要素について、適切なSituationを判定し、その理由と適用可能な達成方法も含めてください。

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
