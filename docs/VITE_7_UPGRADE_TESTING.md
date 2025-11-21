# Vite 7.x Upgrade Testing Guide

راهنمای کامل تست پس از به‌روزرسانی Vite از نسخه 5.x به 7.x

## ✅ به‌روزرسانی انجام شده

- **Frontend**: vite@^7.2.4 ✅
- **Admin Dashboard**: vite@^7.2.4 ✅

## 🔍 چک‌لیست تست

### 1. Build Testing

```bash
# Frontend
cd frontend
npm install
npm run build

# بررسی خروجی
ls -la dist/
```

**چک‌ها:**
- [ ] Build بدون خطا انجام شود
- [ ] فایل‌های HTML, JS, CSS تولید شوند
- [ ] Bundle size قابل قبول باشد (< 5MB برای production)
- [ ] Source maps تولید شوند

### 2. Development Server Testing

```bash
# Frontend
cd frontend
npm run dev

# Admin Dashboard
cd admin-dashboard
npm run dev
```

**چک‌ها:**
- [ ] Development server شروع شود
- [ ] HMR (Hot Module Replacement) کار کند
- [ ] Fast refresh برای React کار کند
- [ ] Console errors وجود نداشته باشد

### 3. Browser Compatibility Testing

**مرورگرهای مورد آزمایش:**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Chrome (Android)
- [ ] Mobile Safari (iOS)

**تست در هر مرورگر:**
- [ ] Application load شود
- [ ] Routes کار کنند
- [ ] API calls موفق باشند
- [ ] State management کار کند
- [ ] Forms submit شوند

### 4. Feature Testing

#### Authentication Flow
- [ ] Login page نمایش داده شود
- [ ] Login موفق باشد
- [ ] Token ذخیره شود
- [ ] Protected routes کار کنند
- [ ] Logout کار کند

#### Patient Management
- [ ] لیست بیماران نمایش داده شود
- [ ] Create patient کار کند
- [ ] Edit patient کار کند
- [ ] Delete patient کار کند
- [ ] Search کار کند

#### Predictions
- [ ] Create prediction کار کند
- [ ] View predictions کار کند
- [ ] Prediction results نمایش داده شود
- [ ] Charts/reports render شوند

#### Admin Dashboard
- [ ] Dashboard load شود
- [ ] Statistics نمایش داده شوند
- [ ] Navigation کار کند
- [ ] Settings قابل تغییر باشند

### 5. Performance Testing

```bash
# Build برای production
npm run build

# بررسی Bundle size
npx vite-bundle-visualizer
```

**معیارهای عملکرد:**
- [ ] First Contentful Paint (FCP) < 1.5s
- [ ] Time to Interactive (TTI) < 3.5s
- [ ] Largest Contentful Paint (LCP) < 2.5s
- [ ] Cumulative Layout Shift (CLS) < 0.1

### 6. Vite 7.x Specific Features

#### New Features در Vite 7:
- [ ] Import attributes پشتیبانی شوند
- [ ] TypeScript 5.7 features کار کنند
- [ ] New HMR algorithm کار کند
- [ ] Improved build performance قابل مشاهده باشد

### 7. Configuration Testing

بررسی `vite.config.ts`:

```typescript
// بررسی compatibility
export default defineConfig({
  plugins: [react()],
  // Vite 7.x compatibility checks
})
```

**چک‌ها:**
- [ ] Config valid باشد
- [ ] Plugins compatible باشند
- [ ] Build options کار کنند
- [ ] Server options کار کنند

### 8. Dependency Compatibility

بررسی وابستگی‌های کلیدی:

```bash
npm outdated
npm audit
```

**وابستگی‌های مهم:**
- [ ] @vitejs/plugin-react compatible باشد
- [ ] TypeScript 5.7.x کار کند
- [ ] TailwindCSS کار کند
- [ ] React Router 6 کار کند

### 9. Environment Variables

```bash
# بررسی environment variables
cat .env.example
```

**چک‌ها:**
- [ ] VITE_* variables کار کنند
- [ ] Production build با env vars کار کند
- [ ] Type safety برای env vars حفظ شود

### 10. Error Handling

**تست خطاها:**
- [ ] 404 errors handle شوند
- [ ] Network errors handle شوند
- [ ] Build errors واضح باشند
- [ ] Runtime errors در console نمایش داده شوند

## 🧪 Automated Testing

### E2E Tests

```bash
cd tests/e2e
npx playwright test
```

**تست‌های E2E:**
- [ ] Auth flow
- [ ] Patient management
- [ ] Predictions workflow

### Unit Tests (if any)

```bash
cd frontend
npm test
```

## 📊 Performance Metrics

### Before vs After Comparison

| Metric | Vite 5.x | Vite 7.x | Target |
|--------|----------|----------|--------|
| Build Time | ? | ? | < 30s |
| Bundle Size | ? | ? | < 5MB |
| Dev Server Start | ? | ? | < 3s |
| HMR Update | ? | ? | < 100ms |

## 🐛 Known Issues & Breaking Changes

### Vite 7.x Breaking Changes:

1. **Node.js Version**: نیاز به Node.js 18+
   - [ ] بررسی Node.js version: `node --version`

2. **Import Attributes**: New syntax
   - [ ] بررسی استفاده از `import type` و `import with`

3. **HMR API Changes**: Some HMR APIs changed
   - [ ] بررسی custom HMR handlers

### Workarounds (if needed):

```typescript
// اگر مشکلی وجود دارد، این کارها را امتحان کنید:
// 1. Clear cache
rm -rf node_modules/.vite

// 2. Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

// 3. Check vite.config.ts compatibility
```

## ✅ Sign-off Checklist

قبل از deploy به production:

- [ ] تمام تست‌های بالا انجام شده
- [ ] Performance metrics قابل قبول
- [ ] Browser compatibility بررسی شده
- [ ] E2E tests pass می‌شوند
- [ ] No critical errors
- [ ] Documentation به‌روزرسانی شده
- [ ] Team review انجام شده

## 📝 Test Report Template

```
## Vite 7.x Upgrade Test Report

**Date**: _____________
**Tester**: _____________
**Version**: vite@7.2.4

### Build Tests
- [ ] Pass / [ ] Fail
- Issues: _____________

### Dev Server Tests
- [ ] Pass / [ ] Fail
- Issues: _____________

### Browser Compatibility
- Chrome: [ ] Pass / [ ] Fail
- Firefox: [ ] Pass / [ ] Fail
- Safari: [ ] Pass / [ ] Fail
- Edge: [ ] Pass / [ ] Fail

### Performance
- Build Time: _____s
- Bundle Size: _____MB
- FCP: _____s
- TTI: _____s

### Known Issues
1. _____________
2. _____________

### Sign-off
- [ ] Ready for production
- [ ] Needs more testing
```

## 🔗 References

- [Vite 7 Release Notes](https://vitejs.dev/blog/announcing-vite7)
- [Migration Guide](https://vitejs.dev/guide/migration)
- [Vite GitHub Issues](https://github.com/vitejs/vite/issues)

