# DM Screen Configuration Guide

## The Problem
Many websites (like docs.google.com and open.spotify.com) block embedding in iframes for security reasons using X-Frame-Options headers. This means they won't load directly in the DM Screen.

## Solutions

### Google Docs
Instead of `https://docs.google.com`, use a specific document URL with embed mode:

**Format:**
```
https://docs.google.com/document/d/YOUR_DOCUMENT_ID/preview
```

**How to get it:**
1. Open your Google Doc
2. Click "File" → "Share" → "Publish to web" or "Share" → "Get link"
3. Copy the document ID from the URL (the long string after `/d/`)
4. Use the format above

**Example:**
```html
<iframe src="https://docs.google.com/document/d/1ABC123xyz/preview"></iframe>
```

### Spotify
Instead of `https://open.spotify.com`, use Spotify's embed URLs:

**Format for Playlists:**
```
https://open.spotify.com/embed/playlist/YOUR_PLAYLIST_ID
```

**Format for Albums:**
```
https://open.spotify.com/embed/album/YOUR_ALBUM_ID
```

**How to get it:**
1. Open Spotify (web or app)
2. Right-click on a playlist/album
3. Select "Share" → "Copy Embed Code" or "Copy Spotify URI"
4. Extract the ID from the URI or embed code
5. Use the format above

**Example:**
```html
<iframe src="https://open.spotify.com/embed/playlist/37i9dQZF1DXcBWIGoYBM5M"></iframe>
```

### Localhost:3000
This should work fine as long as your local server is running. No changes needed.

### Database (../../index.html)
This should work fine as it's a local file. No changes needed.

## How to Update URLs

Edit the `index.html` file and change the `src` attributes of the iframes:

```html
<!-- Top Left: Google Docs -->
<iframe src="https://docs.google.com/document/d/YOUR_DOC_ID/preview" title="Google Docs"></iframe>

<!-- Top Right: Spotify -->
<iframe src="https://open.spotify.com/embed/playlist/YOUR_PLAYLIST_ID" title="Spotify"></iframe>

<!-- Bottom Left: Local Server -->
<iframe src="http://localhost:3000" title="Local Server"></iframe>

<!-- Bottom Right: Database -->
<iframe src="../../index.html" title="Database"></iframe>
```

## Alternative: Open in Separate Windows

If you prefer not to use embeds, you can:
1. Click the "Open in New Tab" links shown in the fallback messages
2. Arrange your browser windows manually
3. Use the DM Screen for the embeddable content only

## Recommended Setup for D&D Sessions

1. **Top Left (Google Docs)**: Your session notes/adventure document
   - Create a Google Doc with your session notes
   - Publish it and get the embed URL
   
2. **Top Right (Spotify)**: Ambient music playlist
   - Create or find a D&D ambient music playlist
   - Get the embed URL
   
3. **Bottom Left (localhost:3000)**: Your custom tools/apps
   - Run whatever local development server you need
   
4. **Bottom Right (Database)**: The 5e Artisanal Database
   - This should work automatically

## Testing

After updating the URLs, refresh the page. If an iframe shows a fallback message:
- Check that the URL format is correct
- For Google Docs: Make sure the document is shared/published
- For Spotify: Make sure you're using the `/embed/` URL format
- For localhost: Make sure your server is running

