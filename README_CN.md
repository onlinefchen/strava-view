# 🏃‍♂️ Strava 活动仪表板

*[中文版本](README_CN.md) | [English Version](README.md)*

> 一个美观的 GitHub 风格健身可视化仪表板，每 8 小时自动与 Strava 同步数据。

## 🚀 在线演示

**👉 [查看仪表板](https://onlinefchen.github.io/strava-view/) 👈**

[![发布版本](https://img.shields.io/github/v/release/onlinefchen/strava-view?style=flat-square)](https://github.com/onlinefchen/strava-view/releases)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-在线-green?style=flat-square)](https://onlinefchen.github.io/strava-view/)
[![自动同步](https://img.shields.io/badge/Strava%20同步-每8小时-blue?style=flat-square)](#自动同步)

---

## ✨ 功能特色

### 🎯 **核心可视化**
- **📊 GitHub 风格活动热图**：彩色编码的每日强度可视化
- **🕐 圆形时钟图表**：GitHubPoster 风格的每小时活动分布
- **🏆 最佳表现追踪**：最长距离和最佳配速记录，包含位置信息
- **📱 响应式设计**：在桌面、平板和手机上完美显示

### 🔄 **自动化数据管道**
- **⚡ 增量同步**：采用 running_page 的高效策略实现闪电般快速更新
- **🤖 自动部署**：GitHub Actions 每 8 小时更新一次
- **🗺️ 交互式地图**：Mapbox 集成的路线可视化
- **📈 实时统计**：活动计数、距离、配速、连续记录

### 🎨 **个性化定制**
- **🎨 多种主题**：Nike 风格和自定义配色方案
- **👤 个人品牌**：自定义头像、签名、导航链接
- **📅 年度视图**：2024、2025 和历史统计数据
- **🌐 双语支持**：中英文界面

---

## 🚀 快速开始

### 1. Fork 和配置

1. **Fork 这个仓库**到您的 GitHub 账户
2. **添加 Strava API 凭据**在 `Settings > Secrets and variables > Actions` 中：
   ```
   STRAVA_CLIENT_ID        # 您的 Strava 应用客户端 ID
   STRAVA_CLIENT_SECRET    # 您的 Strava 应用客户端密钥
   STRAVA_REFRESH_TOKEN    # 您的 Strava 刷新令牌
   MAPBOX_ACCESS_TOKEN     # 您的 Mapbox API 令牌（可选）
   ```

### 2. 启用 GitHub Pages

1. 进入 `Settings > Pages`
2. 源：**Deploy from a branch**
3. 分支：**gh-pages**
4. 文件夹：**/ (root)**
5. 点击 **Save**

### 3. 获取 Strava API 访问权限

1. **创建 Strava 应用**：访问 [Strava API 设置](https://www.strava.com/settings/api)
2. **获取授权**：使用您的客户端 ID 访问授权 URL：
   ```
   https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read,activity:read_all
   ```
3. **提取代码**：从重定向 URL 中复制 `code` 参数
4. **获取刷新令牌**：使用您选择的 API 客户端将代码交换为刷新令牌

*详细设置指南请参阅 [Strava API 设置](docs/strava-setup.md)*

---

## 🛠 技术架构

### **前端技术栈**
- **HTML5 + CSS3**：响应式现代网页界面
- **原生 JavaScript**：无框架依赖，快速加载
- **SVG 图形**：任何尺寸下都清晰的可视化
- **Mapbox GL JS**：交互式路线地图

### **后端和自动化**
- **Python**：数据处理和可视化生成
- **GitHub Actions**：每 8 小时自动同步
- **Strava API**：实时活动数据获取
- **GitHub Pages**：零成本托管和部署

### **性能优化**
- **增量同步**：仅获取新活动（受 running_page 启发）
- **预生成 SVG**：更快渲染，更好的 SEO
- **高效 API 使用**：智能限流和缓存
- **移动优先设计**：针对所有屏幕尺寸优化

---

## 📊 可视化展示

### **活动热图**
GitHub 风格的贡献图，显示每日活动强度，带有悬停详情和年度摘要。

### **圆形时钟**
24 小时径向图表，显示您最活跃的时间段，帮助识别最佳训练时间。

### **最佳表现卡片**
展示您的最长距离和最佳配速成就，包含位置信息和表现指标。

### **交互式路线地图**
点击任何活动查看详细的 GPS 轨迹、海拔剖面和表现数据。

---

## 🔧 定制指南

### **个人品牌**
```javascript
// config.js
const CONFIG = {
    SIGNATURE: {
        line1: '坚持跑步',
        line2: '永不放弃'  
    },
    NAVIGATION_LINKS: {
        blog: { title: '博客', url: 'https://your-blog.com' },
        about: { title: '关于', url: 'https://your-about.com' }
    }
};
```

### **视觉主题**
- Nike 风格的热图配色
- `styles.css` 中的自定义配色方案
- 移动优化的响应式断点
- 个人头像和资料定制

### **数据处理**
- 修改 `generate_visualizations.py` 创建自定义图表
- 调整热图强度计算
- 添加新的统计指标
- 从 GPS 数据自定义城市提取

---

## 🚀 部署选项

### **GitHub Pages（推荐）**
✅ 免费托管
✅ 自动部署
✅ 自定义域名支持
✅ 包含 SSL 证书

### **Cloudflare Pages**
1. 连接您的 GitHub 仓库
2. 构建命令：`python generate_visualizations.py`
3. 构建输出：`/`
4. 添加环境变量

### **本地开发**
```bash
git clone https://github.com/onlinefchen/strava-view.git
cd strava-view
pip install -r requirements.txt
python sync_strava_data.py
python generate_visualizations.py  
python -m http.server 8000
```

---

## 📈 性能和分析

### **同步效率**
- **增量更新**：比全量同步减少 90% 的 API 调用
- **7 天缓冲**：确保不遗漏任何活动更新
- **限流控制**：尊重 API 使用，自动退避
- **进度指示器**：实时同步状态（`+` 新增，`.` 更新）

### **加载时间**
- **预生成 SVG**：可视化即时加载
- **优化资源**：压缩图片和最小依赖
- **CDN 传输**：GitHub Pages 全球分发
- **移动性能**：3G 网络下 < 2 秒加载时间

---

## 🔒 隐私和安全

- **本地处理**：所有数据处理在您的 GitHub 账户中进行
- **无第三方存储**：数据从不离开 GitHub/Strava 生态系统
- **API 安全**：刷新令牌存储为 GitHub Secrets
- **仅 HTTPS**：安全数据传输

---

## 🤝 贡献指南

我们欢迎贡献！以下是开始方式：

1. **Fork** 仓库
2. **创建**功能分支（`git checkout -b feature/amazing-feature`）
3. **提交**更改（`git commit -m 'Add amazing feature'`）
4. **推送**到分支（`git push origin feature/amazing-feature`）
5. **打开** Pull Request

### **开发环境设置**
```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/

# 生成示例数据
python tools/generate_sample_data.py
```

---

## 📚 文档

- **[API 设置指南](docs/strava-setup.md)**：详细的 Strava API 配置
- **[定制指南](docs/customization.md)**：主题和个性化
- **[部署指南](docs/deployment.md)**：替代托管选项
- **[故障排除](docs/troubleshooting.md)**：常见问题和解决方案

---

## 🙏 致谢

本项目的灵感来源于并构建在以下优秀项目的基础上：

- **[running_page](https://github.com/yihong0618/running_page)** - 高效数据同步策略
- **[GitHubPoster](https://github.com/yihong0618/GitHubPoster)** - 圆形可视化概念
- **GitHub 贡献图** - 热图设计灵感
- **Nike Run Club** - 性能跟踪 UI 模式

---

## 📄 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🆘 支持

- **🐛 错误报告**：[提交 Issue](https://github.com/onlinefchen/strava-view/issues)
- **💡 功能请求**：[发起讨论](https://github.com/onlinefchen/strava-view/discussions)
- **📖 文档**：查看我们的 [Wiki](https://github.com/onlinefchen/strava-view/wiki)
- **💬 社区**：加入我们的 [Discord](https://discord.gg/strava-dashboard)

---

<div align="center">

**🏃‍♂️ 为跑步社区用心制作**

[⭐ 给个星标](https://github.com/onlinefchen/strava-view/stargazers) • [🍴 Fork 一下](https://github.com/onlinefchen/strava-view/fork) • [📢 分享出去](https://twitter.com/intent/tweet?text=看看这个超棒的%20Strava%20仪表板！&url=https://github.com/onlinefchen/strava-view)

</div>