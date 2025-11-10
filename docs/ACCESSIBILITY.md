# ♿ NeuroPredict-AI Accessibility Guide

## WCAG 2.1 Compliance

NeuroPredict-AI is designed to meet WCAG 2.1 Level AA standards.

### Keyboard Navigation

All interactive elements are keyboard accessible:

- **Tab**: Navigate between elements
- **Enter/Space**: Activate buttons and links
- **Arrow Keys**: Navigate within components (e.g., MRI viewer)
- **Escape**: Close modals and dialogs
- **Alt + S**: Skip to main content
- **Ctrl/Cmd + K**: Focus search input

### Screen Reader Support

- All images have alt text
- Form inputs have labels
- Buttons have descriptive aria-labels
- Navigation landmarks are properly marked
- Status messages use aria-live regions

### ARIA Attributes

- `role`: Navigation, main, dialog, alert
- `aria-label`: Descriptive labels for icons and buttons
- `aria-current`: Current page indicator
- `aria-live`: Dynamic content updates
- `aria-expanded`: Collapsible sections

### Color Contrast

- Text meets WCAG AA contrast ratios (4.5:1 for normal text, 3:1 for large text)
- Interactive elements have visible focus indicators
- Color is not the only means of conveying information

### Responsive Design

- Works on all screen sizes (320px and up)
- Touch targets are at least 44x44 pixels
- Content reflows appropriately on smaller screens

### Internationalization

- RTL support for Persian/Farsi
- Language switching without page reload
- Proper text direction handling

---

*Last Updated: November 2024*

