# مستندات روش همجوشی داده‌ها (Data Fusion Method Documentation)

## برای ثبت اختراع - جزئیات ریاضی و الگوریتمی

**نسخه**: 1.0  
**تاریخ**: 2024-12-XX  
**وضعیت**: Confidential - برای ثبت اختراع

---

## 📋 خلاصه

این سند روش نوآورانه همجوشی داده‌های چند-مدالیته (Multi-modal Data Fusion) در سیستم NeuroPredict-AI را با جزئیات ریاضی و الگوریتمی کامل توضیح می‌دهد.

**نوآوری اصلی**: استفاده از معماری شبکه عصبی عمیق که به صورت end-to-end یاد می‌گیرد چگونه ویژگی‌های ناهمگون از مدالیته‌های مختلف را به صورت بهینه ترکیب کند.

---

## 1. معرفی مدالیته‌ها

### 1.1 مدالیته‌های ورودی

سیستم NeuroPredict-AI از **4 مدالیته اصلی** داده استفاده می‌کند:

#### الف) داده‌های MRI (Imaging Modality)

**ویژگی‌های استخراج شده:**
- `hippocampal_volume` ∈ R: حجم هیپوکامپ (mm³)
- `cortical_thickness` ∈ R: ضخامت قشر مغز (mm)
- `ventricular_volume` ∈ R: حجم بطنی (mm³)
- `white_matter_hyperintensities` ∈ R: شدت هیپراینتنسیتی ماده سفید (scale 0-10)
- `brain_volume_total` ∈ R: حجم کل مغز (mm³)
- `imaging_features` ∈ R³²: ویژگی‌های عمیق استخراج شده از CNN (32 بعد)

**نمادگذاری ریاضی:**
```
X_mri ∈ R^d_mri
```
که در آن `d_mri = 5 + 32 = 37`

#### ب) نمرات شناختی (Cognitive Modality)

**ویژگی‌های استخراج شده:**
- `mmse_score` ∈ [0, 30]: نمره Mini-Mental State Examination
- `moca_score` ∈ [0, 30]: نمره Montreal Cognitive Assessment
- `memory_score` ∈ [0, 100]: نمره حافظه
- `attention_score` ∈ [0, 100]: نمره توجه
- `executive_function_score` ∈ [0, 100]: نمره عملکرد اجرایی

**نمادگذاری ریاضی:**
```
X_cognitive ∈ R^d_cog
```
که در آن `d_cog = 5`

#### ج) بیومارکرها (Biomarker Modality)

**ویژگی‌های استخراج شده:**
- `amyloid_beta` ∈ R: سطح آمیلوئید بتا (pg/mL)
- `tau_protein` ∈ R: سطح پروتئین tau (pg/mL)
- `dopamine_level` ∈ R: سطح دوپامین (ng/mL)

**نمادگذاری ریاضی:**
```
X_biomarker ∈ R^d_bio
```
که در آن `d_bio = 3`

#### د) داده‌های جمعیت‌شناختی و ژنتیکی (Demographic/Genetic Modality)

**ویژگی‌های استخراج شده:**
- `age` ∈ R: سن (سال)
- `gender` ∈ {0, 1}: جنسیت (0=زن, 1=مرد)
- `education_years` ∈ N: سال‌های تحصیل
- `apoe_e4_status` ∈ {0, 1}: وضعیت APOE-e4 allele

**نمادگذاری ریاضی:**
```
X_demographic ∈ R^d_dem
```
که در آن `d_dem = 4`

---

## 2. روش همجوشی (Data Fusion Method)

### 2.1 گام 1: پیش‌پردازش و نرمال‌سازی

**هدف**: تبدیل داده‌های ناهمگون به فضای یکنواخت [0, 1]

#### الف) نرمال‌سازی خطی

برای ویژگی‌های پیوسته:

```
x_normalized = (x - x_min) / (x_max - x_min)
```

**مثال برای ویژگی‌های مختلف:**

```
age_norm = age / 100.0  # فرض: max age = 100
mmse_norm = mmse_score / 30.0  # max score = 30
amyloid_norm = amyloid_beta / 1000.0  # typical max = 1000 pg/mL
hippocampal_vol_norm = hippocampal_volume / 5000.0  # typical max = 5000 mm³
```

#### ب) کدگذاری دودویی

برای ویژگی‌های دسته‌ای:

```
gender_encoded = {
    1.0  if gender == 'male'
    0.0  if gender == 'female'
}
```

### 2.2 گام 2: Concatenation اولیه (Early Fusion)

**عمل**: ترکیب عمودی تمام ویژگی‌های نرمال‌شده

**فرمول ریاضی:**

```
X_concatenated = [X_demographic; X_cognitive; X_biomarker; X_mri] ∈ R^d
```

که در آن:
```
d = d_dem + d_cog + d_bio + d_mri
  = 4 + 5 + 3 + 37
  = 49 ≈ 50
```

**نمایش ماتریسی:**

```
X_concatenated = [age_norm, gender_encoded, education_years_norm, apoe_e4,
                  mmse_norm, moca_norm, memory_score_norm, attention_score_norm, exec_function_norm,
                  amyloid_norm, tau_norm, dopamine_norm,
                  hippocampal_vol_norm, cortical_thickness_norm, ventricular_vol_norm, 
                  wmh_norm, brain_vol_norm,
                  imaging_feat_1, ..., imaging_feat_32]
```

### 2.3 گام 3: Feature Extraction با یادگیری عمیق

**نوآوری اصلی**: استفاده از لایه‌های Fully Connected که **تعاملات بین-مدالیته** را یاد می‌گیرند.

#### ساختار لایه‌های Feature Extractor

```
Layer 1: Linear Transformation
h^(1) = W^(1) X_concatenated + b^(1)
       W^(1) ∈ R^(256 × 50), b^(1) ∈ R^256

Layer 2: Normalization and Activation
h^(1)_norm = BatchNorm(h^(1))
h^(1)_activated = ReLU(h^(1)_norm)

Layer 3: Regularization
h^(1)_dropout = Dropout(h^(1)_activated, p=0.3)
```

**فرمول کامل برای هر لایه:**

```
h^(l) = Dropout(ReLU(BatchNorm(W^(l) h^(l-1) + b^(l))), p=0.3)
```

که در آن:
- `l` = 1, 2, 3 (3 لایه)
- `W^(1)` ∈ R^(256×50), `W^(2)` ∈ R^(128×256), `W^(3)` ∈ R^(64×128)
- `b^(1)` ∈ R^256, `b^(2)` ∈ R^128, `b^(3)` ∈ R^64

#### Batch Normalization - جزئیات ریاضی

برای هر لایه `l` و هر نمونه `i` در batch `B`:

**گام 1: محاسبه میانگین و واریانس batch**

```
μ_B^(l) = (1/|B|) Σ[i∈B] h^(l)_i
σ²_B^(l) = (1/|B|) Σ[i∈B] (h^(l)_i - μ_B^(l))²
```

**گام 2: نرمال‌سازی**

```
ĥ^(l)_i = (h^(l)_i - μ_B^(l)) / √(σ²_B^(l) + ε)
```

که در آن `ε = 10⁻⁵` برای جلوگیری از تقسیم بر صفر

**گام 3: Scale and Shift (با پارامترهای قابل یادگیری)**

```
h^(l)_norm_i = γ^(l) * ĥ^(l)_i + β^(l)
```

که در آن:
- `γ^(l)`, `β^(l)`: پارامترهای قابل یادگیری

**هدف**: 
- تثبیت فرآیند یادگیری
- کاهش Internal Covariate Shift
- امکان استفاده از learning rate بالاتر

#### ReLU Activation - جزئیات ریاضی

```
ReLU(x) = max(0, x) = {
    x    if x > 0
    0    if x ≤ 0
}
```

**مزیت**: 
- غیرخطی بودن
- محاسبات سریع
- جلوگیری از Vanishing Gradient (برای x > 0)

**مشتق:**

```
d/dx ReLU(x) = {
    1    if x > 0
    0    if x ≤ 0
}
```

#### Dropout Regularization - جزئیات ریاضی

**در حین آموزش:**

برای هر عنصر `h_i`:

```
h'_i = {
    h_i / (1 - p)    with probability (1 - p)
    0                with probability p
}
```

که در آن `p = 0.3` (نرخ dropout)

**در حین استنتاج:**

```
h'_i = h_i
```

**هدف**: 
- جلوگیری از Overfitting
- بهبود Generalization
- ایجاد Ensemble Effect

**اثر ریاضی**: در آموزش، هر لایه در واقع `1/(1-p)` شبکه مجزا را آموزش می‌دهد (ensemble)

### 2.4 گام 4: استخراج ویژگی‌های نهایی (Final Feature Representation)

**خروجی Feature Extractor:**

```
h_final = h^(3)_dropout ∈ R^64
```

این بردار 64 بعدی نمایانگر **ویژگی‌های ترکیبی** است که:
- اطلاعات از تمام مدالیته‌ها را شامل می‌شود
- تعاملات پیچیده بین مدالیته‌ها را مدل کرده است
- برای پیش‌بینی بیماری‌های مختلف قابل استفاده است

---

## 3. معماری Ensemble Heads

### 3.1 ایده اصلی

به جای استفاده از یک head برای پیش‌بینی، از **سرهای جداگانه** برای هر بیماری استفاده می‌شود که:
- از ویژگی‌های مشترک (shared features) استفاده می‌کنند
- وزن‌های متفاوت دارند
- به صورت مستقل آموزش داده می‌شوند

### 3.2 ساختار Alzheimer Head

```
Input: h_final ∈ R^64

Hidden Layer 1:
h_alz^(1) = ReLU(W_alz^(1) h_final + b_alz^(1))
         W_alz^(1) ∈ R^(32 × 64), b_alz^(1) ∈ R^32

Output Layer:
y_alz = σ(W_alz^(2) h_alz^(1) + b_alz^(2))
      σ: Sigmoid function
      W_alz^(2) ∈ R^(1 × 32), b_alz^(2) ∈ R^1
```

**Sigmoid Activation:**

```
σ(x) = 1 / (1 + e^(-x))
```

**خروجی**: `y_alz ∈ [0, 1]` (احتمال خطر Alzheimer's)

### 3.3 ساختار Parkinson Head

```
Input: h_final ∈ R^64

Hidden Layer 1:
h_park^(1) = ReLU(W_park^(1) h_final + b_park^(1))
           W_park^(1) ∈ R^(32 × 64), b_park^(1) ∈ R^32

Output Layer:
y_park = σ(W_park^(2) h_park^(1) + b_park^(2))
```

**خروجی**: `y_park ∈ [0, 1]` (احتمال خطر Parkinson's)

### 3.4 مزایای Ensemble Heads

**1. یادگیری بهینه برای هر بیماری:**

هر head می‌تواند وزن‌های متفاوتی به ویژگی‌های مشترک بدهد:

```
∂L_alz/∂W_alz ≠ ∂L_park/∂W_park
```

**2. به‌اشتراک‌گذاری دانش:**

ویژگی‌های مشترک `h_final` از داده‌های هر دو بیماری یاد می‌گیرند:

```
∂h_final/∂W^(3) ∝ (∂L_alz/∂h_final + ∂L_park/∂h_final)
```

**3. کاهش نیاز به داده:**

در مقایسه با آموزش مدل‌های جداگانه، این روش نیاز به داده کمتری دارد.

---

## 4. تابع Loss و Optimization

### 4.1 Binary Cross-Entropy Loss

برای هر بیماری:

```
L_alz = -[y_alz_true * log(y_alz_pred) + (1 - y_alz_true) * log(1 - y_alz_pred)]
```

```
L_park = -[y_park_true * log(y_park_pred) + (1 - y_park_true) * log(1 - y_park_pred)]
```

**Loss کل:**

```
L_total = L_alz + L_park
```

### 4.2 Adam Optimizer

برای هر پارامتر `θ`:

**Momentum:**

```
m_t = β₁ m_(t-1) + (1 - β₁) ∇_θ L(θ_(t-1))
v_t = β₂ v_(t-1) + (1 - β₂) [∇_θ L(θ_(t-1))]²
```

**Bias Correction:**

```
m̂_t = m_t / (1 - β₁^t)
v̂_t = v_t / (1 - β₂^t)
```

**Update:**

```
θ_t = θ_(t-1) - (α / (√v̂_t + ε)) * m̂_t
```

که در آن:
- `α = 0.001`: learning rate
- `β₁ = 0.9`: decay rate برای momentum
- `β₂ = 0.999`: decay rate برای squared gradients
- `ε = 10⁻⁸`: مقدار کوچک

---

## 5. نوآوری‌های کلیدی برای ثبت اختراع

### 5.1 نوآوری 1: یادگیری تعاملات بین-مدالیته

**ادعا**: استفاده از لایه‌های Fully Connected که به صورت **end-to-end** یاد می‌گیرند چگونه ویژگی‌های ناهمگون را ترکیب کنند.

**مزیت نسبت به روش‌های سنتی:**
- ❌ **Concatenation ساده**: `X_combined = [X₁; X₂; ...; Xₙ]` → عدم یادگیری تعاملات
- ✅ **روش نوآورانه**: لایه‌های یادگیری عمیق → یادگیری تعاملات پیچیده

**فرمول ریاضی:**

در concatenation ساده، هر مدالیته مستقل است:
```
y = f([X₁; X₂; ...; Xₙ])
```

در روش نوآورانه، تعاملات یاد گرفته می‌شوند:
```
h^(l) = g^(l)(W^(l) h^(l-1) + b^(l))
```
که در آن `g^(l)` یاد می‌گیرد که چگونه ویژگی‌های مختلف با هم تعامل کنند

### 5.2 نوآوری 2: Ensemble Heads با Shared Features

**ادعا**: استفاده از ویژگی‌های مشترک (shared features) برای چند بیماری با سرهای جداگانه.

**فرمول ریاضی:**

```
h_shared = FeatureExtractor(X_concatenated)
y_disease₁ = Head₁(h_shared)
y_disease₂ = Head₂(h_shared)
```

**مزیت**: 
- به‌اشتراک‌گذاری دانش بین بیماری‌ها
- کاهش نیاز به داده
- بهبود generalization

### 5.3 نوآوری 3: Architecture Scalability

**ادعا**: معماری قابل گسترش که می‌تواند:
- مدالیته‌های جدید اضافه کند
- بیماری‌های جدید اضافه کند
- بدون تغییر architecture اصلی

**مثال:**

برای اضافه کردن مدالیته جدید `X_new`:
```
X_concatenated_new = [X_concatenated; X_new]
h_final_new = FeatureExtractor_new(X_concatenated_new)
```

---

## 6. پیاده‌سازی الگوریتمی

### 6.1 Pseudocode

```
Algorithm: Multi-Modal Data Fusion for Disease Prediction

Input: X_dem, X_cog, X_bio, X_mri
Output: y_alz, y_park

// Step 1: Normalize each modality
X_dem_norm = Normalize(X_dem)
X_cog_norm = Normalize(X_cog)
X_bio_norm = Normalize(X_bio)
X_mri_norm = Normalize(X_mri)

// Step 2: Concatenate
X_combined = Concatenate(X_dem_norm, X_cog_norm, X_bio_norm, X_mri_norm)

// Step 3: Feature Extraction
h^(0) = X_combined
for l = 1 to 3:
    h^(l) = W^(l) * h^(l-1) + b^(l)
    h^(l) = BatchNorm(h^(l))
    h^(l) = ReLU(h^(l))
    h^(l) = Dropout(h^(l), p=0.3)
end for
h_final = h^(3)

// Step 4: Disease-specific predictions
h_alz = ReLU(W_alz^(1) * h_final + b_alz^(1))
y_alz = Sigmoid(W_alz^(2) * h_alz + b_alz^(2))

h_park = ReLU(W_park^(1) * h_final + b_park^(1))
y_park = Sigmoid(W_park^(2) * h_park + b_park^(2))

return (y_alz, y_park)
```

---

## 7. ادعاهای اختراع (Patent Claims)

### Claim 1: روش همجوشی داده‌های چند-مدالیته

**ادعا**: روشی برای پیش‌بینی خطر بیماری‌های عصبی شامل:

1. **دریافت داده‌ها** از حداقل 3 مدالیته:
   - تصاویر MRI
   - نمرات شناختی
   - بیومارکرهای زیستی
   - داده‌های جمعیت‌شناختی/ژنتیکی

2. **نرمال‌سازی** هر مدالیته به فضای یکنواخت

3. **Concatenation** ویژگی‌های نرمال‌شده

4. **استخراج ویژگی با یادگیری عمیق**:
   - استفاده از حداقل 2 لایه Fully Connected
   - Batch Normalization
   - ReLU Activation
   - Dropout Regularization

5. **پیش‌بینی** با استفاده از Ensemble Heads

### Claim 2: معماری Ensemble Heads

**ادعا**: معماری شبکه عصبی شامل:

1. **Shared Feature Extractor**: استخراج ویژگی‌های مشترک از داده‌های چند-مدالیته

2. **Multiple Disease Heads**: حداقل 2 head جداگانه برای بیماری‌های مختلف

3. **Joint Training**: آموزش همزمان تمام heads با loss function ترکیبی

### Claim 3: توضیح‌پذیری با Saliency Maps

**ادعا**: روشی برای تولید توضیحات شامل:

1. **محاسبه Gradients**: با respect به ورودی

2. **Integrated Gradients**: برای attribution دقیق

3. **Mapping به مناطق آناتومیکی**: تطبیق attribution با مناطق مغزی

---

## 8. مزایای نوآوری

### 8.1 بهبود دقت

- **ترکیب اطلاعات چند منبع**: دقت بالاتر نسبت به استفاده از یک مدالیته
- **یادگیری تعاملات**: استخراج الگوهای پیچیده که در یک مدالیته دیده نمی‌شوند

### 8.2 توضیح‌پذیری

- **Feature Attribution**: درک اینکه کدام مدالیته‌ها مهم‌ترند
- **Saliency Maps**: شناسایی مناطق مغزی مهم

### 8.3 مقیاس‌پذیری

- **افزودن مدالیته جدید**: بدون تغییر architecture اصلی
- **افزودن بیماری جدید**: فقط با اضافه کردن head جدید

---

## 9. مقایسه با روش‌های موجود

| روش | ویژگی‌های مهم | محدودیت‌ها | مزیت روش نوآورانه |
|-----|--------------|-----------|-------------------|
| Concatenation ساده | سادگی | عدم یادگیری تعاملات | ✅ یادگیری تعاملات |
| Late Fusion | پیش‌بینی‌های جداگانه | عدم به‌اشتراک‌گذاری دانش | ✅ Shared features |
| Single Head | سادگی | عدم تخصص‌گرایی | ✅ Ensemble heads |

---

## 10. مراجع علمی

1. **Multi-modal Learning**: 
   - Baltrušaitis, T., Ahuja, C., & Morency, L. P. (2018). Multimodal machine learning: A survey and taxonomy. TPAMI.

2. **Deep Learning**:
   - Goodfellow, I., Bengio, Y., & Courville, A. (2016). Deep Learning. MIT Press.

3. **Batch Normalization**:
   - Ioffe, S., & Szegedy, C. (2015). Batch normalization: Accelerating deep network training by reducing internal covariate shift. ICML.

4. **Dropout**:
   - Srivastava, N., et al. (2014). Dropout: A simple way to prevent neural networks from overfitting. JMLR.

---

**آخرین به‌روزرسانی**: 2024-12-XX  
**نسخه**: 1.0  
**وضعیت**: Confidential - برای ثبت اختراع  
**تهیه شده توسط**: NeuroPredict-AI Research Team


