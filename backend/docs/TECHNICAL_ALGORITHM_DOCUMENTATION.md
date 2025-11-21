# مستندات فنی الگوریتم - NeuroPredict-AI

## مستندات نوآوری الگوریتمی برای ثبت اختراع

**نسخه**: 1.0  
**تاریخ**: 2024-12-XX  
**تهیه شده برای**: ثبت اختراع (Patent Application)

---

## 📋 فهرست مطالب

1. [خلاصه اجرایی](#خلاصه-اجرایی)
2. [نوآوری الگوریتمی](#نوآوری-الگوریتمی)
3. [روش همجوشی داده‌ها (Data Fusion)](#روش-همجوشی-دادهها-data-fusion)
4. [معماری شبکه عصبی](#معماری-شبکه-عصبی)
5. [الگوریتم‌های توضیح‌پذیری (XAI)](#الگوریتمهای-توضیحپذیری-xai)
6. [جزئیات ریاضی](#جزئیات-ریاضی)

---

## خلاصه اجرایی

### نوآوری اصلی

سیستم NeuroPredict-AI از یک **روش نوآورانه همجوشی داده‌های چند-مدالیته** (Multi-modal Data Fusion) استفاده می‌کند که:

1. **ترکیب بهینه** داده‌های ناهمگون (MRI، Cognitive Scores، Biomarkers، Genetic)
2. **استخراج خودکار ویژگی‌های مرتبط** از هر مدالیته
3. **یادگیری تعاملی** بین مدالیته‌های مختلف
4. **توضیح‌پذیری پیشرفته** با Saliency Maps و Feature Attribution

---

## نوآوری الگوریتمی

### 1. معماری چند-مدالیته با Feature Fusion

**نوآوری**: استفاده از معماری شبکه عصبی که به صورت **end-to-end** یاد می‌گیرد که چگونه ویژگی‌های مختلف مدالیته‌ها را ترکیب کند.

**مزایا نسبت به روش‌های سنتی:**
- ❌ روش‌های سنتی: Concatenation ساده ویژگی‌ها
- ✅ روش نوآورانه: Feature Fusion با توجه به روابط متقابل مدالیته‌ها

### 2. Ensemble Heads برای پیش‌بینی چند-بیماری

**نوآوری**: استفاده از **سرهای جداگانه** (Separate Heads) برای هر بیماری که از ویژگی‌های مشترک استفاده می‌کنند اما وزن‌های متفاوت دارند.

**مزیت**: 
- یادگیری همزمان برای چند بیماری
- به‌اشتراک‌گذاری دانش بین بیماری‌ها
- کاهش نیاز به داده

---

## روش همجوشی داده‌ها (Data Fusion)

### فرمول‌بندی ریاضی

فرض کنید:
- **X_mri**: ویژگی‌های MRI (m بعد)
- **X_cognitive**: نمرات شناختی (c بعد)
- **X_biomarker**: بیومارکرها (b بعد)
- **X_genetic**: داده‌های ژنتیکی (g بعد)

#### گام 1: استخراج ویژگی‌های اولیه

برای هر مدالیته، یک تابع استخراج ویژگی:

```
f_mri: X_mri → h_mri ∈ R^d_mri
f_cognitive: X_cognitive → h_cognitive ∈ R^d_cog
f_biomarker: X_biomarker → h_biomarker ∈ R^d_bio
f_genetic: X_genetic → h_genetic ∈ R^d_gen
```

که در آن:
- `d_mri`, `d_cog`, `d_bio`, `d_gen` ابعاد فضای ویژگی استخراج شده برای هر مدالیته هستند

#### گام 2: همجوشی اولیه (Early Fusion)

ویژگی‌های استخراج شده به صورت عمودی concatenate می‌شوند:

```
h_concatenated = [h_mri; h_cognitive; h_biomarker; h_genetic] ∈ R^(d_mri + d_cog + d_bio + d_gen)
```

#### گام 3: Feature Extraction با یادگیری تعاملی

**نوآوری اصلی**: استفاده از لایه‌های Fully Connected با Batch Normalization و Dropout:

```
h^(0) = h_concatenated
h^(1) = ReLU(BN(W^(1) h^(0) + b^(1)))
h^(1) = Dropout(h^(1), p=0.3)

h^(2) = ReLU(BN(W^(2) h^(1) + b^(2)))
h^(2) = Dropout(h^(2), p=0.3)

h^(3) = ReLU(BN(W^(3) h^(2) + b^(3)))
h^(3) = Dropout(h^(3), p=0.3)
```

که در آن:
- `W^(i)`: ماتریس وزن لایه i
- `b^(i)`: بردار بایاس لایه i
- `BN`: Batch Normalization
- `ReLU`: Rectified Linear Unit activation
- `Dropout`: Regularization technique

**نکته مهم**: این لایه‌ها یاد می‌گیرند که **تعاملات پیچیده** بین ویژگی‌های مختلف مدالیته‌ها را مدل کنند.

#### گام 4: پیش‌بینی چند-بیماری

ویژگی‌های استخراج شده به سرهای جداگانه برای هر بیماری ارسال می‌شوند:

```
# برای Alzheimer's
h_alz^(1) = ReLU(W_alz^(1) h^(3) + b_alz^(1))
y_alz = σ(W_alz^(2) h_alz^(1) + b_alz^(2))

# برای Parkinson's
h_park^(1) = ReLU(W_park^(1) h^(3) + b_park^(1))
y_park = σ(W_park^(2) h_park^(1) + b_park^(2))
```

که در آن:
- `σ`: Sigmoid activation function
- `y_alz`, `y_park`: احتمالات پیش‌بینی (بین 0 و 1)

---

## معماری شبکه عصبی

### ساختار کامل

```
Input Layer (50 features)
    ↓
Feature Extraction Layers:
    - Linear(50 → 256) + ReLU + BatchNorm + Dropout(0.3)
    - Linear(256 → 128) + ReLU + BatchNorm + Dropout(0.3)
    - Linear(128 → 64) + ReLU + BatchNorm + Dropout(0.3)
    ↓
Shared Feature Representation (64 dimensions)
    ↓
    ├─→ Alzheimer Head:
    │     - Linear(64 → 32) + ReLU
    │     - Linear(32 → 1) + Sigmoid
    │
    └─→ Parkinson Head:
          - Linear(64 → 32) + ReLU
          - Linear(32 → 1) + Sigmoid
```

### جزئیات ریاضی لایه‌ها

#### Batch Normalization

برای هر لایه `i`:

```
μ_B = (1/m) Σ(x_i)  # Mean over batch
σ²_B = (1/m) Σ(x_i - μ_B)²  # Variance over batch
x̂_i = (x_i - μ_B) / √(σ²_B + ε)  # Normalized
y_i = γ * x̂_i + β  # Scale and shift
```

که در آن:
- `γ`, `β`: پارامترهای قابل یادگیری
- `ε`: مقدار کوچک برای جلوگیری از تقسیم بر صفر

#### Dropout

در حین آموزش:

```
y_i = {
    x_i / (1-p)  با احتمال (1-p)
    0            با احتمال p
}
```

در حین استنتاج:

```
y_i = x_i
```

---

## الگوریتم‌های توضیح‌پذیری (XAI)

### 1. Gradient-based Saliency Maps

**فرمول ریاضی:**

برای هر ویژگی ورودی `x_i`:

```
S_i = |∂y/∂x_i|
```

که در آن:
- `y`: خروجی پیش‌بینی
- `S_i`: اهمیت ویژگی i-ام

**نوآوری**: استفاده از این روش برای **شناسایی مناطق مغزی** که بیشترین تأثیر را در پیش‌بینی دارند.

### 2. Integrated Gradients

**فرمول ریاضی:**

```
IG_i(x) = (x_i - x'_i) × ∫[α=0 to 1] (∂F(x' + α(x - x')) / ∂x_i) dα
```

که در آن:
- `x`: ورودی اصلی
- `x'`: baseline (معمولاً صفر)
- `F`: تابع مدل
- `α`: پارامتر interpolation

**ویژگی‌های مهم**:
- **Sensitivity**: اگر ورودی و baseline در یک ویژگی متفاوت باشند و پیش‌بینی متفاوت باشد، آن ویژگی attribution غیرصفر می‌گیرد
- **Implementation Invariance**: Attribution برای مدل‌های معادل عملکردی یکسان است

### 3. SmoothGrad

**فرمول ریاضی:**

```
S_SmoothGrad(x) = (1/N) Σ[i=1 to N] S(x + N(0, σ²))
```

که در آن:
- `N`: تعداد نمونه‌های نویزی
- `σ`: انحراف معیار نویز
- `S`: تابع saliency پایه (gradient)

**هدف**: کاهش نویز در saliency maps با میانگین‌گیری

### 4. SHAP (SHapley Additive exPlanations)

**فرمول ریاضی:**

```
SHAP_i = Σ[S ⊆ F\{i}] [|S|! (|F| - |S| - 1)! / |F|!] × [f(S ∪ {i}) - f(S)]
```

که در آن:
- `F`: مجموعه تمام ویژگی‌ها
- `S`: زیرمجموعه‌ای از ویژگی‌ها
- `f`: تابع مدل
- `|S|!`: فاکتوریل اندازه S

**مزیت**: SHAP values ویژگی‌های مطلوب برای تفسیر را دارند:
- Efficiency: Σ SHAP_i = f(x) - f(baseline)
- Symmetry: ویژگی‌های معادل SHAP values یکسان دارند
- Dummy: ویژگی‌های غیرمؤثر SHAP = 0 دارند

---

## جزئیات ریاضی

### تابع Loss

برای آموزش مدل، از Binary Cross-Entropy Loss استفاده می‌شود:

```
L = -[y_true * log(y_pred) + (1 - y_true) * log(1 - y_pred)]
```

برای چند بیماری:

```
L_total = L_alzheimer + L_parkinson
```

### Optimizer

از Adam Optimizer استفاده می‌شود:

```
m_t = β₁ m_(t-1) + (1 - β₁) g_t
v_t = β₂ v_(t-1) + (1 - β₂) g_t²
m̂_t = m_t / (1 - β₁^t)
v̂_t = v_t / (1 - β₂^t)
θ_t = θ_(t-1) - (α / (√v̂_t + ε)) * m̂_t
```

که در آن:
- `g_t`: gradient در زمان t
- `β₁`, `β₂`: hyperparameters (معمولاً 0.9 و 0.999)
- `α`: learning rate

---

## ادعاهای اختراع (Patent Claims)

### Claim 1: روش همجوشی داده‌های چند-مدالیته

**ادعا**: روشی برای پیش‌بینی خطر بیماری‌های عصبی که شامل:
1. دریافت داده‌های چند-مدالیته (MRI، Cognitive، Biomarker، Genetic)
2. استخراج ویژگی‌های اولیه از هر مدالیته
3. همجوشی ویژگی‌ها با لایه‌های یادگیری عمیق که **تعاملات بین-مدالیته** را یاد می‌گیرند
4. پیش‌بینی با استفاده از ensemble heads برای هر بیماری

### Claim 2: الگوریتم توضیح‌پذیری با Saliency Maps

**ادعا**: روشی برای تولید نقشه‌های برجستگی که:
1. محاسبه gradients با respect به ورودی
2. استفاده از Integrated Gradients برای attribution دقیق
3. تطبیق attribution با مناطق آناتومیکی مغز
4. نمایش بصری برای کمک به رادیولوژیست‌ها

---

## مزایای نوآوری

### 1. بهبود دقت

- ترکیب اطلاعات از چند منبع → دقت بالاتر
- یادگیری تعاملی → استخراج الگوهای پیچیده

### 2. توضیح‌پذیری

- Saliency Maps → شناسایی مناطق مهم
- Feature Attribution → درک چگونگی تصمیم‌گیری

### 3. عمومیت‌پذیری

- معماری قابل گسترش به سایر بیماری‌ها
- امکان افزودن مدالیته‌های جدید

---

## مراجع علمی

1. Goodfellow, I., Bengio, Y., & Courville, A. (2016). Deep Learning. MIT Press.
2. Sundararajan, M., et al. (2017). Axiomatic Attribution for Deep Networks. ICML.
3. Lundberg, S. M., & Lee, S. I. (2017). A Unified Approach to Interpreting Model Predictions. NIPS.
4. Smilkov, D., et al. (2017). SmoothGrad: Removing noise by adding noise. ICML.

---

**آخرین به‌روزرسانی**: 2024-12-XX  
**نسخه**: 1.0  
**تهیه شده برای**: ثبت اختراع  
**وضعیت**: Confidential - برای استفاده داخلی و ثبت اختراع


