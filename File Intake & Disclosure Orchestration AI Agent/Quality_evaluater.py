import cv2
import numpy as np
import os
from pdf2image import convert_from_path # type: ignore

# Quality Evaluation
# Check if enough text is present (text_coverage_ratio >= 0.05, else reject for OCR)
# Check if text is sharp enough (use text-sensitive blur, fail if blur_pass == False)
# Check if document skew is acceptable (abs(skew_angle) <= 2°, else reject or correct)
# Check if contrast is sufficient (contrast_score >= 15, else reject as faded text)
# Check if exposure is valid (not under_exposed and not over_exposed, else reject)
# Check if resolution is OCR-ready (dpi >= 150–200, else reject as low-res)
# Check if document is cropped properly (border_artifacts == False, else reject)


def detect_blur_text_sensitive(image, lap_thresh=100, tenengrad_thresh=50):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Binarize to isolate text
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text_mask = (bw == 0).astype(np.uint8)  # black pixels = text

    # Morphology to clean small noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    text_mask = cv2.morphologyEx(text_mask, cv2.MORPH_OPEN, kernel, iterations=1)

    #Apply mask (keep only text pixels)
    gray_text = cv2.bitwise_and(gray, gray, mask=text_mask)

    #Blur measures (on text only)
    lap_var = float(cv2.Laplacian(gray_text, cv2.CV_64F).var())

    gx = cv2.Sobel(gray_text, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray_text, cv2.CV_64F, 0, 1, ksize=3)
    gnorm = np.sqrt(gx**2 + gy**2)
    tenengrad_median = float(np.median(gnorm[text_mask > 0]) if np.any(text_mask > 0) else 0)

    #Decision
    blur_pass = bool((lap_var >= lap_thresh) and (tenengrad_median >= tenengrad_thresh))

    return {
        "laplacian_score_text": lap_var,
        "tenengrad_median_text": tenengrad_median,
        "blur_pass": blur_pass
    }

def compute_skew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    if angle == -90:
        angle = 0.0
    return float(angle)

def estimate_contrast(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return float(gray.std())

def estimate_resolution(image, dpi_assumed=96):
    h, w = image.shape[:2]
    return {
        "width_px": w,
        "height_px": h,
        "width_inch": w / dpi_assumed,
        "height_inch": h / dpi_assumed
    }

def estimate_brightness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_intensity = float(np.mean(gray))
    return {"mean_brightness": mean_intensity,
            "under_exposed": bool(mean_intensity < 50),
            "over_exposed": bool(mean_intensity > 200)}

def estimate_noise(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    noise_level = float(lap.var())
    return {"noise_score": noise_level,
            "noisy": bool(noise_level > 500)}

def estimate_text_coverage(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text_pixels = np.sum(bw == 0)
    total_pixels = bw.size
    ratio = float(text_pixels / total_pixels)
    return {"text_coverage_ratio": ratio,
            "too_little_text": bool(ratio < 0.05)}

def check_color(image):
    if len(image.shape) < 3 or image.shape[2] == 1:
        return {"is_color": False}
    b, g, r = cv2.split(image)
    if np.array_equal(b, g) and np.array_equal(b, r):
        return {"is_color": False}
    return {"is_color": True}

def detect_borders(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    white_ratio = np.mean(bw == 255)
    return {"border_artifacts": bool(white_ratio < 0.9)}

def analyze_document_quality_file(file_path, dpi=200):
    ext = os.path.splitext(file_path)[-1].lower()

    if ext in [".jpg", ".jpeg",'.webp', ".png", ".tif", ".tiff", ".bmp"]:
        image = cv2.imread(file_path)
        return {"file": file_path, "pages": [analyze_document_quality_image(image)]}

    elif ext == ".pdf":
        pages = convert_from_path(file_path, dpi=dpi)
        results = []
        for i, page in enumerate(pages):
            image = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
            result = analyze_document_quality_image(image)
            results.append({"page": i+1, "report": result})
        return {"file": file_path, "pages": results}

    else:
        raise ValueError(f"Unsupported file type: {ext}")

def analyze_document_quality_image(image, blur_thresh=100, tenengrad_thresh=50, contrast_thresh=15):
    blur_report_with_text = detect_blur_text_sensitive(image, lap_thresh=blur_thresh, tenengrad_thresh=tenengrad_thresh)
    skew_angle = compute_skew(image)
    contrast = estimate_contrast(image)
    resolution = estimate_resolution(image)
    brightness = estimate_brightness(image)
    noise = estimate_noise(image)
    text_coverage = estimate_text_coverage(image)
    color_info = check_color(image)
    borders = detect_borders(image)

    report = {
        "blur_report_with_text": blur_report_with_text,
        "skew_angle_deg": skew_angle,
        "skew_pass": abs(skew_angle) <= 2.0,
        "contrast_score": contrast,
        "contrast_pass": contrast >= contrast_thresh,
        "resolution": resolution,
        "brightness": brightness,
        "noise": noise,
        "text_coverage": text_coverage,
        "color_info": color_info,
        "border_check": borders
    }
    return report

if __name__ == "__main__":
    path = input("Please enter the document path: ").strip().strip('"').strip("'")
    path = os.path.normpath(path)

    if not os.path.exists(path):
        print(f"Error: File not found at {path}")
    else:
        report = analyze_document_quality_file(path)
        print("Document Quality Report:")
        print(report)