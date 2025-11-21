# راهنمای پیاده‌سازی Explainable AI (XAI)

## برای ثبت اختراع - سیستم توضیح‌پذیری پیشرفته

**نسخه**: 1.0  
**تاریخ**: 2024-12-XX

---

## 📋 فهرست مطالب

1. [مقدمه](#مقدمه)
2. [روش‌های پیاده‌سازی شده](#روشهای-پیادهسازی-شده)
3. [استفاده از XAI](#استفاده-از-xai)
4. [API Endpoints](#api-endpoints)
5. [مستندات فنی](#مستندات-فنی)

---

## مقدمه

سیستم NeuroPredict-AI از **روش‌های پیشرفته Explainable AI** استفاده می‌کند تا:

1. **توضیح دهد** که چرا مدل یک پیش‌بینی خاص را انجام داده است
2. **شناسایی کند** که کدام ویژگی‌ها بیشترین تأثیر را دارند
3. **تولید کند** نقشه‌های برجستگی (Saliency Maps) برای تصاویر MRI
4. **ارائه دهد** Feature Attribution برای تمام ورودی‌ها

---

## روش‌های پیاده‌سازی شده

### 1. Gradient-based Saliency Maps

**فرمول ریاضی:**

```
S_i = |∂y/∂x_i|
```

**ویژگی‌ها:**
- محاسبه مستقیم gradient
- سرعت بالا
- مناسب برای اهداف اولیه

**استفاده:**

```python
from app.services.xai_service import XAIService

xai = XAIService(model, device)
saliency = xai.compute_saliency_map(
    input_tensor,
    target_class=0,  # 0=Alzheimer, 1=Parkinson
    method="gradient"
)
```

### 2. Integrated Gradients

**فرمول ریاضی:**

```
IG_i(x) = (x_i - x'_i) × ∫[α=0 to 1] (∂F(x' + α(x - x')) / ∂x_i) dα
```

**ویژگی‌های مهم:**
- ✅ **Sensitivity**: اگر ورودی و baseline در یک ویژگی متفاوت باشند و پیش‌بینی متفاوت باشد، attribution غیرصفر است
- ✅ **Implementation Invariance**: Attribution برای مدل‌های معادل یکسان است
- ✅ **Completeness**: Σ IG_i = F(x) - F(baseline)

**استفاده:**

```python
saliency = xai.compute_saliency_map(
    input_tensor,
    target_class=0,
    method="integrated_gradients"
)
```

### 3. SmoothGrad

**فرمول ریاضی:**

```
S_SmoothGrad(x) = (1/N) Σ[i=1 to N] S(x + N(0, σ²))
```

**هدف**: کاهش نویز در saliency maps با میانگین‌گیری

**استفاده:**

```python
saliency = xai.compute_saliency_map(
    input_tensor,
    target_class=0,
    method="smoothgrad",
    n_samples=50,
    noise_scale=0.15
)
```

### 4. SHAP Values

**فرمول ریاضی:**

```
SHAP_i = Σ[S ⊆ F\{i}] [|S|! (|F| - |S| - 1)! / |F|!] × [f(S ∪ {i}) - f(S)]
```

**ویژگی‌های مطلوب:**
- Efficiency: Σ SHAP_i = f(x) - f(baseline)
- Symmetry: ویژگی‌های معادل SHAP یکسان دارند
- Dummy: ویژگی‌های غیرمؤثر SHAP = 0 دارند

**استفاده:**

```python
shap_values = xai.compute_feature_attribution_shap(
    input_tensor,
    target_class=0,
    background_data=background_samples,
    n_samples=100
)
```

---

## استفاده از XAI

### در Python Code

```python
from app.services.ai_model_service import ai_model_service
from app.services.xai_service import XAIService

# Extract features
features = ai_model_service.extract_features(patient_data)

# Make prediction
prediction_result = await ai_model_service.predict(patient_data)

# Generate explanation
if ai_model_service.xai_service:
    explanation = ai_model_service.xai_service.explain_prediction(
        features,
        prediction_result,
        ai_model_service.feature_names,
        method='integrated_gradients'
    )
    
    print("Top contributing features:")
    for feature_info in explanation['top_contributing_features']:
        print(f"Disease: {feature_info['disease']}")
        for feat in feature_info['features']:
            print(f"  {feat['name']}: {feat['importance']:.4f}")
```

### در API Response

پیش‌بینی‌ها به طور خودکار شامل XAI explanations هستند:

```json
{
  "alzheimer": {
    "risk_score": 0.78,
    "risk_level": "high",
    "confidence": 0.85
  },
  "parkinson": {
    "risk_score": 0.23,
    "risk_level": "low",
    "confidence": 0.82
  },
  "xai_explanation": {
    "saliency_maps": {
      "alzheimer": [0.12, 0.08, ...],
      "parkinson": [0.05, 0.11, ...]
    },
    "top_contributing_features": [
      {
        "disease": "alzheimer",
        "features": [
          {"name": "tau_protein", "importance": 0.25},
          {"name": "hippocampal_volume", "importance": 0.20},
          ...
        ]
      }
    ],
    "confidence_analysis": {
      "alzheimer_confidence": 0.85,
      "explanation": "High confidence in Alzheimer's assessment..."
    }
  }
}
```

---

## API Endpoints

### GET /api/v1/predictions/{prediction_id}/explain

**توضیحات**: دریافت توضیحات پیشرفته برای یک پیش‌بینی

**پارامترها:**
- `prediction_id` (path): شناسه پیش‌بینی
- `method` (query): روش XAI
  - `gradient`: Vanilla gradient
  - `integrated_gradients`: Integrated Gradients (پیش‌فرض، دقیق‌تر)
  - `smoothgrad`: SmoothGrad
  - `shap`: SHAP values

**مثال Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/predictions/1/explain?method=integrated_gradients" \
  -H "Authorization: Bearer <token>"
```

**Response:**

```json
{
  "prediction_id": 1,
  "method": "integrated_gradients",
  "explanation": {
    "prediction": {...},
    "saliency_maps": {
      "alzheimer": [...],
      "parkinson": [...]
    },
    "top_contributing_features": [...],
    "confidence_analysis": {...}
  },
  "timestamp": "2024-12-XXT..."
}
```

---

## مستندات فنی

### ساختار XAI Service

```python
class XAIService:
    def compute_saliency_map(input_tensor, target_class, method) -> np.ndarray
    def _gradient_saliency(input_tensor, target_class) -> np.ndarray
    def _integrated_gradients(input_tensor, target_class, baseline, steps) -> np.ndarray
    def _smoothgrad_saliency(input_tensor, target_class, n_samples, noise_scale) -> np.ndarray
    def compute_feature_attribution_shap(input_tensor, target_class, background_data, n_samples) -> np.ndarray
    def generate_saliency_map_for_mri(mri_features, imaging_features, feature_names, target_class) -> Dict
    def explain_prediction(input_features, prediction_result, feature_names, method) -> Dict
```

### یکپارچه‌سازی با AI Model Service

XAI Service به طور خودکار در `AIModelService` initialize می‌شود:

```python
# در ai_model_service.py
self.xai_service = initialize_xai_service(self.model, self.device)
```

### استفاده در پیش‌بینی‌ها

هر پیش‌بینی به طور خودکار شامل XAI explanations می‌شود:

```python
result = await ai_model_service.predict(patient_data)
# result['xai_explanation'] شامل توضیحات است
```

---

## نقشه‌های برجستگی برای MRI

### روش تولید

1. **استخراج ویژگی‌های MRI**: حجم هیپوکامپ، ضخامت قشر مغز، ...
2. **محاسبه Attribution**: استفاده از Integrated Gradients
3. **Mapping به مناطق آناتومیکی**: تطبیق با ساختار مغز
4. **نمایش بصری**: Overlay بر روی تصاویر MRI

### مثال خروجی

```
Region Attribution:
- Hippocampus: 40% contribution
- Temporal Cortex: 25% contribution
- White Matter: 15% contribution
- Ventricles: 10% contribution
- Other: 10% contribution
```

---

## مزایای نوآوری برای ثبت اختراع

### 1. توضیح‌پذیری پیشرفته

- ✅ روش‌های متعدد (Gradient, Integrated Gradients, SmoothGrad, SHAP)
- ✅ Mapping به مناطق آناتومیکی مغز
- ✅ نمایش بصری برای پزشکان

### 2. قابلیت اطمینان

- ✅ Feature Attribution دقیق
- ✅ Confidence Analysis
- ✅ Uncertainty Quantification

### 3. کاربرد بالینی

- ✅ کمک به رادیولوژیست‌ها در تفسیر
- ✅ شناسایی مناطق مهم مغز
- ✅ بهبود اعتماد پزشکان به AI

---

## منابع علمی

1. **Integrated Gradients**:
   - Sundararajan, M., et al. (2017). Axiomatic Attribution for Deep Networks. ICML.

2. **SHAP Values**:
   - Lundberg, S. M., & Lee, S. I. (2017). A Unified Approach to Interpreting Model Predictions. NIPS.

3. **SmoothGrad**:
   - Smilkov, D., et al. (2017). SmoothGrad: Removing noise by adding noise. ICML.

---

**آخرین به‌روزرسانی**: 2024-12-XX  
**نسخه**: 1.0  
**تهیه شده توسط**: NeuroPredict-AI Research Team

