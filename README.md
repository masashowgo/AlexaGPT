# Alexa Gemini スキル

このプロジェクトは、GoogleのGemini AIと会話できるAlexaスキルです。

## 主な特徴

- **対話型AI**: 高性能なGeminiモデルとAlexaを通じて会話できます。
- **会話履歴の記憶**: セッション内で文脈を維持した会話が可能です。
- **AWS Lambdaバックエンド**: バックエンドはPythonで実装されたAWS Lambda関数で動作します。
- **デプロイが容易**: 簡単な設定でご自身のAWSアカウントにデプロイできます。

## 技術スタック

- **Alexa Skills Kit**: 音声ユーザーインターフェースの構築
- **Python**: バックエンドロジックの実装言語
- **AWS Lambda**: バックエンドのサーバーレス実行環境
- **Google Gemini API**: 対話型AIエンジン

## セットアップとインストール

以下の手順で、スキルのセットアップとデプロイを行います。

### 必要なもの

- Alexaスキルを作成するためのAmazon開発者アカウント
- Lambda関数をホストするためのAWSアカウント
- Gemini APIが有効化されたGoogleのAPIキー

### 1. リポジトリのクローン

```bash
git clone https://github.com/masashowgo/AlexaGPT.git
cd AlexaGPT
```

### 2. APIキーの設定

`lambda/keys.py` ファイルを開き、プレースホルダーをご自身のGoogle APIキーに置き換えてください。

```python
# lambda/keys.py
GOOGLE_API_KEY = 'ここにAPIキーを入れる'
SYSTEM_MESSAGE = 'あなたは優秀なアシスタントです。簡潔に分かりやすく回答してください。'
MODEL = 'gemini-2.5-flash-lite'
```

### 3. 依存ライブラリのインストール

バックエンド関数はいくつかのPythonライブラリを必要とします。これらを `lambda` ディレクトリ内にインストールします。

```bash
cd lambda
pip install -r requirements.txt -t .
```

**注**: `-t .` フラグは、ライブラリをカレントディレクトリにインストールします。これはLambdaのデプロイパッケージを作成するために必要な手順です。

### 4. デプロイパッケージの作成

ライブラリをインストールした後、`lambda` ディレクトリ内のすべてのファイルを含むZIPファイルを作成します。

```bash
# lambda ディレクトリにいることを確認してください
zip -r ../deployment_package.zip .
```

これにより、プロジェクトのルートディレクトリに `deployment_package.zip` というファイルが作成されます。

### 5. AlexaとAWSの設定

1.  **Alexaスキルの作成**:
    - Amazon開発者コンソールで、新しいカスタムスキルを作成します。
    - スキルのマニフェストとして `skill.json` の内容を使用します。
    - 対話モデルとして `interactionModels/custom/ja-JP.json` の内容を使用します。
2.  **AWS Lambda関数の作成**:
    - AWSマネジメントコンソールで、Pythonランタイムの新しいLambda関数を作成します。
    - 作成した `deployment_package.zip` をアップロードします。
    - ハンドラーを `lambda_function.handler` に設定します。
3.  **AlexaとLambdaの接続**:
    - Lambda関数のARNをコピーします。
    - Alexaスキルの設定画面で、「エンドポイント」のセクションにLambdaのARNを貼り付けます。

## 使用方法

デプロイ後、呼び出し名（"チャット"）を使ってスキルと会話を開始できます。

> **あなた**: アレクサ、チャットを開いて
>
> **Alexa**: ようこそ。何が知りたいですか？
>
> **あなた**: 今日の天気は？
>
> **Alexa**: (Geminiからの応答)

---

*補足: このプロジェクトは元々、Node.jsとOpenAI APIを使用していましたが、PythonとGoogle Gemini APIを使用するように書き換えられました。*