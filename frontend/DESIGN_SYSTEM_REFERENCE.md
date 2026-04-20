# Design System Quick Reference

## Color Classes

### Text Gradients
```html
<h1 class="text-gradient-primary">Gradient Text</h1>
```

### Backgrounds
```html
<div class="bg-gradient-subtle">Subtle gradient background</div>
<div class="bg-gradient-mesh">Mesh gradient background</div>
<div class="bg-pattern-dots">Dotted pattern background</div>
<div class="bg-pattern-grid">Grid pattern background</div>
```

## Typography Classes

### Display Text (Hero Titles)
```html
<h1 class="text-display-1">Largest Display</h1>
<h1 class="text-display-2">Medium Display</h1>
<h1 class="text-display-3">Small Display</h1>
```

### Headings
```html
<h2 class="text-heading-1">Main Heading</h2>
<h3 class="text-heading-2">Sub Heading</h3>
<h4 class="text-heading-3">Minor Heading</h4>
```

### Body Text
```html
<p class="text-body-lg">Large body text</p>
<p class="text-body">Regular body text</p>
<p class="text-body-sm">Small body text</p>
<span class="text-caption">LABEL TEXT</span>
```

## Button Components

### Primary Button
```html
<button class="btn-enhanced-primary">
  <span>Button Text</span>
  <svg class="w-5 h-5"><!-- icon --></svg>
</button>
```

### Secondary Button
```html
<button class="btn-enhanced-secondary">
  <span>Button Text</span>
</button>
```

## Card Components

### Enhanced Card
```html
<div class="card-enhanced">
  <!-- Card content -->
</div>
```

## Form Elements

### Input Field
```html
<input type="text" class="input-enhanced" placeholder="Enter text">
```

### Select Dropdown
```html
<select class="select-enhanced">
  <option>Option 1</option>
</select>
```

### Input with Error
```html
<input type="text" class="input-enhanced error">
```

### Input with Success
```html
<input type="text" class="input-enhanced success">
```

## Badge Components

```html
<span class="badge-enhanced badge-success">Success</span>
<span class="badge-enhanced badge-warning">Warning</span>
<span class="badge-enhanced badge-error">Error</span>
<span class="badge-enhanced badge-info">Info</span>
<span class="badge-enhanced badge-primary">Primary</span>
<span class="badge-enhanced badge-secondary">Secondary</span>
```

## Progress Bars

### Standard Progress
```html
<div class="progress-enhanced">
  <div class="progress-enhanced-fill" style="width: 60%"></div>
</div>
```

### Semantic Progress
```html
<div class="progress-enhanced">
  <div class="progress-enhanced-fill success" style="width: 80%"></div>
</div>

<div class="progress-enhanced">
  <div class="progress-enhanced-fill warning" style="width: 70%"></div>
</div>

<div class="progress-enhanced">
  <div class="progress-enhanced-fill error" style="width: 100%"></div>
</div>
```

## Utility Classes

### Shadows
```html
<div class="shadow-glow-primary">Primary glow</div>
<div class="shadow-glow-secondary">Secondary glow</div>
```

### Effects
```html
<div class="glass-effect">Glass morphism effect</div>
```

### Loading States
```html
<div class="skeleton-enhanced" style="height: 20px; width: 200px;"></div>
<div class="spinner-enhanced"></div>
```

## Layout Sections

### Hero Section
```html
<section class="hero-enhanced">
  <div class="absolute inset-0 -z-10 bg-gradient-mesh"></div>
  <div class="container mx-auto px-4 text-center relative z-10">
    <!-- Hero content -->
  </div>
</section>
```

### Gradient Section Background
```html
<section class="py-20 bg-gradient-subtle">
  <!-- Section content -->
</section>
```

## CSS Variables Reference

### Colors
- `--color-primary-600` - Main brand blue
- `--color-secondary-700` - Brand purple
- `--color-success` - Green
- `--color-warning` - Amber
- `--color-error` - Red
- `--color-gray-[50-950]` - Gray scale

### Gradients
- `--gradient-primary` - Primary gradient
- `--gradient-secondary` - Secondary gradient
- `--gradient-brand` - Brand gradient (primary to secondary)
- `--gradient-subtle` - Subtle background gradient

### Spacing
- `--spacing-xs` to `--spacing-3xl` (0.25rem to 4rem)

### Border Radius
- `--radius-xs` to `--radius-3xl` (0.25rem to 2rem)
- `--radius-full` - Fully rounded (9999px)

### Shadows
- `--shadow-primary-sm` to `--shadow-primary-xl`
- `--shadow-secondary-sm` to `--shadow-secondary-lg`
- `--shadow-elevated` - Maximum elevation

### Typography
- `--font-size-xs` to `--font-size-7xl`
- `--font-weight-light` to `--font-weight-black`
- `--line-height-tight` to `--line-height-loose`
- `--letter-spacing-tighter` to `--letter-spacing-widest`

### Animation
- `--duration-instant` to `--duration-slower` (100ms to 700ms)
- `--ease-linear`, `--ease-in`, `--ease-out`, `--ease-in-out`, `--ease-bounce`, `--ease-smooth`

## Best Practices

1. **Consistency**: Use design system classes instead of custom styles
2. **Hierarchy**: Follow typography scale for proper visual hierarchy
3. **Spacing**: Use spacing variables for consistent rhythm
4. **Colors**: Use semantic colors for status/feedback
5. **Interactions**: All interactive elements should have hover states
6. **Accessibility**: Maintain proper contrast ratios and focus states
7. **Performance**: Prefer CSS animations over JavaScript
8. **Responsive**: Test on mobile, tablet, and desktop viewports

## Examples

### Committee Card
```html
<div class="card-enhanced">
  <div class="flex items-start justify-between mb-4">
    <h3 class="font-display text-3xl font-bold text-gradient-primary">UNGA</h3>
    <span class="badge-enhanced badge-success">Available</span>
  </div>
  <h4 class="text-heading-3 mb-2">United Nations General Assembly</h4>
  <p class="text-body-sm mb-6">English • 30 Seats</p>
  <div class="space-y-3">
    <div class="flex justify-between text-sm">
      <span class="text-body-sm">Capacity</span>
      <span class="font-semibold">8/30</span>
    </div>
    <div class="progress-enhanced">
      <div class="progress-enhanced-fill" style="width: 27%"></div>
    </div>
  </div>
</div>
```

### CTA Section
```html
<section class="py-20">
  <div class="container mx-auto px-4">
    <div class="relative rounded-3xl overflow-hidden p-16 text-center shadow-elevated">
      <div class="absolute inset-0 bg-gradient-brand"></div>
      <div class="absolute inset-0 bg-pattern-dots opacity-10"></div>
      <div class="relative z-10 text-white">
        <h2 class="text-display-2 mb-6">Ready to Join?</h2>
        <p class="text-xl opacity-95 mb-10">Secure your spot today</p>
        <a href="/register.html" class="btn-enhanced-primary">
          <span>Register Now</span>
          <svg class="w-5 h-5"><!-- arrow icon --></svg>
        </a>
      </div>
    </div>
  </div>
</section>
```

### Form Field
```html
<div>
  <label class="block text-sm font-semibold mb-2 text-gray-700">
    Email Address <span class="text-error">*</span>
  </label>
  <input
    type="email"
    class="input-enhanced"
    placeholder="your@email.com"
  >
  <p class="text-sm text-error mt-2 hidden font-medium" id="email-error"></p>
</div>
```
