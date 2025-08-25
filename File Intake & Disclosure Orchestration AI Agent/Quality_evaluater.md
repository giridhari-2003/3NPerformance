# Document Quality Evaluation Functions

This module provides utilities to evaluate the quality of scanned or digital documents for OCR readiness.  
The checks include blur detection, skew correction, contrast, brightness, resolution, noise, text coverage, and border detection.

---

## `detect_blur_text_sensitive(image, lap_thresh=100, tenengrad_thresh=50)`

**Description:**  
Detects blur in text regions of the image using Laplacian variance and Tenengrad gradient-based sharpness metrics.

**Parameters:**
- `image` (np.ndarray): Input image in BGR format.
- `lap_thresh` (int, default=100): Threshold for Laplacian variance.
- `tenengrad_thresh` (int, default=50): Threshold for Tenengrad sharpness.

**Returns:**  
`dict` with:
- `"laplacian_score_text"` (float): Variance of Laplacian (sharpness measure).
- `"tenengrad_median_text"` (float): Median Tenengrad value over text pixels.
- `"blur_pass"` (bool): `True` if text is sharp enough.

---

## `compute_skew(image)`

**Description:**  
Estimates the skew angle of the document based on text alignment.

**Parameters:**
- `image` (np.ndarray): Input image in BGR format.

**Returns:**  
- `float`: Estimated skew angle in degrees.  
  Positive = counterclockwise, Negative = clockwise.

---

## `estimate_contrast(image)`

**Description:**  
Computes the contrast of the document using grayscale pixel standard deviation.

**Parameters:**
- `image` (np.ndarray): Input image in BGR format.

**Returns:**  
- `float`: Contrast score (higher = better contrast).

---

## `estimate_resolution(image, dpi_assumed=96)`

**Description:**  
Estimates resolution and physical size of the document image.

**Parameters:**
- `image` (np.ndarray): Input image in BGR format.
- `dpi_assumed` (int, default=96): Assumed DPI of the image.

**Returns:**  
`dict` with:
- `"width_px"` (int): Width in pixels.
- `"height_px"` (int): Height in pixels.
- `"width_inch"` (float): Width in inches.
- `"height_inch"` (float): Height in inches.

---

## `estimate_brightness(image)`

**Description:**  
Estimates mean brightness and checks for under/over-exposure.

**Parameters:**
- `image` (np.ndarray): Input image in BGR format.

**Returns:**  
`dict` with:
- `"mean_brightness"` (float): Average grayscale value.
- `"under_exposed"` (bool): `True` if mean < 50.
- `"over_exposed"` (bool): `True` if mean > 200.

---

## `estimate_noise(image)`

**Description:**  
Estimates noise level in the document using Laplacian variance.

**Parameters:**
- `image` (np.ndarray): Input image in BGR format.

**Returns:**  
`dict` with:
- `"noise_score"` (float): Variance of Laplacian (noise measure).
- `"noisy"` (bool): `True` if noise level > 500.

---

## `estimate_text_coverage(image)`

**Description:**  
Estimates how much of the image contains text (black pixel coverage).

**Parameters:**
- `image` (np.ndarray): Input image in BGR format.

**Returns:**  
`dict` with:
- `"text_coverage_ratio"` (float): Ratio of text pixels to total pixels.
- `"too_little_text"` (bool): `True` if coverage < 0.05.

---

## `check_color(image)`

**Description:**  
Determines if the image is color or grayscale.

**Parameters:**
- `image` (np.ndarray): Input image in BGR format.

**Returns:**  
`dict` with:
- `"is_color"` (bool): `True` if color image, `False` if grayscale.

---

## `detect_borders(image)`

**Description:**  
Detects border artifacts (extra white/black margins) in the document.

**Parameters:**
- `image` (np.ndarray): Input image in BGR format.

**Returns:**  
`dict` with:
- `"border_artifacts"` (bool): `True` if white space < 90%.

---

## `analyze_document_quality_image(image, blur_thresh=100, tenengrad_thresh=50, contrast_thresh=15)`

**Description:**  
Runs all quality checks on a single document image.

**Parameters:**
- `image` (np.ndarray): Input image in BGR format.
- `blur_thresh` (int, default=100): Blur threshold.
- `tenengrad_thresh` (int, default=50): Tenengrad threshold.
- `contrast_thresh` (int, default=15): Minimum acceptable contrast.

**Returns:**  
`dict` with reports from all quality checks.

---

## `analyze_document_quality_file(file_path, dpi=200)`

**Description:**  
Processes a file (image or PDF) and evaluates quality for OCR readiness.

**Parameters:**
- `file_path` (str): Path to image or PDF file.
- `dpi` (int, default=200): Resolution to render PDF pages.

**Returns:**  
`dict` with:
- `"file"` (str): File path.
- `"pages"` (list): Quality reports per page/image.

---

