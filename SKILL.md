---
name: blend-credit-table
description: 从 Blender 工程(.blend)中找出用到的第三方模型/场景，对照本地模型库 readme 匹配作者，生成借物表(credit list/素材表/来源标注)。当用户需要写借物表、素材表、credit list、来源标注，或要确认某个 .blend 里用了哪些别人做的模型及其作者时使用。即使只是说"帮我看下我 Blender 工程里用了哪些模型""这个场景是谁做的"，也应使用本 skill。
---

# Blender 借物表生成（Blend Credit Table）

用户在 Blender 里做视频/作品，场景混用了 MMD/他人建模的模型，需要把「用到的模型 → 作者」对应起来，产出借物表。

## 核心思路

**从 .blend 反查模型 → 到本地模型库文件夹匹配 → 读 readme 提取作者 → 输出借物表。**

- `.blend` 里模型对象名通常就是 PMX 内部名或文件名，可直接匹配模型库文件夹。
- 借物表按用户要求精简：默认 **只写主要作者**，格式 `模型名-作者`，按「角色」「场景」等分组。用户要求更详细时再列出部件原作者。

## 前置条件

- 本机装了 Blender（后台模式可用）。用 `Get-ChildItem D:\ -Filter "*blender*"` 之类探测路径，或直接问用户。脚本调用方式是 `blender.exe --background --python 脚本.py -- 文件路径`（`--` 后才是传给脚本的参数）。
- 模型库目录（如 `D:\模型`）下每个模型文件夹带 readme（txt/md 等）。
- 系统有 Python 3（脚本用系统 python 跑，不用 Blender 内置 python）。

## 流程

### 1. 解析 .blend，找出用到的模型

用 [scripts/dump_blend.py](scripts/dump_blend.py) 逐个导出场景集合层级与对象名（每个 .blend 生成 `<blend>.scene_dump.json`，可并行跑）：

```powershell
& "D:\blender-4.4.3-windows-x64\blender.exe" --background --python "scripts\dump_blend.py" -- "D:\工程\xxx.blend" 2>&1 | Select-Object -Last 3
```

再用 [scripts/list_models.py](scripts/list_models.py) 过滤 dump，只看 **主 Collection**（名为 `Collection` 的顶层集合），跳过刚体/关节/骨骼/灯光噪声，得到实际模型名：

```powershell
python scripts\list_models.py "D:\工程\*.scene_dump.json"
```

### 2. 在模型库里找到对应文件夹

用模型名反查模型库目录树（`Get-ChildItem D:\模型 -Directory -Recurse`）。匹配手段按可靠度排序：

1. **PMX 文件名**直接等于对象名（最常见，最可靠）。
2. 对象名是 PMX 内部名，用 [scripts/pmx_author.py](scripts/pmx_author.py) 读 PMX 头部 name/comment 确认。
3. **同名模型有多个候选**时（如「八雲紫」有 Miy式 和 改変版两个文件夹），用 [scripts/dump_materials.py](scripts/dump_materials.py) 导出 blend 里该模型的**材质贴图名**，与各候选文件夹里的贴图文件对比判定：

```powershell
& "D:\blender-...\blender.exe" --background --python "scripts\dump_materials.py" -- "D:\工程\xxx.blend" 2>&1 | Select-String "MATS_DONE"
```

### 3. 读 readme 提取作者

readme 多为日文/中文，编码不定（shift_jis / cp932 / gb18030 / utf-8 / utf-16）。用 [scripts/read_readmes.py](scripts/read_readmes.py) 自动探测编码解码并打印，从中找作者字段。

**无 readme 时**：用 [scripts/pmx_author.py](scripts/pmx_author.py) 从 PMX 的**内部注释（comment）**里找作者——很多模型会把「××式〇〇」「作者名」写进注释（实测从无 readme 的蓬莱山輝夜 PMX 注释里挖出了「ろくご式蓬莱山輝夜」）。

### 4. 输出借物表

按用户要求格式生成 txt，默认精简格式：

```
角色：
八雲紫-Miy
レミリア スカーレット-雪萱

场景：
民家-ムムム
```

## 作者判定要点

- 角色模型常是多作者**拼合改造**（readme 的「致谢/改変元」列出一堆部件作者）。默认只写**改変模型的制作/配布者**（主要作者）；若用户要做严谨 credit，把所有部件原作者都列出。
- 场景模型可能是「原模型 + MMD 化」双层作者，如 CC BY 模型的原始作者（Sketchfab 等）按协议**必须表记**，需提醒用户。
- 借物表要遵守各模型规约（大多数禁止商用、禁止无改再配布），可在表尾补一条通用说明。

## 常见坑

- **PowerShell 引用**：含特殊字符的路径（`（`、空格、日文）用双引号包住；避免在 `"..."` 里用反斜杠转义。
- **GBK 乱码**：readme 解码失败先试 cp932/shift_jis，再试 gb18030/utf-8。
- **读大文件**：`.scene_dump.json` 可能几 MB，别整读进上下文，用脚本过滤。
- **主集合判定**：dump 里除了 `Collection` 还有 `WGTS_MMR-*_arm` 等绑定集合，模型根对象在 `Collection` 里。
