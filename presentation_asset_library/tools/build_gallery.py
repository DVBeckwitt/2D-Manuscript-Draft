#!/usr/bin/env python3
"""Build the portable, offline asset gallery from catalog.json (Python 3.9+).

No third-party packages, network calls, or browser JSON fetches are required.
The generated page contains the complete catalog as ordinary readable HTML;
JavaScript only adds filtering and accessible result counts.
"""

from __future__ import annotations

import html
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import quote


ROOT = Path(__file__).resolve().parent.parent


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def local_url(value: object) -> str:
    """Reject paths that cannot travel with this offline archive."""
    path = str(value).replace("\\", "/")
    if not path or path.startswith("/") or ":" in path or ".." in PurePosixPath(path).parts:
        raise ValueError(f"Expected an archive-relative path: {value!r}")
    return quote(path, safe="/")


def anchor_id(value: object) -> str:
    return "asset-" + re.sub(r"[^A-Za-z0-9_-]+", "-", str(value)).strip("-")


def prose(value: object, css: str = "") -> str:
    if not value:
        return ""
    items = value if isinstance(value, list) else [value]
    return "".join(f'<p class="{esc(css)}">{esc(item)}</p>' for item in items if item)


def file_link(path: object, label: object, css: str = "", download: bool = False) -> str:
    return (f'<a class="{esc(css)}" href="{local_url(path)}"'
            f'{" download" if download else ""}>{esc(label)}</a>')


def human_size(value: object) -> str:
    number = float(value or 0)
    if number >= 1024 ** 3:
        return f"{number / 1024 ** 3:.1f} GB"
    if number >= 1024 ** 2:
        return f"{number / 1024 ** 2:.1f} MB"
    return f"{number / 1024:.0f} KB"


def duration(value: object) -> str:
    if value is None:
        return ""
    try:
        seconds = float(value)
        return f"{seconds:g} s"
    except (TypeError, ValueError):
        return str(value)


def source_list(items: list[dict], css: str = "file-list") -> str:
    if not items:
        return ""
    rows = []
    for item in items:
        label = item.get("label") or Path(item["path"]).name
        format_name = item.get("format", "").upper()
        description = item.get("description", "")
        rows.append('<li>' + file_link(item["path"], label) +
                    (f'<span class="file-format">{esc(format_name)}</span>' if format_name else "") +
                    (f'<small>{esc(description)}</small>' if description else "") + '</li>')
    return f'<ul class="{css}">' + "".join(rows) + '</ul>'


def asset_media(asset: dict) -> str:
    preferred = asset.get("preferred") or {}
    path = preferred.get("path")
    if not path:
        return '<div class="media-placeholder">See archived sources below</div>'
    fmt = str(preferred.get("format", Path(path).suffix[1:])).lower()
    preview = preferred.get("preview") or asset.get("preview")
    if fmt in ("mp4", "webm", "mov", "m4v"):
        poster = f' poster="{local_url(preview)}"' if preview else ""
        mime = {"mp4": "video/mp4", "m4v": "video/mp4", "webm": "video/webm", "mov": "video/quicktime"}[fmt]
        return (f'<video controls playsinline preload="none"{poster} aria-label="{esc(asset["title"])}">'
                f'<source src="{local_url(path)}" type="{mime}">'
                + file_link(path, "Open animation") + '</video>')
    if fmt in ("png", "jpg", "jpeg", "svg", "gif", "webp", "avif"):
        image_path = preview or path
        return (f'<a class="image-link" href="{local_url(path)}" aria-label="Open {esc(asset["title"])} at full size">'
                f'<img src="{local_url(image_path)}" alt="{esc(asset["title"])}" loading="lazy" decoding="async"></a>')
    if preview:
        return (f'<a class="image-link" href="{local_url(path)}">'
                f'<img src="{local_url(preview)}" alt="{esc(asset["title"])}" loading="lazy" decoding="async"></a>')
    return '<div class="media-placeholder">' + file_link(path, 'Open ' + asset.get("kind", "asset")) + '</div>'


def asset_card(asset: dict) -> str:
    asset_id = anchor_id(asset["id"])
    slides = asset.get("slide_uses", [])
    slide_links = ", ".join(f'<a class="slide-jump" href="#slide-{int(number):02d}">{int(number)}</a>' for number in slides)
    preferred = asset.get("preferred") or {}
    format_name = str(preferred.get("format", "")).upper()
    length = duration(preferred.get("duration_seconds"))
    status = asset.get("status", "")
    kind = asset.get("kind", "figure")
    search_text = " ".join(str(asset.get(key, "")) for key in ("title", "description", "usage", "limitations", "status", "id"))
    search_text += " " + " ".join(f"slide {number}" for number in slides)
    tag = 'In this deck' if slides else 'Library alternative'
    variants = asset.get("variants", [])
    sources = asset.get("sources", [])
    details = ""
    if variants or sources:
        details = '<details class="asset-details"><summary>Versions &amp; sources'
        details += f'<span>{len(variants)} variants · {len(sources)} sources</span></summary>'
        if variants:
            details += '<h4>Other archived versions</h4>' + source_list(variants)
        if sources:
            details += '<h4>Data, generators &amp; provenance</h4>' + source_list(sources)
        details += '</details>'
    preferred_download = ""
    if preferred.get("path"):
        preferred_download = file_link(preferred["path"], f'Open {format_name or "asset"}', "text-action")
        if preferred.get("preview"):
            preferred_download += file_link(preferred["preview"], "Still / preview", "text-action")
    meta = " · ".join(esc(item) for item in (kind.capitalize(), format_name, length) if item)
    return f'''<article class="asset-card catalog-item" id="{asset_id}" data-kind="{esc(kind)}" data-in-ppt="{str(bool(slides)).lower()}" data-search="{esc(search_text.lower())}" tabindex="-1">
      <div class="card-media">{asset_media(asset)}</div>
      <div class="card-body">
        <div class="card-meta"><span>{meta}</span><span class="tag {'tag-used' if slides else ''}">{tag}</span></div>
        <h3>{esc(asset['title'])}</h3>
        {prose(asset.get('description'), 'purpose')}
        {f'<p class="deck-use">Used on slide{ "s" if len(slides) != 1 else ""} {slide_links}</p>' if slides else ''}
        {f'<div class="context"><span class="context-label">Use</span>{prose(asset.get("usage"))}</div>' if asset.get("usage") else ''}
        {f'<div class="context limits"><span class="context-label">Reading the figure</span>{prose(asset.get("limitations"))}</div>' if asset.get("limitations") else ''}
        {f'<p class="status"><strong>Status:</strong> {esc(status)}</p>' if status else ''}
        <div class="file-actions">{preferred_download}</div>
        {details}
      </div>
    </article>'''


def slide_card(slide: dict, assets: dict) -> str:
    number = int(slide["number"])
    related = []
    for asset_id in slide.get("asset_ids", []):
        asset = assets.get(asset_id)
        if asset:
            related.append(f'<li><a class="asset-jump" href="#{anchor_id(asset_id)}">{esc(asset["title"])}</a></li>')
    links = ''
    if slide.get("notes_path"):
        links += file_link(slide["notes_path"], "Speaker notes", "text-action")
    search_text = f"slide {number} {slide.get('title', '')}"
    return f'''<article class="slide-card catalog-item" id="slide-{number:02d}" data-kind="slide" data-in-ppt="true" data-search="{esc(search_text.lower())}" tabindex="-1">
      <a class="image-link" href="{local_url(slide['preview'])}" aria-label="Open slide {number}: {esc(slide.get('title', ''))}">
        <img src="{local_url(slide['preview'])}" alt="Slide {number}: {esc(slide.get('title', ''))}" loading="lazy" decoding="async">
      </a>
      <div class="slide-body"><span class="slide-number">{number:02d}</span><h3>{esc(slide.get('title') or 'Untitled slide')}</h3>
      <div class="file-actions">{links}</div>{'<ul class="related-assets">' + ''.join(related) + '</ul>' if related else ''}</div>
    </article>'''


CSS = r"""
:root{color-scheme:light;--ink:#18313f;--muted:#4b616c;--teal:#006f82;--teal-dark:#005264;--surface:#fff;--canvas:#f5f7f7;--line:#d5e0e4;--soft:#e8f3f3;--warm:#fff5df;--focus:#c87800;--radius:6px}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:150px}body{margin:0;background:var(--canvas);color:var(--ink);font:16px/1.55 'Segoe UI',Arial,sans-serif}a{color:var(--teal);text-underline-offset:3px;text-decoration-thickness:1px}a:hover{color:var(--teal-dark)}button,input{font:inherit}button,a,input,summary,video{outline-offset:4px}:focus-visible{outline:3px solid var(--focus)}[hidden]{display:none!important}img,video{max-width:100%}.wrap{width:min(1440px,calc(100% - 64px));margin-inline:auto}.skip-link{position:absolute;top:-100px;left:24px;background:white;padding:12px;z-index:50}.skip-link:focus{top:12px}.masthead{background:var(--surface);border-top:5px solid var(--teal);border-bottom:1px solid var(--line)}.masthead .wrap{display:flex;align-items:center;justify-content:space-between;gap:24px;padding-block:18px}.brand{font-weight:650;letter-spacing:.02em}.release{font-family:Consolas,'Courier New',monospace;font-size:13px;color:var(--muted)}.intro{padding-top:40px;padding-bottom:32px}.eyebrow{font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--teal);margin:0 0 8px}h1{font-size:clamp(30px,4vw,46px);font-weight:650;line-height:1.12;letter-spacing:-.025em;margin:0 0 12px}.intro-text{font-size:18px;max-width:860px;color:var(--muted);margin:0}.deck-panel{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:32px;align-items:center;margin:24px 0 0;padding:24px;background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--teal);border-radius:var(--radius)}.deck-panel h2{font-size:22px;margin:0 0 8px;line-height:1.25}.deck-panel p{margin:8px 0}.deck-meta{font-size:14px;color:var(--muted)}.deck-preview{display:block;border:1px solid var(--line);background:white;line-height:0}.deck-preview img{display:block;width:100%;aspect-ratio:16/9;object-fit:contain}.deck-actions{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:16px 0}.button{display:inline-flex;align-items:center;justify-content:center;min-height:44px;gap:8px;padding:10px 18px;border:1px solid var(--teal);border-radius:4px;text-decoration:none;font-size:14px;font-weight:650;background:var(--teal);color:white}.button:hover{background:var(--teal-dark);color:white}.button.secondary{background:white;color:var(--teal)}.button.secondary:hover{background:var(--soft)}.sha{max-width:100%;font:11px/1.5 Consolas,'Courier New',monospace;color:var(--muted);overflow-wrap:anywhere}.help-links{display:flex;flex-wrap:wrap;gap:8px 22px;padding-top:16px;font-size:14px}.toolbar{background:var(--surface);border-block:1px solid var(--line);position:sticky;top:0;z-index:10;box-shadow:0 2px 5px #18313f08}.toolbar .wrap{display:flex;gap:16px;align-items:center;justify-content:space-between;padding-block:14px;flex-wrap:wrap}.filter-group{display:flex;gap:5px;flex-wrap:wrap}.filter{min-height:40px;padding:7px 13px;cursor:pointer;background:transparent;border:1px solid transparent;border-radius:4px;color:var(--muted);font-size:14px}.filter:hover{background:var(--canvas);color:var(--ink)}.filter[aria-pressed="true"]{background:var(--soft);border-color:#b5d5da;color:var(--teal-dark);font-weight:650}.search{display:flex;align-items:center;gap:10px;flex:1;max-width:345px;min-width:240px}.search label{font-size:14px;font-weight:600}.search input{min-height:40px;min-width:0;width:100%;border:1px solid #aebfc6;border-radius:4px;padding:7px 11px;background:#fff;color:var(--ink);font-size:14px}.result-line{display:flex;justify-content:space-between;gap:16px;align-items:baseline;margin:24px 0 12px;color:var(--muted);font-size:14px}.result-line p{margin:0}.quiet-link{font-size:13px}.section-heading{display:flex;justify-content:space-between;align-items:baseline;gap:20px;margin:24px 0 16px}.section-heading h2{margin:0;font-size:25px;font-weight:650;letter-spacing:-.015em}.section-heading p{font-size:14px;color:var(--muted);margin:0}.asset-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;align-items:start}.asset-card{min-width:0;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;scroll-margin-top:145px}.card-media{background:white;aspect-ratio:16/9;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:center}.card-media video,.card-media .image-link,.card-media img{display:block;width:100%;height:100%;object-fit:contain}.card-media video{background:white}.image-link{display:block;line-height:0}.media-placeholder{width:100%;height:100%;min-height:200px;display:flex;align-items:center;justify-content:center;font-size:20px;background:var(--soft)}.card-body{padding:22px 24px 0}.card-meta{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;font-size:12px;color:var(--muted);margin:0 0 12px}.tag{font-size:11px;padding:3px 7px;border:1px solid var(--line);border-radius:3px;font-weight:650}.tag-used{color:var(--teal-dark);background:var(--soft);border-color:#b5d5da}.asset-card h3{font-size:23px;font-weight:650;letter-spacing:-.015em;line-height:1.22;margin:0 0 12px}.purpose{font-size:16px;margin:0 0 12px}.deck-use{font-size:13px;margin:0 0 16px;color:var(--muted)}.deck-use a{display:inline-flex;align-items:center;justify-content:center;min-width:26px;min-height:26px;background:var(--soft);border-radius:3px;font-weight:650;text-decoration:none}.context{margin:16px 0;font-size:14px}.context-label{display:block;font-size:11px;letter-spacing:.06em;text-transform:uppercase;font-weight:700;margin-bottom:4px;color:var(--muted)}.context p{margin:4px 0}.limits{border-left:2px solid #bfd0d5;padding-left:12px;color:var(--muted)}.status{font-size:12px;color:var(--muted);margin:16px 0}.status strong{font-weight:650}.file-actions{display:flex;flex-wrap:wrap;gap:12px 20px;padding:0 0 18px}.text-action{font-size:13px;min-height:28px;display:inline-flex;align-items:center;font-weight:600}.asset-details{margin:0 -24px;padding:0 24px;border-top:1px solid var(--line);background:#fafcfc;font-size:13px}.asset-details summary{cursor:pointer;padding:15px 0;font-weight:600}.asset-details summary span{margin-left:10px;font-weight:400;font-size:11px;color:var(--muted)}.asset-details h4{font-size:12px;font-weight:700;margin:8px 0 8px}.file-list{list-style:none;margin:0 0 20px;padding:0;display:grid;gap:9px}.file-list li{overflow-wrap:anywhere}.file-list small{display:block;color:var(--muted);line-height:1.4;margin-top:3px}.file-format{margin-left:8px;color:var(--muted);font-size:10px}.slide-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px;align-items:start}.slide-card{min-width:0;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;scroll-margin-top:145px}.slide-card img{display:block;width:100%;aspect-ratio:16/9;object-fit:contain;border-bottom:1px solid var(--line)}.slide-body{padding:14px 16px 0}.slide-number{font-size:11px;color:var(--teal);font-weight:700;font-family:Consolas,monospace}.slide-card h3{font-size:15px;line-height:1.35;margin:5px 0 10px;font-weight:650}.slide-card .file-actions{padding-bottom:10px}.related-assets{font-size:12px;padding:0 0 16px 16px;margin:0;color:var(--muted)}.related-assets li{margin:4px 0}.empty{padding:40px 24px;background:white;border:1px solid var(--line);text-align:center;margin-block:24px}.empty h2{font-size:23px;margin:0 0 8px}.empty p{color:var(--muted);margin:0 0 16px}.footer{margin-top:48px;border-top:1px solid var(--line);padding:24px 0 36px;font-size:13px;color:var(--muted)}.footer p{margin:4px 0}.no-script{padding:14px 18px;background:var(--warm);margin:16px 0;border-left:3px solid var(--focus)}.js-only{display:none}.js-enabled .js-only{display:flex}.js-enabled .empty.js-only:not([hidden]){display:block}.jump-flash{box-shadow:0 0 0 3px var(--focus)}
@media(min-width:1280px){.asset-grid{gap:28px}.card-body{padding-top:24px}.slide-grid{gap:24px}}
.archive-notice{margin:16px 0 0;padding:12px 14px;background:var(--warm);border-left:3px solid #ba7800;border-radius:3px;font-size:13px}.archive-notice strong{display:block;font-weight:650;margin-bottom:3px}.archive-notice p{margin:3px 0}
@media(max-width:1024px){.wrap{width:calc(100% - 40px)}.slide-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.deck-panel{grid-template-columns:minmax(0,1fr) 260px}.card-body{padding:18px 18px 0}.asset-details{margin:0 -18px;padding:0 18px}.asset-card h3{font-size:21px}.search{max-width:none}.toolbar .wrap{gap:10px}.filter-group{flex:1}}
@media(max-width:767px){.wrap{width:calc(100% - 32px)}.masthead .wrap{align-items:flex-start;gap:8px;flex-direction:column}.intro{padding-top:28px;padding-bottom:24px}.intro-text{font-size:16px}.deck-panel{grid-template-columns:1fr;gap:16px;padding:20px}.deck-preview{max-width:380px}.asset-grid{grid-template-columns:1fr;gap:20px}.slide-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.search{max-width:none;min-width:100%}.toolbar .wrap{padding-block:10px}.filter{padding:6px 9px;font-size:13px;min-height:36px}.section-heading{display:block}.section-heading p{margin-top:6px}.result-line{align-items:flex-start}.quiet-link{max-width:150px;text-align:right}.card-media{aspect-ratio:16/9}.asset-card,.slide-card{scroll-margin-top:185px}html{scroll-padding-top:190px}}
@media(max-width:400px){.slide-grid{grid-template-columns:1fr}.deck-actions{align-items:stretch;flex-direction:column}.button{width:100%}.release{font-size:11px}.card-meta{font-size:11px}.asset-details summary span{display:block;margin:4px 0 0 16px}.wrap{width:calc(100% - 24px)}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{body{background:white}.toolbar,.file-actions,.help-links,.footer,.deck-actions,video,.js-only{display:none!important}.wrap{width:100%}.asset-card,.slide-card{break-inside:avoid}.asset-grid{grid-template-columns:1fr 1fr}.card-body{padding:12px}.asset-details{margin:0;padding:0}.asset-details[open]{display:block}.deck-panel{grid-template-columns:1fr 200px}.card-media{max-height:220px}}
"""


JS = r"""
(() => {
  'use strict';
  document.documentElement.classList.add('js-enabled');
  const input = document.getElementById('asset-search');
  const filters = [...document.querySelectorAll('[data-filter]')];
  const items = [...document.querySelectorAll('.catalog-item')];
  const assetItems = [...document.querySelectorAll('.asset-card')];
  const slideItems = [...document.querySelectorAll('.slide-card')];
  const count = document.getElementById('result-count');
  let filter = 'in-ppt';

  function apply() {
    const words = input.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    items.forEach(item => {
      const kind = item.dataset.kind;
      const modeMatch = filter === 'all' ||
        (filter === 'in-ppt' && item.dataset.inPpt === 'true' && kind !== 'slide') ||
        (filter === 'animations' && kind === 'animation') ||
        (filter === 'figures' && kind === 'figure') ||
        (filter === 'slides' && kind === 'slide');
      const show = modeMatch && words.every(word => item.dataset.search.includes(word));
      item.hidden = !show;
      if (show) visible += 1;
      else item.querySelectorAll('video').forEach(video => video.pause());
    });
    filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === filter)));
    const nAssets = assetItems.filter(item => !item.hidden).length;
    const nSlides = slideItems.filter(item => !item.hidden).length;
    document.getElementById('asset-section').hidden = nAssets === 0;
    document.getElementById('slide-section').hidden = nSlides === 0;
    document.getElementById('empty-state').hidden = visible !== 0;
    const labels = [];
    if (nAssets) labels.push(`${nAssets} asset ${nAssets === 1 ? 'family' : 'families'}`);
    if (nSlides) labels.push(`${nSlides} slide ${nSlides === 1 ? 'page' : 'pages'}`);
    count.textContent = labels.length ? labels.join(' · ') : 'No matching items';
  }

  filters.forEach(button => button.addEventListener('click', () => { filter = button.dataset.filter; apply(); }));
  input.addEventListener('input', apply);
  document.getElementById('reset-search').addEventListener('click', () => {
    filter = 'all'; input.value = ''; apply(); input.focus();
  });

  function revealTarget(hash, moveFocus = true) {
    if (!hash || hash.length < 2) return false;
    let target;
    try { target = document.getElementById(decodeURIComponent(hash.slice(1))); }
    catch (_) { return false; }
    if (!target || !target.classList.contains('catalog-item')) return false;
    input.value = '';
    filter = target.dataset.kind === 'slide' ? 'slides' : 'all';
    apply();
    target.scrollIntoView({ block: 'start' });
    if (moveFocus) target.focus({ preventScroll: true });
    return true;
  }

  document.querySelectorAll('.slide-jump,.asset-jump').forEach(link => {
    link.addEventListener('click', () => revealTarget(link.hash));
  });
  document.querySelector('[data-show-slides]').addEventListener('click', () => {
    filter = 'slides'; input.value = ''; apply();
  });
  window.addEventListener('hashchange', () => revealTarget(location.hash));
  apply();
  revealTarget(location.hash, false);
})();
"""


def build(catalog: dict) -> str:
    if int(catalog.get("schema_version", 0)) != 1:
        raise ValueError("Unsupported catalog schema_version; expected 1")
    presentation = catalog["presentation"]
    slides = catalog.get("slides", [])
    assets = catalog.get("assets", [])
    assets_by_id = {asset["id"]: asset for asset in assets}
    if len(assets_by_id) != len(assets):
        raise ValueError("Asset IDs must be unique")
    dom_ids = [anchor_id(asset["id"]) for asset in assets]
    if len(set(dom_ids)) != len(dom_ids):
        raise ValueError("Asset IDs produce duplicate HTML anchors")
    preview = presentation.get("preview") or (slides[0].get("preview") if slides else None)
    deck_preview = (f'<a class="deck-preview" href="{local_url(preview)}" aria-label="Open the first slide preview">'
                    f'<img src="{local_url(preview)}" alt="First slide of the archived presentation" decoding="async"></a>') if preview else ""
    title = catalog.get("title", "Oriented powder diffraction — presentation asset library")
    release = catalog.get("release_id", "")
    doc_path = catalog.get("documentation_path", "README.md")
    checksums_path = catalog.get("checksums_path", "SHA256SUMS.txt")
    current_assets = sum(bool(asset.get("slide_uses")) for asset in assets)
    html_assets = "\n".join(asset_card(asset) for asset in assets)
    html_slides = "\n".join(slide_card(slide, assets_by_id) for slide in slides)
    deck_name = Path(presentation["path"]).name
    notices = "".join('<aside class="archive-notice">' +
                      (f'<strong>{esc(notice["title"])}</strong>' if notice.get("title") else '') +
                      prose(notice.get("text")) + '</aside>' for notice in catalog.get("notices", []))
    buttons = "".join(f'<button class="filter" type="button" data-filter="{value}" aria-pressed="false">{label}</button>' for value, label in
                      [("in-ppt", "In this deck"), ("all", "All assets"), ("animations", "Animations"), ("figures", "Figures"), ("slides", "Slide pages")])
    return f'''<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light"><meta name="description" content="Offline archive of the oriented powder diffraction presentation, figures, animations, and their source records.">
<title>{esc(title)}</title><style>{CSS}</style></head>
<body>
<a class="skip-link" href="#library">Skip to the asset library</a>
<header class="masthead"><div class="wrap"><span class="brand">Oriented powder diffraction</span><span class="release">Archive / {esc(release)}</span></div></header>
<div class="wrap intro">
  <p class="eyebrow">Presentation &amp; reusable assets</p><h1>{esc(title)}</h1>
  <p class="intro-text">The edited deck, the exact assets it uses, and the source records that explain how to use them again.</p>
  <section class="deck-panel" aria-labelledby="deck-heading"><div>
    <h2 id="deck-heading">The preserved presentation</h2>
    <p class="deck-meta">{esc(deck_name)}<br>{int(presentation.get('slide_count', len(slides)))} slides · {human_size(presentation.get('bytes'))} · {current_assets} linked asset families</p>
    <div class="deck-actions">{file_link(presentation['path'], 'Download the PowerPoint', 'button', True)}<a class="button secondary" data-show-slides href="#slide-section">Browse slide pages</a></div>
    <p class="sha">SHA-256<br>{esc(presentation.get('sha256', 'See the checksum manifest'))}</p>
    {notices}
  </div>{deck_preview}</section>
  <nav class="help-links" aria-label="Archive documents">{file_link(doc_path, 'Read the archive guide')}{file_link('catalog.json', 'Machine-readable catalog')}{file_link(checksums_path, 'File checksums')}</nav>
</div>
<div class="toolbar js-only"><div class="wrap"><div class="filter-group" role="group" aria-label="Filter library">{buttons}</div><div class="search"><label for="asset-search">Search</label><input id="asset-search" type="search" placeholder="Ewald, mosaic, Bi₂Se₃…" autocomplete="off"></div></div></div>
<main class="wrap" id="library">
  <noscript><p class="no-script">All assets and slide pages are shown below. Turn on JavaScript only if you want search and filters; viewing and downloading files works without it.</p></noscript>
  <div class="result-line"><p id="result-count" role="status" aria-live="polite">{len(assets)} asset families · {len(slides)} slide pages</p><a class="quiet-link" href="{local_url(doc_path)}">How to preserve &amp; rebuild</a></div>
  <section id="asset-section" aria-labelledby="asset-heading"><div class="section-heading"><h2 id="asset-heading">Figures &amp; animations</h2><p>Play an animation, or open a figure at full size.</p></div><div class="asset-grid">{html_assets}</div></section>
  <section id="slide-section" aria-labelledby="slide-heading"><div class="section-heading"><h2 id="slide-heading">The deck, in order</h2><p>Static previews of the archived PowerPoint.</p></div><div class="slide-grid">{html_slides}</div></section>
  <div id="empty-state" class="empty js-only" hidden><h2>No matching items</h2><p>Try a material, a physical concept, or a slide number.</p><button id="reset-search" type="button" class="button secondary">Clear search &amp; show all</button></div>
</main>
<footer class="footer"><div class="wrap"><p>This gallery runs offline. Keep it with the accompanying folders so its links continue to work.</p><p>Use the asset notes and source records to distinguish schematic illustrations, conditional fits, and measured comparisons. Regeneration requirements are documented in the archive guide.</p></div></footer>
<script>{JS}</script>
</body></html>
'''


def main() -> None:
    catalog_path = ROOT / "catalog.json"
    with catalog_path.open("r", encoding="utf-8") as handle:
        catalog = json.load(handle)
    result = build(catalog)
    destination = ROOT / "index.html"
    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(result)
    print(json.dumps({"gallery": str(destination), "assets": len(catalog.get("assets", [])), "slides": len(catalog.get("slides", [])), "bytes": destination.stat().st_size}))


if __name__ == "__main__":
    main()
