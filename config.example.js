// Configuration file example - Copy this to config.js and customize
const CONFIG = {
    // Your Mapbox access token (required)
    MAPBOX_ACCESS_TOKEN: 'your_mapbox_token_here',
    
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