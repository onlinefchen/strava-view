// Configuration file example - Copy this to config.js and customize
const CONFIG = {
    // Your Mapbox access token (required)
    MAPBOX_ACCESS_TOKEN: 'your_mapbox_token_here',
    
    // Timezone configuration - set your local timezone
    TIMEZONE: {
        offset: 8,  // UTC offset in hours (e.g., 8 for UTC+8 Beijing time, -5 for UTC-5 Eastern time)
        name: 'Asia/Shanghai'  // IANA timezone name (optional, for better accuracy)
        // Common examples:
        // Beijing/Shanghai: offset: 8, name: 'Asia/Shanghai'
        // New York: offset: -5, name: 'America/New_York' (EST) or offset: -4 (EDT)
        // London: offset: 0, name: 'Europe/London' (GMT) or offset: 1 (BST)  
        // Tokyo: offset: 9, name: 'Asia/Tokyo'
        // Los Angeles: offset: -8, name: 'America/Los_Angeles' (PST) or offset: -7 (PDT)
    },
    
    // Personal signature - customize your personal motto
    SIGNATURE: {
        line1: '数据见证力量',
        line2: '时间积累价值'
    },
    
    // Navigation links - customize these URLs to your own links
    NAVIGATION_LINKS: {
        summary: {
            title: 'Summary',
            url: 'summary.html',  // Link to summary page
            target: '_self'  // '_self' for same tab, '_blank' for new tab
        },
        blog: {
            title: 'Blog', 
            url: 'https://your-blog.com',  // Replace with your blog URL
            target: '_blank'
        },
        about: {
            title: 'About',
            url: 'https://your-about-page.com',  // Replace with your about page URL
            target: '_blank'
        }
    }
    
    // You can add more navigation links by adding more objects:
    // portfolio: {
    //     title: 'Portfolio',
    //     url: 'https://your-portfolio.com',
    //     target: '_blank'
    // },
    // contact: {
    //     title: 'Contact',
    //     url: 'mailto:your-email@example.com',
    //     target: '_self'
    // }
};