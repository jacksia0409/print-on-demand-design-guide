<!-- LANGUAGES:START -->
<div dir="ltr">

[English](../../../en/artwork-types/texture/texture-layout--texture-layout-local.md) · [简体中文](../../../zh/artwork-types/texture/texture-layout--texture-layout-local.md) · [Português (Brasil)](../../../pt-BR/artwork-types/texture/texture-layout--texture-layout-local.md) · [Español](../../../es/artwork-types/texture/texture-layout--texture-layout-local.md) · [Français](../../../fr/artwork-types/texture/texture-layout--texture-layout-local.md) · [Deutsch](../../../de/artwork-types/texture/texture-layout--texture-layout-local.md) · [العربية](../../../ar/artwork-types/texture/texture-layout--texture-layout-local.md) · [Русский](../../../ru/artwork-types/texture/texture-layout--texture-layout-local.md) · **日本語** · [हिन्दी](../../../hi/artwork-types/texture/texture-layout--texture-layout-local.md)

</div>
<!-- LANGUAGES:END -->

[← ガイド索引](../../INDEX.md) · [PodPlo を読む](https://podplo.app/pod-guide/artwork-types/texture/texture-layout--texture-layout-local?utm_source=github&utm_medium=guide&utm_campaign=print-on-demand-design-guide)

<a id="guide-main"></a>

テクスチャ / 制作の方向性

# ローカルテクスチャフラグメント

テクスチャ領域が画像の一部を占め、別の地面が表示されます。

<a id="understand"></a>

![ローカル テクスチャ フラグメント: テクスチャ領域が画像の一部を占め、別の地面が見えるようになります。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-texture-layout--texture-layout-local-1.svg)

構図の模式図

それを認識する方法

## この方向性を定義するもの

テクスチャが主なコンテンツのままです。パッチがアイデンティティを支配する識別可能なオブジェクトになった場合は、それを主役のアートワークとして再考してください。

[← テクスチャに戻る](../texture.md)

<a id="ai-directions"></a>

AIの指示

## この方向性を AI に取り入れましょう

画像と一緒に使うか、画像生成用のプロンプトをこの表現に合わせて書き直すようAIに依頼してください。

**目指す表現**

テクスチャ → 構成 → ローカルテクスチャフラグメント

**入力と出力**

画像が与えられた場合は、その画像をこの表現に合わせて調整してください。プロンプトが与えられた場合は、画像生成にそのまま使える完全なプロンプトに書き直してください。

**目指す構成**

規則的、自然、またはフェード境界を持つ局所的なパッチ内に関連するサーフェスの詳細を集中させます。背景や補足情報を入れるための周囲のスペースを確保してください。

**背景**

参照マテリアル、パレット、雰囲気。欠落している場合に関連する表面処理を作成します。ローカル パッチには別のバッキングを含めることができます。全領域のテクスチャが地面とマージされます。支配的なオブジェクトや物語の設定を追加することは避けてください。

**文字の扱い**

元画像ではっきり読める文字とその言語を維持し、見せ方を調整してください。読めない文字を復元できたと主張しないでください。文字が指定されていない場合は、主なモチーフ、動き、構成を隠さない短い関連フレーズを補助的に加えてください。既存の文字は目指す視覚的な優先順位に合わせ、文字を入れないという明示的な指定には従ってください。

**維持と調整**

オブジェクトのシルエットや完全なシーンを必要とせずに、関連するマテリアル、サーフェス、パレット、雰囲気を保持します。マテリアルの手がかりが存在しないときに、ソースの実際のマテリアルを識別したと主張せずに、要求されたエフェクトを作成します。新しく作成されたコンテンツをソースに存在するものとして記述しないでください。明示的な入力制限と必要なターゲット条件の両方が満たされたと主張するのではなく、それらの間の矛盾を述べます。

**適用範囲と制約**

テクスチャが主なコンテンツのままです。パッチがアイデンティティを支配する識別可能なオブジェクトになった場合は、それを主役のアートワークとして再考してください。

<a id="backgrounds"></a>

## 背景を探る

これらの例では、同じコンテンツ ファミリ内の根拠を比較しています。トリートメントを適用するときは、現在の組成を維持します。完全な手順については、例を開いてください。

[![透明な背景: テクスチャ: 地面は透明のままです。チェッカーボードは単なる表示補助です。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-background--texture--transparent-1.svg)

### 透明背景↗

テクスチャ: 地面は透明のままです。チェッカーボードは単なる表示補助です。](background--texture--transparent.md)[![単色の背景: テクスチャ: 1 つの均一な色が地面を形成します。白も単色の背景です。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-background--texture--solid-1.svg)

### 無地の背景↗

テクスチャ: 1 つの均一な色が地面を形成します。白も単色の背景です。](background--texture--solid.md)[![グラデーションの背景: テクスチャ: メインのコンテンツはクリアなままで、背景の色または明るさが連続的に変化します。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-background--texture--gradient-1.svg)

### グラデーション背景↗

テクスチャ: メインコンテンツはクリアなままでありながら、裏地の色や明るさが連続的に変化します。](background--texture--gradient.md)[![パターン化された背景: ローカル: テクスチャ: 装飾的なパッチがコンテンツの後ろに配置され、パッチの外側に領域が残ります。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-background--texture--pattern-local-1.svg)

### パターン背景: ローカル↗

テクスチャ: 装飾的なパッチがコンテンツの後ろに配置され、パッチの外側に領域が残ります。](background--texture--pattern-local.md)[![パターン化された背景: 全領域: テクスチャ: パターン化された地面が、はっきりと読み取れる前景コンテンツの後ろの画像を覆います。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-background--texture--pattern-full-1.svg)

### パターン背景：全面↗

テクスチャ: パターン化された地面が、はっきりと読み取れる前景コンテンツの背後の画像を覆います。](background--texture--pattern-full.md)[![テクスチャ背景: テクスチャ: 紙粒、粒子、または別の表面の文字が前景コンテンツをサポートします。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-background--texture--texture-1.svg)

### テクスチャ背景↗

テクスチャ: 紙粒、粒子、または別の表面の特徴が前景コンテンツをサポートします。](background--texture--texture.md)[![環境背景: テクスチャ: テーマに関連した環境は、メイン コンテンツをその背後または周囲からサポートします。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-background--texture--scene-1.svg)

### 環境背景↗

テクスチャ: テーマ関連の環境は、メイン コンテンツをその背後または周囲からサポートします。](background--texture--scene.md)

<a id="related"></a>

## 近くのルートを比較する

[![全領域テクスチャ: 表面の詳細が画像を満たすため、メイン コンテンツと地面が 1 つになります。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-texture-layout--texture-layout-full-1.svg)

### 全面テクスチャ↗

表面のディテールが画像全体に表示されるため、メインのコンテンツと地面が 1 つになります。](texture-layout--texture-layout-full.md)[![レイヤード テクスチャ コラージュ: いくつかのテクスチャ フラグメントが重なり合って、マテリアルとエッジの関係が作成されます。](https://images.podplo.app/official/pod-guide/diagrams/b2382e28cd57b514819e/legacy-texture-layout--texture-layout-layers-1.svg)

### レイヤードテクスチャコラージュ↗

いくつかのテクスチャ付きフラグメントが重なり合って、マテリアルとエッジの関係が作成されます。](texture-layout--texture-layout-layers.md)

コードによる研究では、構成と視覚的処理を比較します。メディアとスタイルの例は概念的なものです。これらの方向は、画像モデルを使用して個別にテストされていません。生成されたテキスト、透明度、リピートエッジを確認します。
