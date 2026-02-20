# Plot Area Detection - Implementation Plan

## 문제점

**현재 이슈:**
- Axis labels (1990, 2000, 2010...) 감지됨
- Legend ("Actual", "Projected") 감지됨
- 그래프 영역 밖의 텍스트/요소 포함

## 해결 방안

### Plot Area (그리드 영역) 감지

```python
def detect_plot_area():
    # 1. 그리드 라인 감지 (수직/수평)
    # 2. Bounding box 계산
    # 3. 안쪽 영역만 유효 판정
```

---

## 구현 상세

### 1. Grid Line Detection

```python
def _detect_grid_boundaries():
    # Hough Line Transform으로 수직/수평 라인 찾기
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 
                            threshold=50,
                            minLineLength=width//10)
    
    # 수평선 중 가장 위/아래
    # 수직선 중 가장 왼쪽/오른쪽
    
    return {
        'x_min': left_boundary,
        'x_max': right_boundary,
        'y_min': top_boundary,
        'y_max': bottom_boundary
    }
```

### 2. Alternative: Contour-Based Detection

```python
def _detect_plot_area_by_contour():
    # 그래프 전체를 감싸는 사각형 찾기
    # 배경과 그래프 영역 구분
    
    # Binary threshold
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # Find largest rectangle
    contours = cv2.findContours(binary, ...)
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    
    return {'x_min': x, 'x_max': x+w, 'y_min': y, 'y_max': y+h}
```

### 3. Calibration-Based (가장 정확!) ⭐⭐⭐

사용자가 이미 **calibration**을 하고 있습니다!
```python
# 사용자가 4개 포인트 클릭:
# (x1, y1) - X축 시작
# (x2, y2) - X축 끝
# (y1_x, y1_y) - Y축 시작
# (y2_x, y2_y) - Y축 끝

# Plot area는 이 4개 점이 만드는 영역!
plot_area = {
    'x_min': min(x1, x2, y1_x, y2_x),
    'x_max': max(x1, x2, y1_x, y2_x),
    'y_min': min(y1, y2, y1_y, y2_y),
    'y_max': max(y1, y2, y1_y, y2_y)
}
```

### 4. Point Filtering

```python
def _filter_points_in_plot_area(points, plot_area):
    valid_points = []
    for (x, y) in points:
        if (plot_area['x_min'] <= x <= plot_area['x_max'] and
            plot_area['y_min'] <= y <= plot_area['y_max']):
            valid_points.append((x, y))
    return valid_points
```

---

## 추천 방식

**Option 3: Calibration-Based** ⭐

**장점:**
- 사용자가 이미 calibration 수행
- 100% 정확한 plot area
- 추가 감지 로직 불필요
- 간단하고 robust

**구현:**
1. Backend에서 calibration 데이터 저장
2. Detection 시 calibration points에서 plot area 계산
3. 모든 detected points를 plot area로 필터링

---

## 예상 효과

**Before:**
- ❌ "1990", "2000" 등 axis labels 감지
- ❌ "Actual", "Projected" legend 감지
- ❌ Title 텍스트 감지

**After:**
- ✅ Plot area 내부만 유효
- ✅ Axis labels 자동 제외
- ✅ Legend 자동 제외
- ✅ 깔끔한 그래프 데이터만

---

## 구현 순서

1. [ ] Backend에서 calibration data 전달받기
2. [ ] `_calculate_plot_area_from_calibration()` 구현
3. [ ] `_filter_points_in_plot_area()` 구현
4. [ ] 모든 extraction methods에 적용
