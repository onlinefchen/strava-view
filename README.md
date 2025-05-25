# Strava Activity Visualization

A beautiful web-based dashboard to visualize your Strava running data, inspired by GitHub's contribution graph and modern fitness tracking interfaces.

## Features

- 📊 **Interactive Dashboard**: Two-column layout with personal stats and activity visualizations
- 🗺️ **Interactive Maps**: Mapbox integration showing all routes and individual activity tracks
- 🔥 **Activity Heatmap**: GitHub-style heatmap showing daily activity intensity
- 🕐 **Clock Visualization**: Radial chart displaying activity distribution by hour of day
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- 📈 **Yearly Statistics**: Activity count, distance, pace, and streak tracking
- 🎯 **Activity Details**: Click on individual activities to view their specific routes

## Demo

Visit the live demo: [https://onlinefchen.github.io/strava-view](https://onlinefchen.github.io/strava-view)

## Quick Start

### 1. Set Up Strava API Access

#### Option A: Use Strava API (Recommended for Auto-Sync)

1. **Create Strava Application:**
   - Go to [Strava API Settings](https://www.strava.com/settings/api)
   - Click "Create App"
   - Fill in the application details:
     - Application Name: Your app name
     - Category: Data Importer
     - Club: Leave blank
     - Website: Your website URL
     - Authorization Callback Domain: `localhost` (for development)

2. **Get API Credentials:**
   - Note down your `Client ID` and `Client Secret`
   - Get authorization code by visiting: 
     ```
     https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read,activity:read_all
     ```
   - Copy the `code` parameter from the redirect URL
   - Exchange for refresh token using curl or API client

3. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your Strava API credentials
   ```

#### Option B: Manual Data Export

1. Go to [Strava Settings](https://www.strava.com/settings/privacy)
2. Click "Request Your Archive" at the bottom of the page
3. Wait for Strava to prepare your data (can take up to 7 days)
4. Download and extract the ZIP file
5. Copy the `activities.json` file to the `data/` directory

### 2. Configure the Application

1. **Set up Mapbox:**
   - Create a free account at [Mapbox](https://www.mapbox.com/)
   - Go to your [Mapbox account page](https://account.mapbox.com/)
   - Navigate to "Access tokens" section
   - Copy your "Default public token" or create a new token
   - **Important**: The free tier includes 50,000 map loads per month, which is sufficient for personal use

2. **Create configuration file:**
   ```bash
   cp config.example.js config.js
   ```

3. **Edit config.js with your settings:**
   ```javascript
   const CONFIG = {
       // Add your Mapbox token
       MAPBOX_ACCESS_TOKEN: 'your_actual_token_here',
       
       // Customize your personal signature
       SIGNATURE: {
           line1: 'Your first line',
           line2: 'Your second line'
       },
       
       // Customize navigation links
       NAVIGATION_LINKS: {
           summary: {
               title: 'Summary',
               url: 'summary.html',
               target: '_self'
           },
           blog: {
               title: 'Blog', 
               url: 'https://your-blog.com',
               target: '_blank'
           },
           about: {
               title: 'About',
               url: 'https://your-about-page.com',
               target: '_blank'
           }
       }
   };
   ```

### 3. Run Locally

#### Option A: With Strava API Sync

```bash
# Clone the repository
git clone https://github.com/onlinefchen/strava-view.git
cd strava-view

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API credentials

# Sync data from Strava
python sync_strava_data.py

# Generate visualizations
python calculate_stats.py
python generate_visualizations.py

# Serve the files
python3 -m http.server 8000
```

#### Option B: Simple HTTP Server (Manual Data)

```bash
# Clone the repository
git clone https://github.com/onlinefchen/strava-view.git
cd strava-view

# Add your activities.json to data/ directory
# Generate visualizations
python3 generate_visualizations.py

# Serve the files (choose one):
python3 -m http.server 8000
# or
npx serve .
```

#### Option B: Using a Local Web Server

You can also use any local web server like XAMPP, WAMP, or serve the files through your preferred development environment.

### 4. Open in Browser

Navigate to `http://localhost:8000` (or your chosen port) to view your dashboard.

## Deployment

### GitHub Pages with Auto-Sync

1. **Fork this repository**

2. **Set up GitHub Secrets:**
   - Go to Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `STRAVA_CLIENT_ID`: Your Strava application client ID
     - `STRAVA_CLIENT_SECRET`: Your Strava application client secret  
     - `STRAVA_REFRESH_TOKEN`: Your Strava refresh token
     - `MAPBOX_ACCESS_TOKEN`: Your Mapbox API token

3. **Enable GitHub Pages:**
   - Go to Settings → Pages
   - Set Source to "GitHub Actions"

4. **Configure Auto-Sync:**
   - The workflow runs every 8 hours automatically
   - Or trigger manually from Actions tab
   - Data syncs from Strava API and updates visualizations
   - config.js is automatically generated with your Mapbox token

5. **Manual Data Setup (Alternative):**
   - Add your `activities.json` file to the `data/` directory
   - Manually edit `config.js` with your Mapbox token
   - Push to the `main` branch
   - GitHub Actions will deploy to GitHub Pages

### Cloudflare Pages

1. Connect your GitHub repository to Cloudflare Pages
2. Set the build command: `python generate_visualizations.py`
3. Set the build output directory: `/`
4. Add your Mapbox token as an environment variable
5. Deploy

### Custom Domain

To use a custom domain:

1. **GitHub Pages**: Add a `CNAME` file with your domain
2. **Cloudflare Pages**: Configure the custom domain in Cloudflare Pages settings

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `STRAVA_CLIENT_ID` | Your Strava application client ID | Yes (for API sync) |
| `STRAVA_CLIENT_SECRET` | Your Strava application client secret | Yes (for API sync) |
| `STRAVA_REFRESH_TOKEN` | Your Strava refresh token | Yes (for API sync) |
| `MAPBOX_ACCESS_TOKEN` | Your Mapbox API token | Yes |

### Customization

#### Personal Information

**Change Profile Avatar:**
1. Replace `avatar.png` with your own image (recommended size: 200x200px or larger)
2. Keep the filename as `avatar.png` or update the `src` attribute in `index.html`:
   ```html
   <img src="your-avatar-filename.jpg" alt="Profile Avatar" class="avatar" id="avatar">
   ```

**Update Personal Signature:**
Configure your personal motto in `config.js`:
```javascript
const CONFIG = {
    // Personal signature - customize your personal motto
    SIGNATURE: {
        line1: 'Your first line',
        line2: 'Your second line'
    },
    // ... other settings
};
```

**Configure Navigation Links:**
Edit the `NAVIGATION_LINKS` section in `config.js`:
```javascript
NAVIGATION_LINKS: {
    summary: {
        title: 'Summary',
        url: 'summary.html',  // Local page or external URL
        target: '_self'       // '_self' for same tab, '_blank' for new tab
    },
    blog: {
        title: 'Blog',
        url: 'https://your-blog.com',
        target: '_blank'
    }
}
```

**Set Default Year:**
In `index.html`, modify the year selector around line 100:
```html
<select id="year-select">
    <option value="all">All Years</option>
    <option value="2025" selected>2025</option>  <!-- Change 'selected' to your preferred year -->
    <option value="2024">2024</option>
</select>
```

#### Styling

Modify `styles.css` to change:
- Color scheme
- Layout dimensions
- Typography
- Responsive breakpoints

#### Data Processing

The `generate_visualizations.py` script can be customized to:
- Change heatmap intensity calculations
- Modify clock visualization parameters
- Add new statistical calculations

## File Structure

```
strava-view/
├── data/
│   ├── activities.json          # Your Strava data (auto-synced or manual)
│   └── sample/                  # Sample images
├── generated/                   # Auto-generated visualizations
├── .github/workflows/
│   └── sync-strava-data.yml    # GitHub Actions auto-sync workflow
├── index.html                  # Main HTML file
├── summary.html                # Summary page with heatmap and clock
├── styles.css                  # CSS styles
├── script.js                   # JavaScript functionality
├── sync_strava_data.py         # Strava API sync script
├── calculate_stats.py          # Statistics calculation script
├── generate_visualizations.py  # Visualization generation script
├── requirements.txt            # Python dependencies
├── avatar.png                  # Profile avatar (replace with yours)
├── .env.example               # Environment variables template
├── .env                       # Your environment variables (not committed)
├── wrangler.toml              # Cloudflare Pages configuration
└── README.md                  # This file
```

## Features Deep Dive

### Clock Visualization
- Shows activity distribution across 24 hours
- Bar length represents total distance for that hour
- Helps identify your preferred running times

### Activity Heatmap
- GitHub-style contribution graph
- Color intensity based on daily distance
- Hover to see exact statistics
- Shows activity consistency over time

### Interactive Map
- All activities displayed as colored routes
- Click individual activities to view detailed tracks
- Automatic map centering and zoom
- Support for different activity types (Run, Ride, Walk, Hike)

### Statistics Panel
- Real-time calculated statistics
- Activity count, total distance, average pace
- Current streak calculation
- Average heart rate (if available)

## Troubleshooting

### Common Issues

1. **Map not loading**: 
   - Check your Mapbox token is correctly set in `config.js`
   - Verify the token is a public token (starts with `pk.`)
   - Check browser console for error messages
   - Ensure the token hasn't expired or been revoked

2. **Map shows gray background**:
   - Your Mapbox token may have exceeded the free tier limit
   - Check your [Mapbox account usage](https://account.mapbox.com/)
   - Consider optimizing map loads or upgrading your plan

3. **No activities showing**: Ensure `activities.json` is in the `data/` directory

4. **Visualizations not generating**: Install Python dependencies: `pip install Pillow`

5. **Mobile layout issues**: Clear browser cache and reload

### Mapbox Configuration Guide

**Step-by-step Mapbox setup:**

1. **Create Account**: Go to [mapbox.com](https://www.mapbox.com/) and sign up
2. **Get Token**: 
   - After login, go to [Account → Access tokens](https://account.mapbox.com/access-tokens/)
   - Copy your "Default public token" (starts with `pk.`)
   - Or create a new token with these scopes:
     - `styles:tiles` (required for map display)
     - `fonts:read` (required for text labels)
3. **Configure**: Add the token to your `config.js`:
   ```javascript
   const CONFIG = {
       MAPBOX_ACCESS_TOKEN: 'pk.your_actual_token_here',
       // ... other settings
   };
   ```
4. **Test**: Open your site and check if maps load properly

**Token Security:**
- Public tokens are safe to expose in client-side code
- They're restricted to specific URLs (configure in Mapbox dashboard)
- Never use secret tokens in client-side code

### Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

### Performance

For large datasets (1000+ activities):
- Visualizations are pre-generated for better performance
- Map routes are optimized for rendering
- Responsive design ensures good mobile performance

## Development

### Prerequisites

- Python 3.7+
- Modern web browser
- Code editor

### Setup for Development

```bash
# Clone the repository
git clone https://github.com/onlinefchen/strava-view.git
cd strava-view

# Install Python dependencies
pip install Pillow

# Set up environment variables
cp .env.example .env
# Edit .env with your Mapbox token

# Generate sample visualizations
python3 generate_visualizations.py

# Start development server
python3 -m http.server 8000
```

### Making Changes

1. **HTML/CSS/JS**: Edit directly and refresh browser
2. **Python scripts**: Run `python3 generate_visualizations.py` after changes
3. **Styling**: Modify `styles.css` for visual changes
4. **Functionality**: Update `script.js` for interactive features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Privacy

- All data processing happens locally in your browser
- No data is sent to external servers (except Mapbox for map tiles)
- Your Strava data remains private and secure

## License

MIT License - see LICENSE file for details

## Support

- 🐛 **Bug Reports**: [Open an issue](https://github.com/onlinefchen/strava-view/issues)
- 💡 **Feature Requests**: [Start a discussion](https://github.com/onlinefchen/strava-view/discussions)
- 📖 **Documentation**: Check this README or the wiki

## Acknowledgments

- Inspired by GitHub's contribution graph
- Built with Mapbox GL JS for beautiful maps
- Designed for the running community

---

**Made with ❤️ for runners everywhere**