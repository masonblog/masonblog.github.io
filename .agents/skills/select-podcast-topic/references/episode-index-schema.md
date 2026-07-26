# 单集覆盖索引规范

仅在覆盖索引缺失、失效、需要增量更新或需要全量审计时读取本文件。

索引文件为同目录下的 `episode-coverage.json`。它是从中文播客文字稿派生的语义索引，不是原文替代品。只有完整阅读对应版本的文字稿后，才能写入该版本的 `source_sha256`；不得根据标题、简介、目录或旧摘要直接更新哈希。

## 顶层结构

```json
{
  "schema_version": 1,
  "full_audit": {
    "completed_at": "YYYY-MM-DD",
    "through_episode": 11
  },
  "episodes": []
}
```

- `schema_version`：固定为 `1`。
- `full_audit.completed_at`：最近一次逐篇完整复核全部索引内文字稿的日期。尚未完成时为 `null`。
- `full_audit.through_episode`：该次全量复核覆盖的最高期数。尚未完成时为 `0`。
- `episodes`：按期数升序排列；每个源文件只能有一条记录。

## 单集条目

```json
{
  "episode": 11,
  "path": "content/post/blog20260722.md",
  "source_sha256": "64 位小写 SHA-256",
  "publication_state": "published",
  "indexed_at": "YYYY-MM-DD",
  "title": "与文字稿一致的标题",
  "date": "YYYY-MM-DD",
  "coverage": {
    "summary": "用具体、克制的语言概括事实线、制度线和论证落点。",
    "eras": ["时代或关键年份"],
    "jurisdictions": ["法域"],
    "people_or_cases": ["中心人物、案件或法律文件；确无具体对象时使用“无单一中心人物或案件”"],
    "legal_fields": ["法律部门"],
    "mechanisms": ["具体制度机制"],
    "core_question": "本集真正回答的一个核心法律史问题。",
    "central_claims": ["主要结论或论证节点"],
    "narrative_hook": "叙事入口及关键转折。",
    "source_types": ["主要一手与二手史料类型"],
    "present_connection": "与当下的连接及类比边界；没有时使用空字符串。",
    "overlap_notes": ["最容易与后续选题重复的机制、命题、人物或预期结论；没有明显重叠时写“暂无明显重叠”"],
    "expected_conclusion": "听众听完后应得到的核心认识，不拔高为原文没有支持的结论。"
  }
}
```

`published` 表示 `draft: false` 且未设 `hidden: true`；其他带有 `podcast:` 字段的中文文字稿记为 `planned`，用于避免撞题。不得索引 `.en.md` 译文。

## 更新规则

1. 运行 `scripts/check_episode_index.py --pretty`，以其 `missing`、`changed`、`incomplete`、`orphaned`、`podcast_page_only` 和 `duplicate_episodes` 分类为准。
2. 对 `missing` 或 `changed` 的源文件逐篇完整阅读，再新增或重写完整条目。不要只改哈希。
3. 对 `incomplete` 条目完整阅读源文件并补齐所有必填字段。
4. 对 `orphaned` 条目先检查源文件是否改名、失去 `podcast:` 字段或被删除；没有用户明确授权时不要直接删除记录，先说明差异。
5. 更新后再次运行检查脚本；只有条目语义字段完整且哈希与源文件一致，才会进入 `current`。
6. 完成全量审计时才更新 `full_audit`。只读了新增、变更或相似单集，不得推进 `full_audit.completed_at` 或 `through_episode`。
7. 保持 JSON 为 UTF-8、两空格缩进并以换行结尾。不要在索引中存放全文、大段引语、小宇宙实时指标或联网检索快照。
