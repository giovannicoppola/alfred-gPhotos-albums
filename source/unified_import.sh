#!/bin/bash
# Unified script: Import albums from Google Photos (bulk or single)
# Detects whether user is on the albums list page or a single album page
# and runs the appropriate scraper, then imports to database

# Change to the script directory
cd "$(dirname "$0")"

# Run the unified scraper to detect page type and get JSON
json_output=$(osascript -l JavaScript <<'SCRAPER_EOF'

const frontmost_app_name = Application('System Events').applicationProcesses.where({ frontmost: true }).name()[0]
const frontmost_app = Application(frontmost_app_name)
const chromium_variants = ['Google Chrome', 'Chromium', 'Opera', 'Vivaldi', 'Brave Browser', 'Microsoft Edge']
const webkit_variants = ['Safari', 'Webkit']

const bookmarklet = `
(function() {
  try {
    var u = window.location.href;
    if (!u.includes('photos.google.com')) {
      return JSON.stringify({error: 'Not a Google Photos page'});
    }
    
    var isSingleAlbum = u.includes('/album/') || u.includes('/share/');
    
    if (isSingleAlbum) {
      var t = document.title.replace(' - Google Photos', '').trim();
      var b = document.body.innerText;
      var dateRange = null;
      var startDate = null;
      var endDate = null;
      
      // Try to match date range with year on end: "Nov 27 – 28, 2014"
      var dateMatch = b.match(/([A-Z][a-z]+ [0-9]{1,2})\\s*[–—-]\\s*([0-9]{1,2}),\\s*([0-9]{4})/);
      if (dateMatch && dateMatch[1] && dateMatch[2] && dateMatch[3]) {
        var monthDay1 = dateMatch[1].trim();  // "Nov 27"
        var day2 = dateMatch[2].trim();       // "28"
        var year = dateMatch[3].trim();       // "2014"
        startDate = monthDay1 + ', ' + year;  // "Nov 27, 2014"
        endDate = monthDay1.split(' ')[0] + ' ' + day2 + ', ' + year;  // "Nov 28, 2014"
        dateRange = monthDay1 + ' – ' + day2 + ', ' + year;
      } else {
        // Try to match date range with years on both: "Nov 27, 2014 – Nov 28, 2014"
        dateMatch = b.match(/([A-Z][a-z]+ [0-9]{1,2}, [0-9]{4})\\s*[–—-]\\s*([A-Z][a-z]+ [0-9]{1,2}, [0-9]{4})/);
        if (dateMatch && dateMatch[1] && dateMatch[2]) {
          startDate = dateMatch[1].trim();
          endDate = dateMatch[2].trim();
          dateRange = startDate + ' – ' + endDate;
        } else {
          // Try to match date range without year: "Nov 27 – Nov 28"
          dateMatch = b.match(/([A-Z][a-z]+ [0-9]{1,2})\\s*[–—-]\\s*([A-Z][a-z]+ [0-9]{1,2})/);
          if (dateMatch && dateMatch[1] && dateMatch[2]) {
            startDate = dateMatch[1].trim();
            endDate = dateMatch[2].trim();
            dateRange = startDate + ' – ' + endDate;
          } else {
            // Try single date with year: "Oct 30, 2024"
            dateMatch = b.match(/([A-Z][a-z]+ [0-9]{1,2}, [0-9]{4})/);
            if (dateMatch) {
              startDate = dateMatch[1].trim();
              dateRange = startDate;
            } else {
              // Try single date without year: "Oct 30"
              dateMatch = b.match(/([A-Z][a-z]+ [0-9]{1,2})/);
              if (dateMatch) {
                startDate = dateMatch[1].trim();
                dateRange = startDate;
              }
            }
          }
        }
      }
      
      var itemCount = 0;
      var countMatch = b.match(/(\\d+)\\s+(item|photo|image)s?/i);
      if (countMatch) {
        var count = parseInt(countMatch[1]);
        if (count < 10000) {
          itemCount = count;
        }
      }
      
      var r = {
        type: 'single',
        url: u, 
        title: t,
        itemCount: itemCount
      };
      
      if (dateRange) {
        r.dateRange = dateRange;
      }
      if (startDate) {
        r.startDate = startDate;
      }
      if (endDate) {
        r.endDate = endDate;
      }
      
      return JSON.stringify(r);
      
    } else if (u.includes('/albums')) {
      var albums = [];
      var albumLinks = document.querySelectorAll('a[href*="/album/"], a[href*="/share/"]');
      
      albumLinks.forEach(function(link) {
        var href = link.href;
        if (!href.includes('photos.google.com')) return;
        if (href.includes('/photo/')) return;
        
        if (href.includes('accounts.google.com')) return;
        if (href.includes('SignOutOptions')) return;
        
        var isAlbum = href.match(/photos\\.google\\.com\\/(album|share)\\//);
        if (!isAlbum) return;
        
        var titleText = '';
        if (link.getAttribute('aria-label')) {
          titleText = link.getAttribute('aria-label');
        } else if (link.textContent && link.textContent.trim()) {
          titleText = link.textContent.trim();
        }
        
        var itemCount = 0;
        if (titleText) {
          var titleCountMatch = titleText.match(/(\\d+)\\s*(item|photo|image)s?/i);
          if (titleCountMatch) {
            var count = parseInt(titleCountMatch[1]);
            if (count < 10000) {
              itemCount = count;
            }
          }
        }
        
        if (itemCount === 0) {
          var siblingText = '';
          var nextSibling = link.nextElementSibling;
          if (nextSibling) {
            siblingText += nextSibling.textContent || '';
          }
          var prevSibling = link.previousElementSibling;
          if (prevSibling) {
            siblingText += ' ' + (prevSibling.textContent || '');
          }
          if (siblingText) {
            var siblingCountMatch = siblingText.match(/(\\d+)\\s*(item|photo|image)s?/i);
            if (siblingCountMatch) {
              var count = parseInt(siblingCountMatch[1]);
              if (count < 10000) {
                itemCount = count;
              }
            }
          }
        }
        
        var title = titleText;
        title = title.replace(/\\d+\\s*(item|photo|image)s?\\b/gi, '');
        title = title.replace(/more\\s+options?/gi, '');
        title = title.replace(/\\s*[·•]\\s*shared\\s*$/gi, '');
        title = title.replace(/\\s+/g, ' ').trim();
        
        if (href && title && !albums.some(function(a) { return a.url === href; })) {
          albums.push({ 
            title: title, 
            url: href, 
            itemCount: itemCount 
          });
        }
      });
      
      if (albums.length === 0) {
        return JSON.stringify({error: 'No albums found on this page'});
      }
      
      return JSON.stringify({type: 'bulk', albums: albums});
      
    } else {
      return JSON.stringify({error: 'Not on an albums list or single album page'});
    }
  } catch (e) {
    return JSON.stringify({error: e.message});
  }
})();
`;

let result = ''
if (webkit_variants.some(app_name => frontmost_app_name.startsWith(app_name))) {
  result = frontmost_app.doJavaScript(bookmarklet, { in: frontmost_app.windows[0].currentTab })
} else if (chromium_variants.some(app_name => frontmost_app_name.startsWith(app_name))) {
  result = frontmost_app.windows[0].activeTab.execute({ javascript: bookmarklet })
} else {
  result = JSON.stringify({error: 'Unsupported browser'})
}

result

SCRAPER_EOF
)

# Check if scraper succeeded
scraper_exit_code=$?
if [ $scraper_exit_code -ne 0 ]; then
    echo '{"items": [{"title": "Error: Failed to scrape", "subtitle": "Could not access browser", "valid": false}]}'
    exit 1
fi

# Check if we got empty output
if [ -z "$json_output" ]; then
    echo '{"items": [{"title": "Error: No data", "subtitle": "No data received from browser", "valid": false}]}'
    exit 1
fi

# Pass the JSON to the unified Python import script
python3 unified_add_albums.py "$json_output"
