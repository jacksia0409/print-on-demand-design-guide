<!-- LANGUAGES:START -->
<div dir="ltr">

[English](../../../en/artwork-types/scene/background--scene--texture.md) · [简体中文](../../../zh/artwork-types/scene/background--scene--texture.md) · [Português (Brasil)](../../../pt-BR/artwork-types/scene/background--scene--texture.md) · [Español](../../../es/artwork-types/scene/background--scene--texture.md) · [Français](../../../fr/artwork-types/scene/background--scene--texture.md) · [Deutsch](../../../de/artwork-types/scene/background--scene--texture.md) · [العربية](../../../ar/artwork-types/scene/background--scene--texture.md) · [Русский](../../../ru/artwork-types/scene/background--scene--texture.md) · **日本語** · [हिन्दी](../../../hi/artwork-types/scene/background--scene--texture.md)

</div>
<!-- LANGUAGES:END -->

[← ガイド索引](../../INDEX.md) · [PodPlo を読む](https://podplo.app/pod-guide/artwork-types/scene/background--scene--texture?utm_source=github&utm_medium=guide&utm_campaign=print-on-demand-design-guide)

<a id="guide-main"></a>

シーン / クリエイティブディレクション / シーン

# テクスチャ背景

シーン: 紙粒、パーティクル、または別の表面キャラクターが前景コンテンツをサポートします。

<a id="understand"></a>

![テクスチャ背景: シーン: 紙粒、粒子、または別の表面キャラクターが前景コンテンツをサポートします。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-background--scene--texture-1.svg)

構図の模式図

それを認識する方法

## この方向性を定義するもの

テクスチャード加工された裏地は、自動的に独立したオブジェクトや物語のシーン全体になるべきではありません。テクスチャ カテゴリでは、主表面の断片とその支持地盤を区別します。

[← シーンに戻る](../scene.md)

<a id="ai-directions"></a>

AIの指示

## この方向性を AI に取り入れましょう

画像と一緒に使うか、画像生成用のプロンプトをこの表現に合わせて書き直すようAIに依頼してください。

**目指す表現**

シーン → 背景 → テクスチャ背景

**入力と出力**

画像が与えられた場合は、その画像をこの表現に合わせて調整してください。プロンプトが与えられた場合は、画像生成にそのまま使える完全なプロンプトに書き直してください。

**目指す構成**

シーンの重要なスペース、設定、既存のイベントを保存します。シーンを構成するコンテキストを削除するのではなく、背景の地面、空のレイヤー、または周囲の背景を変更します。

**背景**

既存のサーフェスの詳細、パレット、密度を参照するか、存在しない場合はテーマに関連した低干渉テクスチャを作成します。素材が脇役にとどまるように、スケールとコントラストを調整します。

**文字の扱い**

元画像ではっきり読める文字とその言語を維持し、見せ方を調整してください。読めない文字を復元できたと主張しないでください。文字が指定されていない場合は、主なモチーフ、動き、構成を隠さない短い関連フレーズを補助的に加えてください。既存の文字は目指す視覚的な優先順位に合わせ、文字を入れないという明示的な指定には従ってください。

**維持と調整**

中心となるテーマと、元の対象を識別できる特徴を維持してください。元の表現方法と配色を出発点とし、選んだ表現に必要な範囲だけ変更してください。新たに作成した内容を、元画像に存在していたものとして説明しないでください。明示的な入力条件と、目指す結果に必要な条件が矛盾する場合は、両方を満たしたと主張せず、その矛盾を説明してください。

**適用範囲と制約**

テクスチャード加工された裏地は、自動的に独立したオブジェクトや物語のシーン全体になるべきではありません。テクスチャ カテゴリでは、主表面の断片とその支持地盤を区別します。

<a id="related"></a>

## 近くのルートを比較する

[![透明な背景: シーン: 地面は透明のままです。チェッカーボードは単なる表示補助です。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-background--scene--transparent-1.svg)

### 透明背景↗

シーン: 地面は透明のままです。チェッカーボードは単なる表示補助です。](background--scene--transparent.md)[![単色の背景: シーン: 1 つの均一な色が地面を形成します。白も単色の背景です。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-background--scene--solid-1.svg)

### 無地の背景↗

シーン: 単一の均一な色が地面を形成します。白も単色の背景です。](background--scene--solid.md)[![グラデーションの背景: シーン: メインのコンテンツはクリアなままで、背景の色または明るさが連続的に変化します。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-background--scene--gradient-1.svg)

### グラデーション背景↗

シーン: メインコンテンツはクリアなままですが、裏地の色や明るさが連続的に変化します。](background--scene--gradient.md)[![パターン化された背景: ローカル: シーン: 装飾的なパッチがコンテンツの背後にあり、パッチの外側に領域が残ります。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-background--scene--pattern-local-1.svg)

### パターン背景: ローカル↗

シーン: 装飾的なパッチがコンテンツの後ろに配置され、パッチの外側に領域が残ります。](background--scene--pattern-local.md)

コードによる研究では、構成と視覚的処理を比較します。メディアとスタイルの例は概念的なものです。これらの方向は、画像モデルを使用して個別にテストされていません。生成されたテキスト、透明度、リピートエッジを確認します。
