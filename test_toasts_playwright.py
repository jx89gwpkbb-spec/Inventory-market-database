"""Playwright E2E test for toast behavior.

Requires:
  pip install playwright
  playwright install

Run the app locally (python -m inventory.web) before running this test.
"""
from playwright.sync_api import sync_playwright
import time
import os
import datetime


def _ensure_screenshots_dir():
  path = os.path.join('reports', 'screenshots')
  os.makedirs(path, exist_ok=True)
  return path


def test_toast_on_create_user():
  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    # create context with video recording
    context = browser.new_context(record_video_dir="reports/videos")
    # start tracing (captures DOM snapshots, screenshots, sources)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    trace_path = None
    try:
      page.goto('http://127.0.0.1:5000/')
      # use switchboard quick create form
      page.fill('input[name="username"]', 'e2euser')
      page.fill('input[name="email"]', 'e2e@example.com')
      page.click('button:has-text("Create user")')
      # wait for toast container
      page.wait_for_selector('.toast-container .toast-item', timeout=3000)
      text = page.text_content('.toast-container .toast-item')
      assert 'e2euser' in text
    except Exception:
      # On failure, capture a screenshot, stop tracing and ensure video is saved
      screenshots_dir = _ensure_screenshots_dir()
      ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
      ss_path = os.path.join(screenshots_dir, f'toast_failure_{ts}.png')
      try:
        page.screenshot(path=ss_path, full_page=True)
      except Exception:
        pass
      # stop tracing and write trace zip
      try:
        trace_path = os.path.join('reports', f'trace_{ts}.zip')
        context.tracing.stop(path=trace_path)
      except Exception:
        trace_path = None
      # close context to finalize video
      try:
        context.close()
      except Exception:
        pass
      browser.close()
      raise
    else:
      # on success, stop tracing and save trace too (optional)
      try:
        ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        trace_path = os.path.join('reports', f'trace_{ts}.zip')
        context.tracing.stop(path=trace_path)
      except Exception:
        trace_path = None
    finally:
      try:
        context.close()
      except Exception:
        pass
      try:
        browser.close()
      except Exception:
        pass
