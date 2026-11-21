// Shrink a photo to the detector's 256x256 input in the browser, producing
// exactly the pixels the server would compute from the full-size upload, and
// send that as a lossless PNG (~150 KB instead of several MB).
//
// Why this is accuracy-neutral: the server runs
//   Image.open(f).convert("RGB").resize((256, 256), BICUBIC)
// and Pillow returns an unchanged copy when the image is already 256x256. So as
// long as (1) the browser decodes the JPEG/PNG to the same pixels as Pillow and
// (2) we resize with Pillow's exact algorithm (pilResize.js), the model sees
// the same input. (1) is not guaranteed by every browser (colour management,
// EXIF rotation, decoder differences), so before using the fast path we decode
// a built-in probe JPEG (Adobe RGB profile + EXIF rotation + 4:2:0 chroma) and
// require its pixels to match Pillow's byte for byte. Anything unusual, or any
// failure, falls back to uploading the original file.

import { pilBicubicResize } from './pilResize.js';

const SIZE = 256;
const MIN_BYTES = 300 * 1024; // smaller files upload quickly anyway
const MAX_PIXELS = 40e6; // stay clear of browser canvas limits

const PROBE_JPEG_B64 = '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';
// SHA-256 of Pillow's decoded RGB pixels for the probe (stored orientation, no
// colour conversion), from Pillow 13 / libjpeg-turbo.
const PROBE_SHA256 = '587d252f700966e5a4c0aee6f43b07038acda8e1953ee9034995a786ea5b28c8';

const BITMAP_OPTS = {
  imageOrientation: 'from-image',
  colorSpaceConversion: 'none',
  premultiplyAlpha: 'none',
};

// ----------------------------------------------------------------- file sniffing
function u16(b, o, le) { return le ? b[o] | (b[o + 1] << 8) : (b[o] << 8) | b[o + 1]; }
function u32(b, o, le) {
  return le
    ? (b[o] | (b[o + 1] << 8) | (b[o + 2] << 16)) + b[o + 3] * 0x1000000
    : b[o] * 0x1000000 + ((b[o + 1] << 16) | (b[o + 2] << 8) | b[o + 3]);
}

function exifOrientation(b, start, end) {
  // start points at "Exif\0\0"
  const t = start + 6;
  if (t + 8 > end) return 1;
  const le = b[t] === 0x49;
  const ifd = t + u32(b, t + 4, le);
  if (ifd + 2 > end) return 1;
  const n = u16(b, ifd, le);
  for (let i = 0; i < n; i++) {
    const e = ifd + 2 + i * 12;
    if (e + 12 > end) break;
    if (u16(b, e, le) === 0x0112) return u16(b, e + 8, le) || 1;
  }
  return 1;
}

/** Parse JPEG markers: component count, size, EXIF orientation, Adobe transform. */
function inspectJpeg(b) {
  const info = { components: 0, width: 0, height: 0, orientation: 1, adobe: false };
  let o = 2;
  while (o + 4 <= b.length) {
    if (b[o] !== 0xff) return null;
    const m = b[o + 1];
    if (m === 0xd8 || (m >= 0xd0 && m <= 0xd7) || m === 0x01 || m === 0xff) { o += m === 0xff ? 1 : 2; continue; }
    const len = u16(b, o + 2, false);
    const seg = o + 4;
    if (m === 0xe1 && b[seg] === 0x45 && b[seg + 1] === 0x78 && b[seg + 2] === 0x69 && b[seg + 3] === 0x66) {
      info.orientation = exifOrientation(b, seg, Math.min(b.length, o + 2 + len));
    } else if (m === 0xee && b[seg] === 0x41 && b[seg + 1] === 0x64) {
      info.adobe = true; // Adobe APP14 (CMYK/YCCK and other transforms)
    } else if (m >= 0xc0 && m <= 0xcf && m !== 0xc4 && m !== 0xc8 && m !== 0xcc) {
      if (b[seg] !== 8) return null; // 12-bit JPEG
      info.height = u16(b, seg + 1, false);
      info.width = u16(b, seg + 3, false);
      info.components = b[seg + 5];
      return info;
    }
    o += 2 + len;
  }
  return null;
}

/** PNG: only 8-bit, non-animated, no gamma/colour chunks (browsers may apply them). */
function pngIsPlain(b) {
  if (b[24] !== 8) return false; // bit depth
  let o = 8;
  while (o + 8 <= b.length) {
    const len = u32(b, o, false);
    const type = String.fromCharCode(b[o + 4], b[o + 5], b[o + 6], b[o + 7]);
    if (type === 'IDAT' || type === 'IEND') return true;
    if (['gAMA', 'cHRM', 'iCCP', 'acTL', 'eXIf'].includes(type)) return false;
    o += 12 + len;
  }
  return false;
}

// ------------------------------------------------------------ pixel utilities
function newCanvas(w, h) {
  if (typeof OffscreenCanvas !== 'undefined') return new OffscreenCanvas(w, h);
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  return c;
}

async function decode(blob) {
  const bmp = await createImageBitmap(blob, BITMAP_OPTS);
  try {
    const c = newCanvas(bmp.width, bmp.height);
    const ctx = c.getContext('2d', { willReadFrequently: true, colorSpace: 'srgb' });
    ctx.drawImage(bmp, 0, 0);
    return { data: ctx.getImageData(0, 0, bmp.width, bmp.height).data, width: bmp.width, height: bmp.height };
  } finally {
    bmp.close && bmp.close();
  }
}

/**
 * The browser shows EXIF-rotated pixels; Pillow (and so the model) sees them as
 * stored. Map the decoded image back to stored orientation.
 */
function unorient(img, orientation, storedW, storedH) {
  if (orientation === 1) return img;
  const W = storedW, H = storedH;
  const dw = orientation >= 5 ? H : W;
  const src = img.data;
  const out = new Uint8ClampedArray(W * H * 4);
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      let dx, dy;
      switch (orientation) {
        case 2: dx = W - 1 - x; dy = y; break;
        case 3: dx = W - 1 - x; dy = H - 1 - y; break;
        case 4: dx = x; dy = H - 1 - y; break;
        case 5: dx = y; dy = x; break;
        case 6: dx = H - 1 - y; dy = x; break;
        case 7: dx = H - 1 - y; dy = W - 1 - x; break;
        default: dx = y; dy = W - 1 - x; break; // 8
      }
      const s = (dy * dw + dx) * 4, d = (y * W + x) * 4;
      out[d] = src[s]; out[d + 1] = src[s + 1]; out[d + 2] = src[s + 2]; out[d + 3] = src[s + 3];
    }
  }
  return { data: out, width: W, height: H };
}

/** Decode and return pixels in stored orientation, or null if not reliable. */
async function decodeStored(blob, orientation, storedW, storedH) {
  const img = await decode(blob);
  if (img.width === storedW && img.height === storedH) {
    // Browser did not rotate. Fine for 1, ambiguous for 2-4 (mirror/180 keep size).
    if (orientation === 1) return img;
    if (orientation >= 5) return null; // rotation expected but not applied: unknown behaviour
  } else if (!(img.width === storedH && img.height === storedW && orientation >= 5)) {
    return null;
  }
  return unorient(img, orientation, storedW, storedH);
}

async function sha256Rgb(rgba) {
  const rgb = new Uint8Array((rgba.length / 4) * 3);
  for (let i = 0, j = 0; i < rgba.length; i += 4, j += 3) {
    rgb[j] = rgba[i]; rgb[j + 1] = rgba[i + 1]; rgb[j + 2] = rgba[i + 2];
  }
  const h = new Uint8Array(await crypto.subtle.digest('SHA-256', rgb));
  return Array.from(h, (x) => x.toString(16).padStart(2, '0')).join('');
}

let probeResult = null;
/** True if this browser decodes JPEGs exactly like Pillow (checked once). */
export function browserDecodesLikePillow() {
  if (!probeResult) {
    probeResult = (async () => {
      try {
        if (typeof createImageBitmap !== 'function' || !crypto?.subtle) return false;
        const bytes = Uint8Array.from(atob(PROBE_JPEG_B64), (c) => c.charCodeAt(0));
        const info = inspectJpeg(bytes);
        const img = await decodeStored(new Blob([bytes], { type: 'image/jpeg' }), info.orientation, info.width, info.height);
        return !!img && (await sha256Rgb(img.data)) === PROBE_SHA256;
      } catch {
        return false;
      }
    })();
  }
  return probeResult;
}

/**
 * Returns the file to upload for /api/check-image: a 256x256 PNG with the exact
 * pixels the server would use, or the original file whenever that cannot be
 * guaranteed.
 */
export async function prepareDetectorUpload(file, { minBytes = MIN_BYTES } = {}) {
  try {
    if (!file || file.size < minBytes) return file;
    const head = new Uint8Array(await file.slice(0, 256 * 1024).arrayBuffer());
    let orientation = 1, w, h;
    if (head[0] === 0xff && head[1] === 0xd8) {
      const info = inspectJpeg(head);
      if (!info || info.adobe || (info.components !== 3 && info.components !== 1)) return file;
      ({ orientation, width: w, height: h } = info);
      if (orientation < 1 || orientation > 8) return file;
    } else if (head[0] === 0x89 && head[1] === 0x50 && head[2] === 0x4e && head[3] === 0x47) {
      if (!pngIsPlain(head)) return file;
      w = u32(head, 16, false);
      h = u32(head, 20, false);
    } else {
      return file; // WebP, HEIC, GIF, ...: let the server decode the original
    }
    if (w < SIZE || h < SIZE || w * h > MAX_PIXELS) return file;
    if (!(await browserDecodesLikePillow())) return file;

    const img = await decodeStored(file, orientation, w, h);
    if (!img) return file;
    const px = img.data;
    for (let i = 3; i < px.length; i += 4) {
      if (px[i] !== 255) return file; // transparency: browser and Pillow differ
    }

    const small = pilBicubicResize(px, img.width, img.height, SIZE, SIZE);
    const c = newCanvas(SIZE, SIZE);
    c.getContext('2d', { colorSpace: 'srgb' }).putImageData(new ImageData(small, SIZE, SIZE), 0, 0);
    const blob = c.convertToBlob
      ? await c.convertToBlob({ type: 'image/png' })
      : await new Promise((r) => c.toBlob(r, 'image/png'));
    if (!blob || blob.size >= file.size) return file;
    return new File([blob], 'detector-input.png', { type: 'image/png' });
  } catch (e) {
    console.warn('Falling back to full-size upload:', e);
    return file;
  }
}
