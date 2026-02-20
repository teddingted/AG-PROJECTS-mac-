# Implementation Plan - Auto-Detection Features

## Goal
자동으로 그래프 이미지에서:
1. **축 감지 및 캘리브레이션**: X축, Y축 위치와 눈금 값 자동 인식
2. **데이터 추출**: 그래프 선을 따라 데이터 포인트 자동 추출

## User Review Required

> [!IMPORTANT]
> **OCR 라이브러리 선택**: Tesseract OCR을 사용할 예정입니다. 설치가 필요합니다:
> - Mac: `brew install tesseract`
> - Windows: [Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki) 다운로드
> 
> **대안**: OCR 없이 사용자가 축 범위만 입력하고 축 위치는 자동 감지하는 방식도 가능합니다.

> [!WARNING]
> **정확도 제한**: 자동 감지는 100% 정확하지 않을 수 있습니다. 특히:
> - 복잡한 배경이 있는 그래프
> - 여러 선이 겹치는 경우
> - 손글씨나 특이한 폰트
> 
> 따라서 **수동 보정 기능**을 반드시 유지합니다.

## Proposed Changes

### 1. Auto Axis Detection (OpenCV)

#### [NEW] [auto_detector.py](file:///Users/dm_chamber/.gemini/antigravity/scratch/AutoPlotDigitizerPython/core/auto_detector.py)
- **Hough Line Transform**: 직선 감지로 축 찾기
- **Edge Detection**: Canny edge detector로 경계선 추출
- **Axis Identification**: 가장 긴 수평선(X축), 수직선(Y축) 찾기

### 2. OCR Integration (Tesseract)

#### [NEW] [ocr_reader.py](file:///Users/dm_chamber/.gemini/antigravity/scratch/AutoPlotDigitizerPython/core/ocr_reader.py)
- **Text Detection**: 축 주변 텍스트 영역 찾기
- **Number Extraction**: 숫자만 추출하여 축 범위 파악
- **Position Mapping**: 텍스트 위치와 픽셀 좌표 매핑

### 3. Auto Curve Tracing

#### [MODIFY] [auto_detector.py](file:///Users/dm_chamber/.gemini/antigravity/scratch/AutoPlotDigitizerPython/core/auto_detector.py)
- **Color Segmentation**: 그래프 선 색상 분리
- **Skeleton Extraction**: 선을 1픽셀 두께로 변환
- **Point Sampling**: 일정 간격으로 데이터 포인트 추출

### 4. UI Updates

#### [MODIFY] [main_window.py](file:///Users/dm_chamber/.gemini/antigravity/scratch/AutoPlotDigitizerPython/gui/main_window.py)
- "Auto Detect" 버튼 추가
- 감지 결과 미리보기 표시
- 수동 보정 인터페이스 유지

## Technical Approach

### Phase 1: Axis Detection (No OCR)
먼저 OCR 없이 구현:
1. 사용자가 축 범위 값만 입력 (예: X: 0~10, Y: 0~100)
2. OpenCV로 축 위치 자동 감지
3. 입력한 값과 감지된 위치를 매핑

### Phase 2: OCR Integration (Optional)
나중에 OCR 추가:
1. Tesseract로 축 라벨 읽기
2. 완전 자동 캘리브레이션

### Phase 3: Auto Curve Tracing
1. 색상 기반 선 감지
2. 자동 데이터 포인트 추출

## Dependencies
```
pytesseract  # OCR (Phase 2)
Pillow       # Image processing
scikit-image # Advanced image processing (optional)
```

## Verification Plan

### Test Cases
1. **Simple Line Graph**: 단순한 선 그래프로 테스트
2. **Multiple Series**: 여러 선이 있는 그래프
3. **Noisy Background**: 배경이 복잡한 그래프
4. **Different Styles**: 다양한 스타일의 그래프

### Success Criteria
- 축 감지 정확도 > 90%
- 데이터 추출 오차 < 5%
- 실패 시 수동 모드로 전환 가능
