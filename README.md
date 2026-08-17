# blend-credit-table

从 **Blender 工程文件（.blend）** 中找出用到的第三方模型/场景，对照本地模型库 readme 匹配作者，生成**借物表**（credit list / 素材表 / 来源标注）。

## 功能

- 解析 `.blend`，提取实际导入的模型/场景名（自动跳过刚体、关节、灯光、RIG 绑定集合等噪声）
- 在本地模型库中匹配对应模型文件夹
- 读取模型 readme 提取作者（自动处理 Shift-JIS / GBK / UTF-8 等多种编码）
- 无 readme 时从 PMX 内部注释挖掘作者（如「ろくご式蓬莱山輝夜」）
- 同名不同作者的模型用材质贴图名区分（如 Miy式 八雲紫 vs 改変八雲紫）
- 输出借物表：按「角色 / 场景」分组，格式 `模型名-作者`

## 目录结构

```
blend-credit-table/
├── SKILL.md                     # 使用流程说明
└── scripts/
    ├── dump_blend.py            # Blender 后台解析 .blend → scene_dump.json
    ├── list_models.py           # 过滤出实际用到的模型名
    ├── dump_materials.py        # 导出材质贴图名（区分同名模型）
    ├── pmx_author.py            # 从 PMX 内部注释找作者
    └── read_readmes.py          # 编码探测读取 readme
```

## 使用方式

作为 Claude Code / Claude Agent SDK 的 skill 安装到 `~/.claude/skills/` 即可，或手动按 `SKILL.md` 流程执行。

前置依赖：本机安装 Blender（后台模式）、Python 3、本地模型库（含各模型的 readme）。

## 目前没有适配的内容，可以提交pull来一起完善这个skill

本 skill **目前只覆盖「模型 / 场景」的作者标注**，以下需要标注作者的内容**尚未适配**：

- **动作（VMD / 外部导入的动作）** —— 只识别模型，不检测也不提取动作来源
- **插件 / 附加组件** —— 如 MikuMikuRig 等第三方插件的署名
- **材质 / 贴图 / 纹理** —— 材质若来自第三方需单独标注，本 skill 不处理
- **特效（MME Effect）、背景、音频等其它素材**

如果工程里混用了以上第三方内容，请另外标注其作者。

## 示例输出

```
角色：
八雲紫-Miy
レミリア スカーレット-雪萱

场景：
民家-ムムム
```

## 相关项目

- [KariHelper](https://github.com/swlt-silica/KariHelper) — skill整合的软件
