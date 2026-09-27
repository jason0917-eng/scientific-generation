# 图示数据约定

`sources.json`：对象含 `paper`（原文身份字段见 source-and-coverage.md）及 `visual_references` 数组。每个参考含 `url, title, figure, inspected_region, borrow, must_change`。记录来源实际访问情况。

`graph.json`：
```json
{
  "nodes": [{"id":"n1","label":"Input","role":"input","stage":"inference","source":"section/page/equation locator"}],
  "edges": [{"id":"e1","from":"n1","to":"n2","relation":"data","label":"representation","source":"section/page/equation locator"}]
}
```
以上是字段片段，不是可直接采用的完整科学图。所有端点必须存在，ID 唯一。每条边需科学依据；依赖关系与空间排列分开保存。loss/feedback/sharing/conditioning 等关系明确命名。节点需要的 shape、dtype、重复次数按实际论文填写，不确定处不要猜。

`graph.json` 仅为科学逻辑记录，不是绘图程序、SVG结构或固定矩形布局。`visual-plan.md` 为每个核心节点补充实际可见形态、参考范例、局部机制和短标签；不能把 graph 直接变成文字框图。

`design.json` 为历史比较的独立记录：
```json
{
  "run_id": "20260926-model-001",
  "paper_id": "confirmed-paper-id",
  "style": ["flat", "thin-lines", "sans-serif"],
  "layout": ["left-to-right", "training-lane", "detail-inset"],
  "elements": ["token-strip", "encoder-stack"],
  "relation_visuals": ["orthogonal-data-arrows", "dashed-supervision"],
  "topology": ["input->encoder:data", "encoder->head:data"],
  "plan_review_status": "pending",
  "review_status": "draft"
}
```
用稳定、具体、统一语言的小写描述词，不靠换同义词逃避比较。`topology` 使用真实语义标签与边类型，不能包含随机节点 ID；`relation_visuals` 只写展示形式。相对图片路径以 design.json 所在目录为基准。脚本不是科学、图像或 AI 内容检测器。

`preflight.md`：出图前验证记录，标注所核对的方案与提示词版本，逐项列出科学依据、布局适配、节点/边/标签、最多 5 色及组映射、跨图配色差异（比较本批方案与可访问历史）、历史比较、创意师方案审查、提示词一致性、问题修复及总状态。design.json 的 palette 保存本图功能组→HEX映射，不使用全批共享色板。所有适用项通过且无未解决问题才写 passed，并同步 design.json 的 plan_review_status；此时没有当前成图，review_status 仍为 draft，不写 image_path。不适用于出图前判断的像素级项目明确留到成图执行检查。

`qa.md`：记录成图对已验证方案的执行情况，包括 graph→图片逐项核对、成图查看方式/文件、视觉范例匹配、配色、图像生成/编辑调用记录、执行偏差、修订次数、残留问题和最终状态。实际生成并检查通过后才添加 image_path: figure.png，将 review_status 改为 passed，并登记历史。仅有脚本分数不能标记 passed。当前输出为 figure.png，不要求或生成可编辑矢量文件。
