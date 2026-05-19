// Global variables
let activitiesData = [];
let statsData = {};
let map;
let thumbnailMap;
let currentYear = new Date().getFullYear();
let displayedActivities = 14; // Show only 14 activities initially
const activitiesPerPage = 14;

// Get timezone configuration from CONFIG
function getTimezoneConfig() {
    if (typeof CONFIG !== 'undefined' && CONFIG.TIMEZONE) {
        return {
            offset: CONFIG.TIMEZONE.offset || 8,
            name: CONFIG.TIMEZONE.name || 'Asia/Shanghai'
        };
    }
    // Default to UTC+8 (Beijing time) if not configured
    return { offset: 8, name: 'Asia/Shanghai' };
}

// Helper function to parse local datetime properly using configured timezone
function parseLocalDateTime(dateString) {
    if (!dateString) return null;
    
    const timezoneConfig = getTimezoneConfig();
    
    // If it ends with 'Z', it's UTC time, convert to configured local timezone
    if (dateString.endsWith('Z')) {
        const utcDate = new Date(dateString);
        // Convert to configured local time
        const configuredOffset = timezoneConfig.offset * 60; // hours to minutes
        const localOffset = utcDate.getTimezoneOffset(); // Local browser offset in minutes (negative for UTC+)
        const configuredTime = new Date(utcDate.getTime() + (configuredOffset + localOffset) * 60 * 1000);
        return configuredTime;
    } else {
        // Assume it's already local time
        return new Date(dateString);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', async function() {
    await loadActivitiesData();
    await loadStatsData();
    generateNavigationLinks();
    
    // Get initial year from year selector
    const yearSelect = document.getElementById('year-select');
    currentYear = yearSelect.value === 'all' ? 'all' : parseInt(yearSelect.value);
    
    initializeMap();
    renderActivitiesList();
    setupEventListeners();
    updateYearlyStats();
    updateLeftSidebarYear(currentYear);
    updateProfileFromConfig();
    updateTimezoneDisplay();
});

// Generate navigation links from config
function generateNavigationLinks() {
    const navContainer = document.getElementById('nav-links');
    const links = CONFIG.NAVIGATION_LINKS;
    
    navContainer.innerHTML = '';
    
    Object.keys(links).forEach(key => {
        const linkConfig = links[key];
        const linkElement = document.createElement('a');
        
        linkElement.href = linkConfig.url;
        linkElement.textContent = linkConfig.title;
        linkElement.className = 'nav-link';
        linkElement.target = linkConfig.target;
        
        // Add rel="noopener noreferrer" for external links
        if (linkConfig.target === '_blank') {
            linkElement.rel = 'noopener noreferrer';
        }
        
        navContainer.appendChild(linkElement);
    });
}

// Load activities data
async function loadActivitiesData() {
    try {
        const response = await fetch('./data/activities.json');
        activitiesData = await response.json();
        console.log('Loaded activities:', activitiesData.length);
    } catch (error) {
        console.error('Error loading activities data:', error);
    }
}

// Load pre-calculated stats data
async function loadStatsData() {
    try {
        const response = await fetch('./generated/stats.json');
        statsData = await response.json();
        console.log('Loaded stats for years:', Object.keys(statsData));
    } catch (error) {
        console.error('Error loading stats data:', error);
        statsData = {};
    }
}

// Initialize Mapbox map
function initializeMap() {
    // Get Mapbox token from config
    const mapboxToken = CONFIG.MAPBOX_ACCESS_TOKEN;
    
    if (!mapboxToken || mapboxToken === 'your_mapbox_token_here') {
        document.getElementById('map').innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #21262d; color: #8b949e;">Please add your Mapbox token to config.js file</div>';
        return;
    }
    
    mapboxgl.accessToken = mapboxToken;
    
    // Calculate center from all activities
    const center = calculateMapCenter();
    
    map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/dark-v10',
        center: center,
        zoom: 13
    });
    
    map.on('load', function() {
        displayAllRoutes();
    });
}

// Calculate map center from activities
function calculateMapCenter() {
    const validActivities = activitiesData.filter(activity => 
        activity.start_latlng && activity.start_latlng.length === 2
    );
    
    if (validActivities.length === 0) {
        return [121.588016, 31.113161]; // Default to Shanghai
    }
    
    const latSum = validActivities.reduce((sum, activity) => sum + activity.start_latlng[0], 0);
    const lngSum = validActivities.reduce((sum, activity) => sum + activity.start_latlng[1], 0);
    
    return [lngSum / validActivities.length, latSum / validActivities.length];
}

// Display all routes on map
// Get activities from last 6 months for better map bounds
function getRecentActivitiesForBounds() {
    const sixMonthsAgo = new Date();
    sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
    
    return activitiesData.filter(activity => {
        if (!activity.start_date_local) return false;
        const activityDate = parseLocalDateTime(activity.start_date_local);
        return activityDate >= sixMonthsAgo;
    });
}

function displayAllRoutes() {
    if (!map) return;
    
    const filteredActivities = getFilteredActivities();
    
    // Clear existing routes first
    clearMapRoutes();
    
    const bounds = new mapboxgl.LngLatBounds();
    let hasCoordinates = false;
    
    filteredActivities.forEach((activity, index) => {
        if (activity.map && activity.map.summary_polyline) {
            const polyline = activity.map.summary_polyline;
            const coordinates = decodePolyline(polyline);
            
            if (coordinates.length > 0) {
                const sourceId = `route-${index}`;
                const layerId = `route-layer-${index}`;
                
                map.addSource(sourceId, {
                    type: 'geojson',
                    data: {
                        type: 'Feature',
                        properties: {
                            activity: activity
                        },
                        geometry: {
                            type: 'LineString',
                            coordinates: coordinates
                        }
                    }
                });
                
                map.addLayer({
                    id: layerId,
                    type: 'line',
                    source: sourceId,
                    layout: {
                        'line-join': 'round',
                        'line-cap': 'round'
                    },
                    paint: {
                        'line-color': getActivityColor(activity),
                        'line-width': 2,
                        'line-opacity': 0.7
                    }
                });
                
                // Extend bounds to include this route
                coordinates.forEach(coord => bounds.extend(coord));
                hasCoordinates = true;
            }
        }
    });
    
    // Use recent activities to calculate better bounds for map fitting
    const recentActivities = getRecentActivitiesForBounds();
    const recentBounds = new mapboxgl.LngLatBounds();
    let hasRecentCoordinates = false;
    
    // Calculate bounds based on recent activities for better zoom
    recentActivities.forEach(activity => {
        if (activity.map && activity.map.summary_polyline) {
            const coordinates = decodePolyline(activity.map.summary_polyline);
            if (coordinates.length > 0) {
                coordinates.forEach(coord => recentBounds.extend(coord));
                hasRecentCoordinates = true;
            }
        }
    });
    
    // Use recent bounds if available, otherwise use all activities bounds
    const boundsToUse = hasRecentCoordinates ? recentBounds : bounds;
    const hasCoordinatesToUse = hasRecentCoordinates || hasCoordinates;
    
    // Fit map to show all routes with better zoom logic
    if (hasCoordinatesToUse) {
        // Calculate appropriate zoom level based on bounds size
        const sw = boundsToUse.getSouthWest();
        const ne = boundsToUse.getNorthEast();
        const latDiff = ne.lat - sw.lat;
        const lngDiff = ne.lng - sw.lng;
        const maxDiff = Math.max(latDiff, lngDiff);
        
        // Enhanced zoom levels for better route visibility
        let maxZoom = 15;
        
        // Special handling for recent activities (current year)
        const isCurrentYear = currentYear === new Date().getFullYear() || currentYear === 'all';
        const zoomBoost = isCurrentYear ? 1 : 0;
        
        if (maxDiff > 0.3) maxZoom = 10 + zoomBoost;      // Very large area
        else if (maxDiff > 0.15) maxZoom = 11 + zoomBoost; // Large area  
        else if (maxDiff > 0.08) maxZoom = 12 + zoomBoost; // Medium area
        else if (maxDiff > 0.04) maxZoom = 13 + zoomBoost; // Small area
        else if (maxDiff > 0.02) maxZoom = 14 + zoomBoost; // Very small area
        else if (maxDiff > 0.01) maxZoom = 15 + zoomBoost; // Tiny area
        else maxZoom = 16 + zoomBoost; // Very tiny area
        
        // Cap maximum zoom to prevent over-zooming
        maxZoom = Math.min(maxZoom, 17);
        
        // Use smaller padding and adjust for edge positioning
        map.fitBounds(boundsToUse, { 
            padding: { top: 40, bottom: 40, left: 60, right: 40 },
            maxZoom: maxZoom,
            duration: 800
        });
    }
}

// Get activity color based on type or other criteria
function getActivityColor(activity) {
    const colors = {
        'Run': '#ffb700',        // 亮黄色 - 跑步
        'Ride': '#f59e0b',       // 橙黄色 - 骑行
        'Walk': '#fbbf24',       // 浅黄色 - 步行
        'Hike': '#f97316',       // 橙色 - 徒步
        'Swim': '#06b6d4'        // 青色 - 游泳
    };
    return colors[activity.type] || '#ffb700';
}

// Display single activity route (only update main map, don't affect details)
function displaySingleRoute(activity) {
    console.log('Displaying single route for activity:', activity.name);
    
    // Display route on map (don't hide details)
    if (map && activity.map && activity.map.summary_polyline) {
        // Clear existing routes
        clearMapRoutes();
        
        const polyline = activity.map.summary_polyline;
        const coordinates = decodePolyline(polyline);
        
        if (coordinates.length > 0) {
            map.addSource('single-route', {
                type: 'geojson',
                data: {
                    type: 'Feature',
                    properties: {},
                    geometry: {
                        type: 'LineString',
                        coordinates: coordinates
                    }
                }
            });
            
            map.addLayer({
                id: 'single-route-layer',
                type: 'line',
                source: 'single-route',
                layout: {
                    'line-join': 'round',
                    'line-cap': 'round'
                },
                paint: {
                    'line-color': '#ffb700',
                    'line-width': 5,
                    'line-opacity': 0.95,
                    'line-blur': 0.5
                }
            });
            
            // Fit map to route bounds
            const bounds = new mapboxgl.LngLatBounds();
            coordinates.forEach(coord => bounds.extend(coord));
            
            // Calculate appropriate zoom for single route
            const sw = bounds.getSouthWest();
            const ne = bounds.getNorthEast();
            const latDiff = ne.lat - sw.lat;
            const lngDiff = ne.lng - sw.lng;
            const maxDiff = Math.max(latDiff, lngDiff);
            
            let maxZoom = 16;
            if (maxDiff > 0.05) maxZoom = 13;
            else if (maxDiff > 0.02) maxZoom = 14;
            else if (maxDiff > 0.01) maxZoom = 15;
            
            map.fitBounds(bounds, { 
                padding: { top: 60, bottom: 60, left: 60, right: 60 },
                maxZoom: maxZoom,
                duration: 800
            });
            
            console.log('Main map updated with route');
        }
    }
}

// Show activity details and thumbnail map (triggered by share button)
function showActivityShare(activity) {
    console.log('Showing activity share for:', activity.name);
    
    // Only show activity details overlay (don't update main map)
    showActivityDetails(activity);
}

// Show activity details
function showActivityDetails(activity) {
    const detailsOverlay = document.getElementById('activity-details-overlay');
    
    // Show details overlay
    detailsOverlay.style.display = 'block';
    
    // Update the title to show activity name
    const detailsTitle = document.getElementById('details-title');
    detailsTitle.textContent = activity.name;
    
    // Populate activity details
    const detailsContent = document.getElementById('details-content');
    const date = parseLocalDateTime(activity.start_date_local);
    
    detailsContent.innerHTML = `
        <div class="detail-item">
            <div class="detail-label">Activity Name</div>
            <div class="detail-value highlight">${activity.name}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Activity Type</div>
            <div class="detail-value">${activity.type}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Distance</div>
            <div class="detail-value highlight">${(activity.distance / 1000).toFixed(2)} km</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Moving Time</div>
            <div class="detail-value">${formatDuration(activity.moving_time)}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Elapsed Time</div>
            <div class="detail-value">${formatDuration(activity.elapsed_time)}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Average Pace</div>
            <div class="detail-value highlight">${calculatePace(activity)}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Average Speed</div>
            <div class="detail-value">${activity.average_speed ? (activity.average_speed * 3.6).toFixed(1) + ' km/h' : 'N/A'}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Max Speed</div>
            <div class="detail-value">${activity.max_speed ? (activity.max_speed * 3.6).toFixed(1) + ' km/h' : 'N/A'}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Average Heart Rate</div>
            <div class="detail-value">${activity.average_heartrate ? Math.round(activity.average_heartrate) + ' bpm' : 'N/A'}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Max Heart Rate</div>
            <div class="detail-value">${activity.max_heartrate ? Math.round(activity.max_heartrate) + ' bpm' : 'N/A'}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Elevation Gain</div>
            <div class="detail-value">${activity.total_elevation_gain ? activity.total_elevation_gain.toFixed(1) + ' m' : 'N/A'}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Start Time</div>
            <div class="detail-value">${formatFullDateTime(date)}</div>
        </div>
    `;
    
    // Always create/update thumbnail map (even if overlay is already shown)
    createThumbnailMap(activity);
}

// Hide activity details overlay
function hideActivityDetails() {
    const detailsOverlay = document.getElementById('activity-details-overlay');
    
    // Only hide if currently shown
    if (detailsOverlay.style.display === 'block') {
        console.log('Hiding activity details');
        // Hide details overlay
        detailsOverlay.style.display = 'none';
        
        // Destroy thumbnail map
        if (thumbnailMap) {
            thumbnailMap.remove();
            thumbnailMap = null;
        }
    }
}

// Reset map to show all routes
function resetMapToAllRoutes() {
    console.log('Resetting map to show all routes');
    clearMapRoutes();
    displayAllRoutes();
}

// Create thumbnail map for activity details
function createThumbnailMap(activity) {
    console.log('Creating thumbnail map for activity:', activity.name);
    const container = document.getElementById('activity-thumbnail-map');
    
    // Always destroy existing map first
    if (thumbnailMap) {
        console.log('Destroying existing thumbnail map');
        thumbnailMap.remove();
        thumbnailMap = null;
    }
    
    // Clear container
    container.innerHTML = '';
    
    if (!activity.map || !activity.map.summary_polyline) {
        container.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #21262d; color: #8b949e; border-radius: 8px;">No route data available</div>';
        return;
    }
    
    const mapboxToken = CONFIG.MAPBOX_ACCESS_TOKEN;
    if (!mapboxToken || mapboxToken === 'your_mapbox_token_here') {
        container.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #21262d; color: #8b949e; border-radius: 8px;">Mapbox token required</div>';
        return;
    }
    
    // Set token
    mapboxgl.accessToken = mapboxToken;
    
    // Decode polyline
    const coordinates = decodePolyline(activity.map.summary_polyline);
    if (coordinates.length === 0) {
        container.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #21262d; color: #8b949e; border-radius: 8px;">Invalid route data</div>';
        return;
    }
    
    // Calculate bounds
    const bounds = new mapboxgl.LngLatBounds();
    coordinates.forEach(coord => bounds.extend(coord));
    
    // Create a unique container ID to avoid conflicts
    const mapId = 'thumbnail-map-' + Date.now();
    container.innerHTML = `<div id="${mapId}" style="width: 100%; height: 100%;"></div>`;
    
    // Wait a moment for DOM to update, then create map
    setTimeout(() => {
        const mapContainer = document.getElementById(mapId);
        if (!mapContainer) return;
        
        // Create thumbnail map
        thumbnailMap = new mapboxgl.Map({
            container: mapId,
            style: 'mapbox://styles/mapbox/dark-v10',
            center: bounds.getCenter(),
            zoom: 12,
            interactive: false // Make it non-interactive for better screenshot experience
        });
        
        thumbnailMap.on('load', function() {
            // Add route to thumbnail map
            thumbnailMap.addSource('thumbnail-route', {
                type: 'geojson',
                data: {
                    type: 'Feature',
                    properties: {},
                    geometry: {
                        type: 'LineString',
                        coordinates: coordinates
                    }
                }
            });
            
            // Add route background (wider, darker line)
            thumbnailMap.addLayer({
                id: 'thumbnail-route-bg',
                type: 'line',
                source: 'thumbnail-route',
                layout: {
                    'line-join': 'round',
                    'line-cap': 'round'
                },
                paint: {
                    'line-color': '#1a1a1a',
                    'line-width': 6,
                    'line-opacity': 0.8
                }
            });
            
            // Add main route line
            thumbnailMap.addLayer({
                id: 'thumbnail-route-layer',
                type: 'line',
                source: 'thumbnail-route',
                layout: {
                    'line-join': 'round',
                    'line-cap': 'round'
                },
                paint: {
                    'line-color': '#ffb700',
                    'line-width': 4,
                    'line-opacity': 1,
                    'line-blur': 0.2
                }
            });
            
            // Add route highlight (thinner, brighter line)
            thumbnailMap.addLayer({
                id: 'thumbnail-route-highlight',
                type: 'line',
                source: 'thumbnail-route',
                layout: {
                    'line-join': 'round',
                    'line-cap': 'round'
                },
                paint: {
                    'line-color': '#ffd700',
                    'line-width': 2,
                    'line-opacity': 0.9
                }
            });
            
            // Fit to route bounds with appropriate padding
            thumbnailMap.fitBounds(bounds, { 
                padding: 30,
                duration: 0 // No animation for instant display
            });
        });
        
        thumbnailMap.on('error', function(e) {
            console.error('Thumbnail map error:', e);
            mapContainer.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #21262d; color: #8b949e; border-radius: 8px;">Map loading error</div>';
        });
    }, 100);
}

// Format full date and time
function formatFullDateTime(date) {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

// Clear all routes from map
function clearMapRoutes() {
    if (!map) return;
    
    const layers = map.getStyle().layers;
    const routeLayers = layers.filter(layer => layer.id.includes('route'));
    
    routeLayers.forEach(layer => {
        if (map.getLayer(layer.id)) {
            map.removeLayer(layer.id);
        }
        if (map.getSource(layer.source)) {
            map.removeSource(layer.source);
        }
    });
}

// Decode polyline string to coordinates
function decodePolyline(str, precision = 5) {
    let index = 0;
    let lat = 0;
    let lng = 0;
    const coordinates = [];
    let shift = 0;
    let result = 0;
    let byte = null;
    let latitude_change;
    let longitude_change;
    const factor = Math.pow(10, precision);

    while (index < str.length) {
        byte = null;
        shift = 0;
        result = 0;

        do {
            byte = str.charCodeAt(index++) - 63;
            result |= (byte & 0x1f) << shift;
            shift += 5;
        } while (byte >= 0x20);

        latitude_change = ((result & 1) ? ~(result >> 1) : (result >> 1));

        shift = result = 0;

        do {
            byte = str.charCodeAt(index++) - 63;
            result |= (byte & 0x1f) << shift;
            shift += 5;
        } while (byte >= 0x20);

        longitude_change = ((result & 1) ? ~(result >> 1) : (result >> 1));

        lat += latitude_change;
        lng += longitude_change;

        coordinates.push([lng / factor, lat / factor]);
    }

    return coordinates;
}



// Render activities list
function renderActivitiesList(reset = true) {
    const container = document.getElementById('activities-container');
    const filteredActivities = getFilteredActivities();
    const loadMoreContainer = document.getElementById('load-more-container');
    
    if (reset) {
        container.innerHTML = '';
        displayedActivities = activitiesPerPage;
    }
    
    // Get activities to display
    const activitiesToShow = filteredActivities.slice(0, displayedActivities);
    
    if (reset) {
        // Clear and render all
        activitiesToShow.forEach(activity => {
            const activityElement = createActivityElement(activity);
            container.appendChild(activityElement);
        });
    } else {
        // Add new activities only
        const startIndex = displayedActivities - activitiesPerPage;
        const newActivities = filteredActivities.slice(startIndex, displayedActivities);
        newActivities.forEach(activity => {
            const activityElement = createActivityElement(activity);
            container.appendChild(activityElement);
        });
    }
    
    // Show/hide load more button
    if (filteredActivities.length > displayedActivities) {
        loadMoreContainer.style.display = 'block';
    } else {
        loadMoreContainer.style.display = 'none';
    }
}

// Create single activity element
function createActivityElement(activity) {
    const div = document.createElement('div');
    div.className = 'activity-item';
    
    const date = parseLocalDateTime(activity.start_date_local);
    const distance = (activity.distance / 1000).toFixed(1);
    const pace = calculatePace(activity);
    const duration = formatDuration(activity.moving_time);
    const heartRate = activity.average_heartrate ? Math.round(activity.average_heartrate) : '--';
    
    // Format full date and time
    const formattedDateTime = formatFullDateTime(date);
    
    div.innerHTML = `
        <div class="activity-name">${activity.name}</div>
        <div class="activity-km">${distance}</div>
        <div class="activity-pace">${pace}</div>
        <div class="activity-bpm">${heartRate}</div>
        <div class="activity-time">${duration}</div>
        <div class="activity-date">${formattedDateTime}</div>
        <div class="activity-share">
            <button class="share-btn">Share</button>
        </div>
    `;
    
    // Make entire row clickable (except share button)
    div.style.cursor = 'pointer';
    div.onclick = () => {
        console.log('Activity row clicked:', activity.name);
        displaySingleRoute(activity);
    };
    
    // Make share button work
    const shareBtn = div.querySelector('.share-btn');
    shareBtn.onclick = (event) => {
        console.log('Share button clicked:', activity.name);
        event.stopPropagation(); // Prevent row click
        showActivityShare(activity);
    };
    
    return div;
}

// Calculate pace
function calculatePace(activity) {
    if (activity.moving_time && activity.distance) {
        const paceSeconds = activity.moving_time / (activity.distance / 1000);
        const minutes = Math.floor(paceSeconds / 60);
        const seconds = Math.floor(paceSeconds % 60);
        return `${minutes}:${seconds.toString().padStart(2, '0')}/km`;
    }
    return 'N/A';
}

// Format duration
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
}

// Get filtered activities based on current year
function getFilteredActivities() {
    if (currentYear === 'all') {
        return activitiesData;
    }
    
    return activitiesData.filter(activity => {
        const activityYear = parseLocalDateTime(activity.start_date_local).getFullYear();
        return activityYear === parseInt(currentYear);
    });
}

// Update yearly stats
function updateYearlyStats() {
    // Get stats for current year from pre-calculated data
    const yearKey = currentYear === 'all' ? '2025' : currentYear.toString(); // Default to 2025 for 'all'
    const yearStats = statsData[yearKey];
    
    if (!yearStats) {
        // Fallback to empty values if no data available
        document.getElementById('total-activities').textContent = '-';
        document.getElementById('total-distance').textContent = '-';
        document.getElementById('total-time').textContent = '-';
        document.getElementById('best-pace').textContent = '-';
        document.getElementById('heart-rate').textContent = '-';
        
        // Clear performance section
        document.getElementById('longest-distance').textContent = '-';
        document.getElementById('longest-city').textContent = '-';
        document.getElementById('longest-date').textContent = '-';
        document.getElementById('longest-duration').textContent = '-';
        document.getElementById('longest-pace').textContent = '-';
        document.getElementById('fastest-pace').textContent = '-';
        document.getElementById('fastest-city').textContent = '-';
        document.getElementById('fastest-date').textContent = '-';
        document.getElementById('fastest-distance').textContent = '-';
        document.getElementById('fastest-duration').textContent = '-';
        return;
    }
    
    // Update yearly stats DOM with pre-calculated data
    document.getElementById('total-activities').textContent = yearStats.total_activities;
    document.getElementById('total-distance').textContent = yearStats.total_distance;
    document.getElementById('total-time').textContent = yearStats.avg_pace;
    document.getElementById('best-pace').textContent = yearStats.best_pace;
    document.getElementById('heart-rate').textContent = yearStats.avg_heart_rate;
    
    // Update performance sections with pre-calculated data
    document.getElementById('longest-distance').textContent = yearStats.longest_distance;
    document.getElementById('longest-city').textContent = yearStats.longest_city;
    document.getElementById('longest-date').textContent = yearStats.longest_date;
    document.getElementById('longest-duration').textContent = yearStats.longest_duration;
    document.getElementById('longest-pace').textContent = yearStats.longest_pace;
    
    document.getElementById('fastest-pace').textContent = yearStats.fastest_pace;
    document.getElementById('fastest-city').textContent = yearStats.fastest_city;
    document.getElementById('fastest-date').textContent = yearStats.fastest_date;
    document.getElementById('fastest-distance').textContent = yearStats.fastest_distance;
    document.getElementById('fastest-duration').textContent = yearStats.fastest_duration;
}

// Update best performance section with the activity that has the best pace
function updateBestPerformance(activity) {
    if (!activity) {
        // Clear best performance data if no activity found
        document.getElementById('best-city').textContent = 'N/A';
        document.getElementById('best-start-time').textContent = 'N/A';
        document.getElementById('best-duration').textContent = 'N/A';
        document.getElementById('best-activity-pace').textContent = 'N/A';
        document.getElementById('best-distance').textContent = 'N/A';
        return;
    }
    
    // Extract city from location string (assuming format like "City, Country" or just "City")
    const city = activity.location ? activity.location.split(',')[0].trim() : 'Unknown';
    
    // Format start time (assuming start_date_local exists)
    const startTime = activity.start_date_local ? 
        parseLocalDateTime(activity.start_date_local).toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit', 
            hour12: false 
        }) : 'N/A';
    
    // Format duration
    const duration = formatTime(activity.moving_time);
    
    // Calculate average pace for this specific activity
    const avgPace = activity.moving_time / (activity.distance / 1000);
    
    // Format distance
    const distance = (activity.distance / 1000).toFixed(1) + ' km';
    
    // Update DOM elements
    document.getElementById('best-city').textContent = city;
    document.getElementById('best-start-time').textContent = startTime;
    document.getElementById('best-duration').textContent = duration;
    document.getElementById('best-activity-pace').textContent = formatPace(avgPace);
    document.getElementById('best-distance').textContent = distance;
}

// Calculate best pace from activities and return the activity details
function getBestPaceActivity(activities) {
    if (activities.length === 0) return null;
    
    let bestPace = Infinity;
    let bestActivity = null;
    
    activities.forEach(activity => {
        if (activity.moving_time && activity.distance && activity.distance > 1000) { // Only consider runs > 1km
            const pace = activity.moving_time / (activity.distance / 1000); // seconds per km
            if (pace < bestPace && pace > 180) { // Sanity check: pace should be > 3 minutes per km
                bestPace = pace;
                bestActivity = activity;
            }
        }
    });
    
    return bestActivity;
}

// Calculate best pace from activities (backward compatibility)
function calculateBestPace(activities) {
    const bestActivity = getBestPaceActivity(activities);
    if (!bestActivity) return 0;
    
    return bestActivity.moving_time / (bestActivity.distance / 1000);
}

// Calculate activity streak
function calculateStreak(activities) {
    if (activities.length === 0) return 0;
    
    const dates = activities
        .map(activity => parseLocalDateTime(activity.start_date_local).toDateString())
        .filter((date, index, arr) => arr.indexOf(date) === index)
        .sort((a, b) => new Date(b) - new Date(a));
    
    let streak = 1;
    const today = new Date().toDateString();
    
    if (dates[0] !== today) {
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        if (dates[0] !== yesterday.toDateString()) {
            return 0;
        }
    }
    
    for (let i = 1; i < dates.length; i++) {
        const currentDate = new Date(dates[i]);
        const previousDate = new Date(dates[i - 1]);
        const diffTime = previousDate - currentDate;
        const diffDays = diffTime / (1000 * 60 * 60 * 24);
        
        if (diffDays === 1) {
            streak++;
        } else {
            break;
        }
    }
    
    return streak;
}

// Format pace
function formatPace(paceSeconds) {
    if (!paceSeconds || isNaN(paceSeconds)) return 'N/A';
    
    const minutes = Math.floor(paceSeconds / 60);
    const seconds = Math.floor(paceSeconds % 60);
    return `${minutes}'${seconds.toString().padStart(2, '0')}"`;
}

// Load more activities
function loadMoreActivities() {
    displayedActivities += activitiesPerPage;
    renderActivitiesList(false); // Don't reset, just add more
}

// Setup event listeners
function setupEventListeners() {
    const yearSelect = document.getElementById('year-select');
    yearSelect.addEventListener('change', function() {
        currentYear = this.value === 'all' ? 'all' : parseInt(this.value);
        updateYearlyStats();
        renderActivitiesList(true); // Reset activities list
        hideActivityDetails(); // Hide details when changing year
        updateVisualizationsForYear(currentYear); // Update heatmap and clock
        updateLeftSidebarYear(currentYear); // Update left sidebar year display
        setTimeout(() => {
            resetMapToAllRoutes(); // Reset map to show all routes for new year
        }, 100);
    });
    
    // Load more button
    const loadMoreBtn = document.getElementById('load-more-btn');
    loadMoreBtn.addEventListener('click', loadMoreActivities);
    
    // Reset map button
    const resetMapBtn = document.getElementById('reset-map-btn');
    resetMapBtn.addEventListener('click', function() {
        console.log('Reset map button clicked');
        resetMapToAllRoutes();
    });
    
    // Close button for activity details
    const closeBtn = document.getElementById('close-details');
    closeBtn.addEventListener('click', hideActivityDetails);
    
    // ESC key to close activity details
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const detailsOverlay = document.getElementById('activity-details-overlay');
            if (detailsOverlay.style.display === 'block') {
                hideActivityDetails();
            }
        }
    });
    
    // Click outside details overlay to close it
    document.addEventListener('click', function(event) {
        const detailsOverlay = document.getElementById('activity-details-overlay');
        if (detailsOverlay.style.display === 'block') {
            // Check if click is outside the overlay
            if (!detailsOverlay.contains(event.target)) {
                console.log('Clicked outside details overlay, hiding details');
                hideActivityDetails();
            }
        }
    });
    
    
    // Initialize with current year
    updateYearlyStats();
}

// Update year display and show recent 2 years
function updateYearDisplay() {
    const currentYear = new Date().getFullYear();
    const previousYear = currentYear - 1;
    
    // Update year selector
    const yearSelect = document.getElementById('year-select');
    yearSelect.innerHTML = `
        <option value="all">All Years</option>
        <option value="${currentYear}" selected>${currentYear}</option>
        <option value="${previousYear}">${previousYear}</option>
    `;
    
    // Update left sidebar to show both years
    updateLeftSidebarForTwoYears(currentYear, previousYear);
}

// Update left sidebar year display
function updateLeftSidebarYear(selectedYear) {
    const yearElement = document.querySelector('.yearly-stats .year');
    if (yearElement) {
        if (selectedYear === 'all') {
            yearElement.textContent = 'All Years';
        } else {
            yearElement.textContent = selectedYear;
        }
    }
}

// Update visualizations (no longer needed in main page since moved to summary)
function updateVisualizationsForYear(selectedYear) {
    // Function kept for compatibility but no longer updates visualizations
    // Visualizations are now in summary.html
}

// Update left sidebar to show two years with divider
function updateLeftSidebarForTwoYears(currentYear, previousYear) {
    const leftColumn = document.querySelector('.left-column');
    
    // Clear existing yearly stats
    const existingStats = leftColumn.querySelector('.yearly-stats');
    if (existingStats) {
        existingStats.remove();
    }
    
    // Create stats for current year
    const currentYearStats = createYearStatsSection(currentYear, true);
    
    // Create divider
    const divider = document.createElement('div');
    divider.className = 'year-divider';
    divider.innerHTML = '<div class="divider-line"></div>';
    
    // Create stats for previous year  
    const previousYearStats = createYearStatsSection(previousYear, false);
    
    // Insert after profile section
    const profileSection = leftColumn.querySelector('.profile-section');
    profileSection.after(currentYearStats);
    currentYearStats.after(divider);
    divider.after(previousYearStats);
}

// Create year stats section
function createYearStatsSection(year, isCurrentYear) {
    const yearActivities = activitiesData.filter(activity => {
        const activityYear = parseLocalDateTime(activity.start_date_local).getFullYear();
        return activityYear === year;
    });
    
    const totalActivities = yearActivities.length;
    const totalDistance = yearActivities.reduce((sum, activity) => sum + activity.distance, 0) / 1000;
    const totalTime = yearActivities.reduce((sum, activity) => sum + activity.moving_time, 0);
    const avgPace = totalTime / (totalDistance || 1);
    const avgHeartRate = yearActivities
        .filter(activity => activity.average_heartrate)
        .reduce((sum, activity, _, arr) => sum + activity.average_heartrate / arr.length, 0);
    const bestPace = calculateBestPace(yearActivities);
    const streak = calculateStreak(yearActivities);
    
    const section = document.createElement('div');
    section.className = 'yearly-stats';
    section.innerHTML = `
        <div class="year">${year}</div>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">
                    <span class="stat-number">${totalActivities}</span>
                    <span class="stat-label">runs</span>
                </div>
            </div>
            <div class="stat-item">
                <div class="stat-value">
                    <span class="stat-number">${totalDistance.toFixed(1)}</span>
                    <span class="stat-label">km</span>
                </div>
            </div>
            <div class="stat-item">
                <div class="stat-value">
                    <span class="stat-number">${formatPace(avgPace)}</span>
                    <span class="stat-label">avg pace</span>
                </div>
            </div>
            <div class="stat-item">
                <div class="stat-value">
                    <span class="stat-number">${formatPace(bestPace)}</span>
                    <span class="stat-label">best pace</span>
                </div>
            </div>
            <div class="stat-item">
                <div class="stat-value">
                    <span class="stat-number">${Math.round(avgHeartRate) || 'N/A'}</span>
                    <span class="stat-label">avg bpm</span>
                </div>
            </div>
        </div>
    `;
    
    return section;
}

// Update timezone display
function updateTimezoneDisplay() {
    const timezoneConfig = getTimezoneConfig();
    const timezoneElement = document.getElementById('timezone-value');
    
    if (timezoneElement) {
        const offset = timezoneConfig.offset;
        const offsetString = `UTC${offset >= 0 ? '+' : ''}${offset}`;
        timezoneElement.textContent = offsetString;
    }
}

// Update profile from config
function updateProfileFromConfig() {
    // Update signature from config
    if (CONFIG.SIGNATURE) {
        const line1Element = document.getElementById('signature-line1');
        const line2Element = document.getElementById('signature-line2');
        const overlayLine1Element = document.getElementById('signature-overlay-line1');
        const overlayLine2Element = document.getElementById('signature-overlay-line2');
        
        if (line1Element && line2Element) {
            line1Element.textContent = CONFIG.SIGNATURE.line1 || '';
            line2Element.textContent = CONFIG.SIGNATURE.line2 || '';
        }
        
        if (overlayLine1Element && overlayLine2Element) {
            overlayLine1Element.textContent = CONFIG.SIGNATURE.line1 || '';
            overlayLine2Element.textContent = CONFIG.SIGNATURE.line2 || '';
        }
    }
    
    // Legacy support for old PROFILE config structure
    if (CONFIG.PROFILE) {
        const avatar = document.getElementById('avatar');
        const avatarOverlay = document.getElementById('avatar-overlay');
        
        // Update avatar if configured
        if (CONFIG.PROFILE.avatar) {
            avatar.src = CONFIG.PROFILE.avatar;
            if (avatarOverlay) {
                avatarOverlay.src = CONFIG.PROFILE.avatar;
            }
        }
        
        // Legacy signature support
        if (CONFIG.PROFILE.signature) {
            const line1Element = document.getElementById('signature-line1');
            const line2Element = document.getElementById('signature-line2');
            const overlayLine1Element = document.getElementById('signature-overlay-line1');
            const overlayLine2Element = document.getElementById('signature-overlay-line2');
            
            if (line1Element && line2Element) {
                line1Element.textContent = CONFIG.PROFILE.signature.line1 || '';
                line2Element.textContent = CONFIG.PROFILE.signature.line2 || '';
            }
            
            if (overlayLine1Element && overlayLine2Element) {
                overlayLine1Element.textContent = CONFIG.PROFILE.signature.line1 || '';
                overlayLine2Element.textContent = CONFIG.PROFILE.signature.line2 || '';
            }
        }
    }
}