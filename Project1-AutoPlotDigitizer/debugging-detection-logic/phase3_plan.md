# Implementation Plan - Complete Automation (Phase 3)

## Goal
완전 자동화된 Plot Digitizer:
1. **OCR 축 라벨 읽기**: Tesseract로 축 눈금 자동 인식
2. **다중 시리즈 감지**: 색상/스타일별로 여러 그래프 자동 분리
3. **원클릭 워크플로우**: 이미지만 넣으면 모든 것 자동 처리

## User Review Required

> [!IMPORTANT]
> **Tesseract OCR 설치 필요**:
> ```bash
> # Mac
> brew install tesseract
> 
> # Python package
> pip install pytesseract easyocr
> ```
> 
> **대안**: EasyOCR (더 정확하지만 느림) 또는 Tesseract (빠르지만 덜 정확)
> 
> 어떤 것을 선호하시나요? 또는 둘 다 구현하고 사용자가 선택하게 할까요?

> [!WARNING]
> **OCR 정확도 한계**:
> - 손글씨나 특이한 폰트는 인식 실패 가능
> - 작은 글씨나 회전된 텍스트는 어려움
> - 과학적 표기법 (1e-5 등) 파싱 복잡
> 
> **해결책**: OCR 실패 시 사용자에게 수동 입력 요청

## Proposed Changes

### 1. OCR Module

#### [NEW] [ocr_reader.py](file:///Users/dm_chamber/.gemini/antigravity/scratch/AutoPlotDigitizerPython/core/ocr_reader.py)
- **Text Region Detection**: 축 주변 영역에서 텍스트 찾기
- **Number Extraction**: 정규식으로 숫자 추출 (정수, 소수, 과학적 표기법)
- **Position Mapping**: 텍스트 위치 → 픽셀 좌표 매핑
- **Axis Range Inference**: 최소/최대 값으로 축 범위 추정

### 2. Multi-Series Detection

#### [MODIFY] [auto_detector.py](file:///Users/dm_chamber/.gemini/antigravity/scratch/AutoPlotDigitizerPython/core/auto_detector.py)
- **Color Clustering**: K-means로 주요 색상 분리
- **Line Style Detection**: 
  - Solid lines: 연속된 픽셀
  - Dashed lines: 간격 패턴 감지
- **Series Separation**: 각 색상/스타일별로 별도 contour 추출
- **Labeling**: 자동으로 "Series 1", "Series 2" 등 라벨링

### 3. Full Auto Workflow

#### [MODIFY] [main_window.py](file:///Users/dm_chamber/.gemini/antigravity/scratch/AutoPlotDigitizerPython/gui/main_window.py)
- "Full Auto" 버튼 추가
- 워크플로우:
  1. 축 감지
  2. OCR로 축 라벨 읽기
  3. 자동 캘리브레이션
  4. 다중 시리즈 감지
  5. 모든 데이터 추출
  6. 자동 CSV 저장 (또는 미리보기)

## Technical Approach

### Phase 3.1: OCR Integration
```python
# Tesseract 사용 예시
import pytesseract
from PIL import Image

# 축 영역 crop
axis_region = image[y1:y2, x1:x2]

# OCR 실행
text = pytesseract.image_to_string(axis_region, config='--psm 6')

# 숫자 추출
import re
numbers = re.findall(r'-?\d+\.?\d*(?:[eE][+-]?\d+)?', text)
```

### Phase 3.2: Multi-Series Detection
```python
# 색상 기반 분리
from sklearn.cluster import KMeans

# 주요 색상 찾기 (배경 제외)
colors = image.reshape(-1, 3)
kmeans = KMeans(n_clusters=5)
kmeans.fit(colors)

# 각 색상별로 마스크 생성
for color in kmeans.cluster_centers_:
    mask = cv2.inRange(image, color-threshold, color+threshold)
    contours = cv2.findContours(mask, ...)
```

### Phase 3.3: Dash Line Detection
```python
# 선의 연속성 분석
def is_dashed(contour):
    # 픽셀 간 간격 측정
    gaps = []
    for i in range(len(contour)-1):
        dist = distance(contour[i], contour[i+1])
        if dist > threshold:
            gaps.append(dist)
    
    # 규칙적인 간격 = dashed
    return has_regular_pattern(gaps)
```

## Dependencies
```
pytesseract      # Tesseract wrapper
easyocr          # Alternative OCR (optional)
scikit-learn     # K-means clustering
Pillow           # Image processing
```

## Verification Plan

### Test Cases
1. **Simple Graph**: 단일 solid line, 명확한 축 라벨
2. **Multiple Series**: 3개 색상, solid lines
3. **Dashed Lines**: solid + dashed 혼합
4. **Complex Labels**: 과학적 표기법, 작은 글씨
5. **Noisy Background**: 복잡한 배경, 격자선

### Success Criteria
- OCR 축 라벨 인식률 > 80%
- 다중 시리즈 분리 정확도 > 90%
- 완전 자동 모드 성공률 > 70% (실패 시 수동 모드로 전환)

## Implementation Order
1. **먼저**: Multi-series detection (OCR 없이도 유용)
2. **나중**: OCR integration (설치 필요, 복잡도 높음)
3. **마지막**: Full auto workflow (모든 기능 통합)
