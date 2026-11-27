# 运动计数器

液态玻璃风格的圆环运动计数器：由内到外转动圆环调整组数、个数、速度，点中心开始，Anna Su 真人语音报数。

- 网页：GitHub Pages 发布 `docs/` 文件夹。
- iPhone：Safari 打开 → 分享 → 添加到主屏幕；安卓：Chrome 菜单 → 添加到主屏幕。第一次打开后可以离线使用。

## 文件

| 路径 | 说明 |
|---|---|
| `index.html` | 计数器源码（也是 claude.ai 上发布的版本） |
| `voices/anna.json` | Anna Su 语音包（ElevenLabs eleven_v4 生成，1～200、开始、第 N 组完成、全部完成） |
| `tools/build_site.py` | 从 `index.html` 生成 `docs/`（补上网页头、主屏幕图标、离线缓存） |
| `tools/make_icons.py` | 生成主屏幕图标 |
| `docs/` | 实际发布到 GitHub Pages 的网站 |

改完 `index.html` 后运行 `python tools/build_site.py`，再提交 `docs/`。
