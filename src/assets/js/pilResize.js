// Bit-exact port of Pillow's BICUBIC resize (src/libImaging/Resample.c, 8-bit
// path) so the browser can shrink a photo to the detector's 256x256 input and
// produce exactly the pixels the server would compute from the full file.
// Two passes (horizontal, then vertical), 22-bit fixed-point coefficients,
// rounding and clipping to uint8 between passes, just like Pillow.

const PRECISION_BITS = 32 - 8 - 2;
const ONE = 2 ** PRECISION_BITS;
const HALF = 2 ** (PRECISION_BITS - 1);
const MAX = 2 ** (PRECISION_BITS + 8);

function bicubic(x) {
  const a = -0.5;
  if (x < 0.0) x = -x;
  if (x < 1.0) return ((a + 2.0) * x - (a + 3.0)) * x * x + 1;
  if (x < 2.0) return (((x - 5) * x + 8) * x - 4) * a;
  return 0.0;
}

function precomputeCoeffs(inSize, outSize) {
  const scale = inSize / outSize;
  const filterscale = scale < 1.0 ? 1.0 : scale;
  const support = 2.0 * filterscale;
  const ksize = Math.ceil(support) * 2 + 1;
  const kk = new Int32Array(outSize * ksize);
  const bounds = new Int32Array(outSize * 2);
  const w = new Float64Array(ksize);
  for (let xx = 0; xx < outSize; xx++) {
    const center = (xx + 0.5) * scale;
    const ss = 1.0 / filterscale;
    let xmin = Math.trunc(center - support + 0.5);
    if (xmin < 0) xmin = 0;
    let xmax = Math.trunc(center + support + 0.5);
    if (xmax > inSize) xmax = inSize;
    xmax -= xmin;
    let ww = 0.0;
    for (let x = 0; x < xmax; x++) {
      w[x] = bicubic((x + xmin - center + 0.5) * ss);
      ww += w[x];
    }
    for (let x = 0; x < xmax; x++) {
      const k = ww !== 0.0 ? w[x] / ww : w[x];
      // normalize_coeffs_8bpc: round half away from zero, then C int truncation
      kk[xx * ksize + x] = k < 0 ? Math.trunc(-0.5 + k * ONE) : Math.trunc(0.5 + k * ONE);
    }
    bounds[xx * 2] = xmin;
    bounds[xx * 2 + 1] = xmax;
  }
  return { ksize, kk, bounds };
}

function clip8(v) {
  if (v >= MAX) return 255;
  if (v <= 0) return 0;
  return Math.floor(v / ONE); // == v >> 22 for the positive range here
}

/**
 * Resize interleaved RGBA pixels (alpha ignored) with Pillow's BICUBIC filter.
 * Returns a new RGBA Uint8ClampedArray of outW x outH with alpha = 255.
 */
export function pilBicubicResize(src, inW, inH, outW, outH) {
  const H = precomputeCoeffs(inW, outW);
  const V = precomputeCoeffs(inH, outH);

  // Only the source rows the vertical pass reads (Pillow's ybox crop).
  const yFirst = V.bounds[0];
  const yLast = V.bounds[outH * 2 - 2] + V.bounds[outH * 2 - 1];
  const rows = yLast - yFirst;

  let tmp, tmpW;
  if (inW !== outW) {
    tmpW = outW;
    tmp = new Uint8Array(outW * rows * 3);
    for (let y = 0; y < rows; y++) {
      const rowOff = (y + yFirst) * inW * 4;
      for (let xx = 0; xx < outW; xx++) {
        const xmin = H.bounds[xx * 2];
        const xmax = H.bounds[xx * 2 + 1];
        const kOff = xx * H.ksize;
        let s0 = HALF, s1 = HALF, s2 = HALF;
        for (let x = 0; x < xmax; x++) {
          const k = H.kk[kOff + x];
          const p = rowOff + (x + xmin) * 4;
          s0 += src[p] * k;
          s1 += src[p + 1] * k;
          s2 += src[p + 2] * k;
        }
        const o = (y * outW + xx) * 3;
        tmp[o] = clip8(s0);
        tmp[o + 1] = clip8(s1);
        tmp[o + 2] = clip8(s2);
      }
    }
  } else {
    tmpW = inW;
    tmp = new Uint8Array(inW * rows * 3);
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < inW; x++) {
        const p = ((y + yFirst) * inW + x) * 4;
        const o = (y * inW + x) * 3;
        tmp[o] = src[p];
        tmp[o + 1] = src[p + 1];
        tmp[o + 2] = src[p + 2];
      }
    }
  }

  const out = new Uint8ClampedArray(outW * outH * 4);
  for (let yy = 0; yy < outH; yy++) {
    const kOff = yy * V.ksize;
    const ymin = V.bounds[yy * 2] - yFirst;
    const ymax = V.bounds[yy * 2 + 1];
    for (let xx = 0; xx < tmpW; xx++) {
      let s0 = HALF, s1 = HALF, s2 = HALF;
      if (inH !== outH) {
        for (let y = 0; y < ymax; y++) {
          const k = V.kk[kOff + y];
          const p = ((y + ymin) * tmpW + xx) * 3;
          s0 += tmp[p] * k;
          s1 += tmp[p + 1] * k;
          s2 += tmp[p + 2] * k;
        }
      }
      const o = (yy * outW + xx) * 4;
      if (inH !== outH) {
        out[o] = clip8(s0);
        out[o + 1] = clip8(s1);
        out[o + 2] = clip8(s2);
      } else {
        const p = (yy * tmpW + xx) * 3;
        out[o] = tmp[p];
        out[o + 1] = tmp[p + 1];
        out[o + 2] = tmp[p + 2];
      }
      out[o + 3] = 255;
    }
  }
  return out;
}
