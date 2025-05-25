# 🏃‍♂️ Strava Dashboard v1.0.0

A beautiful, GitHub-style fitness visualization dashboard that automatically syncs with Strava every 8 hours.

## ✨ Features

- **GitHub-style Activity Heatmap**: Visualize your workout intensity with color-coded heatmaps
- **Circular Clock Visualization**: GitHubPoster-inspired daily activity distribution 
- **Best Performance Tracking**: Display longest distance and best pace achievements with city information
- **Automatic Data Sync**: Fetch latest activities from Strava API every 8 hours
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Multiple Color Schemes**: Nike-style and custom themes

## 🚀 Live Demo

**👉 [View Your Dashboard](https://onlinefchen.github.io/strava-view/) 👈**

## 🔧 Quick Setup

1. **Configure Strava API**:
   - Add your Strava credentials in Repository Settings > Secrets:
     - `STRAVA_CLIENT_ID`
     - `STRAVA_CLIENT_SECRET` 
     - `STRAVA_REFRESH_TOKEN`

2. **Enable GitHub Pages**:
   - Go to Settings > Pages
   - Source: Deploy from branch `gh-pages`

3. **Automatic Sync**:
   - Dashboard updates every 8 hours automatically
   - Manual sync available via GitHub Actions

## 📊 What's Included

- Interactive activity heatmaps (2024, 2025, All-time)
- Circular clock visualizations showing daily patterns
- Best performance statistics with location data
- Responsive web interface
- Automated data processing pipeline

## 🛠 Technical Stack

- **Frontend**: HTML5, CSS3, JavaScript, SVG
- **Backend**: Python with Strava API
- **Deployment**: GitHub Actions + GitHub Pages
- **Data Processing**: Automated statistics generation

---

**Ready to track your fitness journey?** 
🔗 **[Launch Dashboard](https://onlinefchen.github.io/strava-view/)**