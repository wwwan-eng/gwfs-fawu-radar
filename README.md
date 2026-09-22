
# 广外就业 · 法务岗位雷达（自动监控版）

这个版本可以部署到 GitHub Pages，并由 GitHub Actions 每 30 分钟自动抓取广东外语外贸大学就业信息网的“招聘简讯”，分析正文中的法律/法务/合规关键词，然后更新网页数据。

## 为什么监控学校就业信息网
“广外就业”公众号是学校就业信息的重要发布渠道；学校官网也明确提供就业信息网。当前可直接稳定读取的公开来源是：
https://career.gdufs.edu.cn/web/Index/jobs-brief-list

## 部署步骤
1. 在 GitHub 新建一个 **Public repository**，例如 `gwfs-fawu-radar`。
2. 把本项目所有文件上传到仓库根目录。
3. 打开仓库 Settings → Pages。
4. Source 选择 `GitHub Actions`。
5. 在 Actions 中手动运行 `update-gwfs-fawu-radar` 一次。
6. GitHub Pages 部署完成后，会得到一个 `https://你的用户名.github.io/gwfs-fawu-radar/` 的网址。

## 自动更新
GitHub Actions 默认每 30 分钟执行一次；也可以在 Actions 页面手动运行。
网页本身每 5 分钟重新读取 `data/jobs.json`。

## 注意
- 微信公众号直接抓取存在访问限制，所以当前正式版先监控学校公开就业信息网，这是学校官方招聘信息源。
- 当前“法务判断”是关键词规则，不是大模型判断；因此网页会给出命中的关键词，方便你人工核对。
- 如果以后希望识别“没有写法务，但岗位实际属于法律/合规”的招聘，可以再接入 AI 分类。
