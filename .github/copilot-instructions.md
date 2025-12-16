# AI Coding Agent Instructions for Python Crawler Course

## Project Overview
This is a **Python web scraping course** (2025) at 台北市職能發展學院 teaching practical web crawling, automation, and data extraction techniques. The project demonstrates progression from basics to advanced scraping patterns across 6 lessons.

## Architecture & Key Technologies

### Primary Tools
- **Playwright** (sync_api): Browser automation for form filling, AJAX handling, and dynamic content
- **crawl4ai**: High-level web crawling framework with async support and caching
- **Jupyter Notebooks (.ipynb)**: Interactive teaching/demonstration format
- **Python 3.10+**: Required (specified in `pyproject.toml`)

### Lesson Progression Structure
```
lesson03/  → Basics (requests, parsing, static sites)
lesson04/  → Form interaction, navigation (forms, logins, waiting)
lesson05/  → Dynamic content, AJAX, wait strategies
lesson06/  → Advanced crawling with crawl4ai library
```

## Key Patterns & Conventions

### 1. **Playwright Usage Pattern**
All Lesson 4-5 files follow this structure:
```python
from playwright.sync_api import sync_playwright
from time import sleep

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        # Page interactions here
        browser.close()

if __name__ == '__main__':
    main()
```

**Key conventions:**
- `headless=False`: Makes browser visible (debugging aid)
- `slow_mo=500`: 500ms delay between actions (readability)
- Always wrap in `with sync_playwright()` for resource cleanup
- Use absolute file paths via `Path(__file__).parent` for local HTML demos

### 2. **Dynamic Content Handling**
See [../lesson05/lesson5_1.py](../lesson05/lesson5_1.py) - demonstrates three wait strategies:
- `page.wait_for_load_state("networkidle")` → Network requests complete
- `page.wait_for_selector(selector, state="visible|hidden")` → DOM state changes
- `page.wait_for_function(js_condition)` → Custom JS conditions (AJAX polling)

### 3. **Async Pattern (Lesson 6)**
[../lesson06/lesson6_3.py](../lesson06/lesson6_3.py) shows crawl4ai async approach:
```python
async def main():
    browser_config = BrowserConfig(headless=False)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url='...', config=run_config)
```

## Developer Workflows

### Running Lessons
- **Notebooks** (`.ipynb`): Run in Jupyter/VS Code notebook interface
- **Python Scripts** (`.py`): Execute with `python lesson0X/lesson0X_Y.py`
- **Test HTML Files**: Local demos use `file:///absolute/path` URLs with local HTML fixtures

### Debugging Patterns
- Set `headless=False` to watch browser behavior
- Use `slow_mo=500` to slow interactions (default is fast)
- Enable `incognito=True` in BrowserConfig for isolated sessions
- Add `page.wait_for_timeout(ms)` for explicit delays when needed

### Dependencies
Managed via `uv` (pyproject.toml specifies `ipykernel>=7.1.0`, `playwright>=1.56.0`). Install with:
```bash
uv sync
```

## File Organization Practices

### HTML Demo Files
- [../lesson04/form_demo.html](../lesson04/form_demo.html), [../lesson04/login_demo.html](../lesson04/login_demo.html), [../lesson04/waiting_demo.html](../lesson04/waiting_demo.html)
- Local fixture files for teaching specific interaction patterns
- Accessed via `file://` protocol in Playwright

### Output Storage
- [../lesson06/output.md](../lesson06/output.md): Example markdown output from crawl4ai

## Critical Integration Points

1. **Playwright → Page Locators**: Use modern locator syntax (`page.locator()`, `page.fill()`, `page.click()`) not deprecated selectors
2. **File Path Handling**: Always use absolute paths for reproducibility across systems
3. **Resource Management**: `with` statements are mandatory for browser/crawler cleanup
4. **Async vs Sync**: Lesson 3-5 use sync API; Lesson 6 introduces async patterns

## Common Pitfalls to Avoid

- ❌ Forgetting `browser.close()` or using `with` statements
- ❌ Using relative file paths instead of `Path(__file__).parent` resolution
- ❌ Not waiting for network/DOM state after actions (causes flaky tests)
- ❌ Mixing sync/async patterns without proper context managers
- ❌ Running headless without explicit wait strategies

## When Modifying Existing Code
- Preserve lesson structure and progression intent
- Add comments in Chinese (teaching language) for clarity
- Maintain `if __name__ == '__main__'` patterns for executable scripts
- Keep HTML fixtures unchanged unless teaching new concepts
