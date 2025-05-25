# 🏃‍♂️ Strava Activity Dashboard

*[中文版本](README_CN.md) | [English Version](README.md)*

> A beautiful, GitHub-style fitness visualization dashboard that automatically syncs with Strava every 8 hours.

## 🚀 Live Demo

**👉 [View Dashboard](https://onlinefchen.github.io/strava-view/) 👈**

[![Release](https://img.shields.io/github/v/release/onlinefchen/strava-view?style=flat-square)](https://github.com/onlinefchen/strava-view/releases)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-green?style=flat-square)](https://onlinefchen.github.io/strava-view/)
[![Auto Sync](https://img.shields.io/badge/Strava%20Sync-Every%208h-blue?style=flat-square)](#automatic-sync)

---

## ✨ Features

### 🎯 **Core Visualizations**
- **📊 GitHub-style Activity Heatmap**: Color-coded daily intensity visualization  
- **🕐 Circular Clock Chart**: GitHubPoster-inspired hourly activity distribution
- **🏆 Best Performance Tracking**: Longest runs and best pace with location data
- **📱 Responsive Design**: Perfect on desktop, tablet, and mobile

### 🔄 **Automated Data Pipeline**
- **⚡ Incremental Sync**: Lightning-fast updates using running_page's efficient strategy
- **🤖 Auto-deployment**: GitHub Actions updates every 8 hours
- **🗺️ Interactive Maps**: Mapbox integration for route visualization
- **📈 Real-time Statistics**: Activity count, distance, pace, streaks

### 🎨 **Customization**
- **🎨 Multiple Themes**: Nike-style and custom color schemes
- **👤 Personal Branding**: Custom avatar, signature, navigation links
- **📅 Yearly Views**: 2024, 2025, and all-time statistics
- **🌐 Bilingual Support**: English and Chinese interfaces

---

## 🚀 Quick Start

### 1. Fork & Configure

1. **Fork this repository** to your GitHub account
2. **Add Strava API credentials** in `Settings > Secrets and variables > Actions`:
   ```
   STRAVA_CLIENT_ID        # Your Strava app client ID
   STRAVA_CLIENT_SECRET    # Your Strava app client secret  
   STRAVA_REFRESH_TOKEN    # Your Strava refresh token
   MAPBOX_ACCESS_TOKEN     # Your Mapbox API token (optional)
   ```

### 2. Enable GitHub Pages

1. Go to `Settings > Pages`
2. Source: **Deploy from a branch**
3. Branch: **gh-pages**
4. Folder: **/ (root)**
5. Click **Save**

### 3. Get Strava API Access

1. **Create Strava App**: Visit [Strava API Settings](https://www.strava.com/settings/api)
2. **Get Authorization**: Visit authorization URL with your client ID:
   ```
   https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read,activity:read_all
   ```
3. **Extract Code**: Copy the `code` parameter from the redirect URL
4. **Get Refresh Token**: Exchange the code for a refresh token using your preferred API client

*Detailed setup guide available in [Strava API Setup](docs/strava-setup.md)*

---

## 🛠 Technical Architecture

### **Frontend Stack**
- **HTML5 + CSS3**: Responsive, modern web interface
- **Vanilla JavaScript**: No frameworks, fast loading
- **SVG Graphics**: Crisp visualizations at any scale
- **Mapbox GL JS**: Interactive route mapping

### **Backend & Automation**  
- **Python**: Data processing and visualization generation
- **GitHub Actions**: Automated sync every 8 hours
- **Strava API**: Real-time activity data fetching
- **GitHub Pages**: Zero-cost hosting and deployment

### **Performance Optimizations**
- **Incremental Sync**: Only fetch new activities (inspired by running_page)
- **Pre-generated SVGs**: Faster rendering, better SEO
- **Efficient API Usage**: Smart rate limiting and caching
- **Mobile-first Design**: Optimized for all screen sizes

---

## 📊 Visualization Gallery

### **Activity Heatmap**
GitHub-style contribution graph showing daily activity intensity with hover details and yearly summaries.

### **Circular Clock**
24-hour radial chart displaying when you're most active, helping identify optimal training times.

### **Best Performance Cards**
Showcase your longest distance and best pace achievements with location information and performance metrics.

### **Interactive Route Maps**
Click any activity to view detailed GPS tracks with elevation profiles and performance data.

---

## 🔧 Customization Guide

### **Personal Branding**
```javascript
// config.js
const CONFIG = {
    SIGNATURE: {
        line1: 'Keep Running',
        line2: 'Never Give Up'  
    },
    NAVIGATION_LINKS: {
        blog: { title: 'Blog', url: 'https://your-blog.com' },
        about: { title: 'About', url: 'https://your-about.com' }
    }
};
```

### **Visual Themes**
- Nike-inspired heatmap colors
- Custom color schemes in `styles.css`
- Responsive breakpoints for mobile optimization
- Personal avatar and profile customization

### **Data Processing**
- Modify `generate_visualizations.py` for custom charts
- Adjust heatmap intensity calculations
- Add new statistical metrics
- Custom city extraction from GPS data

---

## 🚀 Deployment Options

### **GitHub Pages (Recommended)**
✅ Free hosting  
✅ Automatic deployment  
✅ Custom domain support  
✅ SSL certificate included  

### **Cloudflare Pages**
1. Connect your GitHub repository
2. Build command: `python generate_visualizations.py`
3. Build output: `/`
4. Add environment variables

### **Local Development**
```bash
git clone https://github.com/onlinefchen/strava-view.git
cd strava-view
pip install -r requirements.txt
python sync_strava_data.py
python generate_visualizations.py  
python -m http.server 8000
```

---

## 📈 Performance & Analytics

### **Sync Efficiency**
- **Incremental Updates**: 90% fewer API calls vs full sync
- **7-day Buffer**: Ensures no missed activity updates
- **Rate Limiting**: Respectful API usage with automatic backoff
- **Progress Indicators**: Real-time sync status (`+` new, `.` updated)

### **Load Times**
- **Pre-generated SVGs**: Instant visualization loading
- **Optimized Assets**: Compressed images and minimal dependencies  
- **CDN Delivery**: GitHub Pages global distribution
- **Mobile Performance**: < 2s load time on 3G networks

---

## 🔒 Privacy & Security

- **Local Processing**: All data processing in your GitHub account
- **No Third-party Storage**: Data never leaves GitHub/Strava ecosystem
- **API Security**: Refresh tokens stored as GitHub Secrets
- **HTTPS Only**: Secure data transmission

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### **Development Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Generate sample data
python tools/generate_sample_data.py
```

---

## 📚 Documentation

- **[API Setup Guide](docs/strava-setup.md)**: Detailed Strava API configuration
- **[Customization Guide](docs/customization.md)**: Theming and personalization
- **[Deployment Guide](docs/deployment.md)**: Alternative hosting options
- **[Troubleshooting](docs/troubleshooting.md)**: Common issues and solutions

---

## 🙏 Acknowledgments

This project is inspired by and builds upon the excellent work of:

- **[running_page](https://github.com/yihong0618/running_page)** - Efficient data sync strategies
- **[GitHubPoster](https://github.com/yihong0618/GitHubPoster)** - Circular visualization concepts
- **GitHub Contribution Graph** - Heatmap design inspiration
- **Nike Run Club** - Performance tracking UI patterns

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- **🐛 Bug Reports**: [Open an Issue](https://github.com/onlinefchen/strava-view/issues)
- **💡 Feature Requests**: [Start a Discussion](https://github.com/onlinefchen/strava-view/discussions)  
- **📖 Documentation**: Check our [Wiki](https://github.com/onlinefchen/strava-view/wiki)
- **💬 Community**: Join our [Discord](https://discord.gg/strava-dashboard)

---

<div align="center">

**🏃‍♂️ Made with ❤️ for the running community**

[⭐ Star this repo](https://github.com/onlinefchen/strava-view/stargazers) • [🍴 Fork it](https://github.com/onlinefchen/strava-view/fork) • [📢 Share it](https://twitter.com/intent/tweet?text=Check%20out%20this%20amazing%20Strava%20dashboard!&url=https://github.com/onlinefchen/strava-view)

</div>