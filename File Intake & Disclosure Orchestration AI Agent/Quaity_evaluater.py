import cv2
import numpy as np
import os

# ---------- Blur Detection ----------
def detect_blur(image, lap_thresh=100, tenengrad_thresh=50):
# def detect_blur_text_sensitive(image, lap_thresh=100, tenengrad_thresh=50):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Laplacian variance
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Tenengrad with median (less sensitive to slant/tilt)
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gnorm = np.sqrt(gx**2 + gy**2)
    tenengrad_median = np.median(gnorm)

    # decision
    blur_pass = (lap_var >= lap_thresh) and (tenengrad_median >= tenengrad_thresh)

    return {
        "laplacian_score": lap_var,
        "tenengrad_median": tenengrad_median,
        "blur_pass": blur_pass
    }


# ---------- Skew Detection ----------
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
    # normalize -90 to 0 (common OpenCV quirk)
    if angle == -90:
        angle = 0.0
    return angle

# ---------- Contrast Estimation ----------
def estimate_contrast(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray.std()  # standard deviation of intensity

# ---------- Resolution Estimation ----------
def estimate_resolution(image, dpi_assumed=96):
    h, w = image.shape[:2]
    width_inch = w / dpi_assumed
    height_inch = h / dpi_assumed
    return {"width_px": w, "height_px": h,
            "width_inch": width_inch, "height_inch": height_inch}

# ---------- Full Pipeline ----------
def analyze_document_quality(image_path, blur_thresh=100, tenengrad_thresh=50, contrast_thresh=15):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not read image: check path or file format")

    blur_report = detect_blur(image, blur_thresh, tenengrad_thresh)
    skew_angle = compute_skew(image)
    contrast = estimate_contrast(image)
    resolution = estimate_resolution(image)

    report = {
        "blur_analysis": blur_report,
        "skew_angle_deg": skew_angle,
        "skew_pass": abs(skew_angle) <= 2.0,
        "contrast_score": contrast,
        "contrast_pass": contrast >= contrast_thresh,
        "resolution": resolution
    }

    return report

# ---------- Example Usage ----------
if __name__ == "__main__":
    path = input("Please enter the document path: ").strip().strip('"').strip("'")
    path = os.path.normpath(path)

    if not os.path.exists(path):
        print(f"Error: File not found at {path}")
    else:
        report = analyze_document_quality(path)
        print("Document Quality Report:")
        for k, v in report.items():
            print(f"{k}: {v}")
