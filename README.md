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
git clone https://github.com/masashowgo/alexa-gemini-gpt.git
cd alexa-gemini-gpt
```

### 2. APIキーの設定

`lambda/keys.py` ファイルを開き、プレースホルダーをご自身のGoogle APIキーに置き換えてください。

```python
# lambda/keys.py
GOOGLE_API_KEY = 'ここにAPIキーを入れる'
SYSTEM_MESSAGE = 'あなたは優秀なアシスタントです。簡潔に分かりやすく回答してください。'
MODEL = 'gemini-2.5-flash-lite'
```

### 3. デプロイ用 ZIP の作成

AWS Lambda 実行環境に合わせて zip ファイルを作る必要があります。
そのため、macOS で `pip install` したのでは駄目で、AWS Lambda公式ランタイムコンテナを使ったビルドが必要です。

プロジェクトの `lambda` ディレクトリで以下を実行します。

**【注意事項】**
`colima` はDocker Desktopの代替として利用できるコンテナランタイムです。お使いの環境に合わせて、Docker DesktopやPodmanなどのDocker互換ランタイムを起動してください。

```bash
colima start
docker run --rm -it --platform linux/arm64 \
  -v "$PWD":/var/task \
  public.ecr.aws/lambda/python:3.12 bash
```

- Lambda 関数の アーキテクチャ設定に合わせて `--platform` を変える
    - `x86_64` → `--platform linux/amd64`
    - `arm64` → `--platform linux/arm64`

コンテナに入っていなかった場合:
```bash
docker ps # コンテナIDを確認
docker exec -it <コンテナID> /bin/bash
```

コンテナに入ったら:

```bash
python -m pip install --upgrade pip
pip install --only-binary=:all: -r requirements.txt -t /var/task

dnf install -y zip || yum install -y zip

cd /var/task
zip -r ../deployment_package.zip .
mv ../deployment_package.zip ./
```

`deployment_package.zip` を Lambda にアップロードすればOKです。

### 4. AlexaとAWSの設定

1.  **Alexaスキルの作成**:
    - Amazon開発者コンソールで、新しいカスタムスキルを作成します。
    - スキルのマニフェストとして `skill.json` の内容を使用します。
    - 対話モデルとして `interactionModels/custom/ja-JP.json` の内容を使用します。
    **【ヒント】** Alexa Skills Kit CLI (ASK CLI) の `ask deploy` コマンドや、開発者コンソールからのスキルインポート機能を利用すると、`skill.json` や `interactionModels/custom/ja-JP.json` をより簡単にデプロイできます。
2.  **AWS Lambda関数の作成**:
    - AWSマネジメントコンソールで、Pythonランタイムの新しいLambda関数を作成します。
    - 作成した `deployment_package.zip` をアップロードします。
    - ハンドラーを `lambda_function.handler` に設定します。
3.  **AlexaとLambdaの接続**:
    - Lambda関数のARNをコピーします。
    - Alexaスキルの設定画面で、「エンドポイント」のセクションにLambdaのARNを貼り付けます。

## 使用方法

デプロイ後、呼び出し名（"Gemini"）を使ってスキルと会話を開始できます。

> **あなた**: アレクサ、Gemini
>
> **Alexa**: Geminiです。
>
> **あなた**: 今日の天気は？
>
> **Alexa**: (Geminiからの応答)

---

*補足: このプロジェクトは元々、Node.jsとOpenAI APIを使用していましたが、PythonとGoogle Gemini APIを使用するように書き換えられました。*
