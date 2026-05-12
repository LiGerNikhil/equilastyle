# EQUILA Fashion - Premium E-commerce Platform

A sophisticated Django-based e-commerce website featuring 3D video storytelling, premium fashion collections, and modern web technologies.

## Features

### 🎬 Video Storytelling Homepage
- **Three.js Integration**: Custom canvas-based video frame rendering
- **Scroll-based Animation**: Video frames change based on scroll position
- **GSAP Animations**: Smooth transitions and anti-gravity effects
- **Parallax Effects**: Google-inspired parallax scrolling

### 🛍️ E-commerce Functionality
- **Product Management**: Categories, brands, variants, and inventory
- **Shopping Cart**: Dynamic cart with real-time updates
- **User Authentication**: Registration, login, and profile management
- **Order Processing**: Complete checkout flow
- **Reviews & Ratings**: Customer feedback system

### 🎨 Premium Design
- **Responsive Layout**: Mobile-first design with Bootstrap 5
- **Modern UI/UX**: Clean, professional interface
- **Interactive Elements**: Hover effects, animations, and micro-interactions
- **Premium Collections**: Featured and premium product sections

### 🏗️ Technical Architecture
- **Django 4.2**: Modern Python web framework
- **Modular Structure**: Organized apps for scalability
- **Database Models**: SQLite for development, production-ready
- **Static Assets**: Optimized CSS and JavaScript

## Project Structure

```
equila-demo/
├── manage.py
├── requirements.txt
├── equila_fashion/          # Main Django project
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                # User management
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
├── products/                # Product catalog
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── cart/                    # Shopping cart
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── context_processors.py
├── orders/                  # Order management
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── blog/                    # Content management
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── templates/               # HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── products/
│   ├── cart/
│   └── orders/
└── static/                  # CSS, JS, and media
    ├── css/
    ├── js/
    ├── videos/
    └── media/
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### 1. Clone and Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 3. Collect Static Files
```bash
python manage.py collectstatic
```

### 4. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to view the application.

## Video Setup

### Video Requirements
- Place your video file at `static/videos/equila.mp4`
- Recommended resolution: 4K (3840x2160)
- Format: MP4 with H.264 codec
- Duration: 8 seconds (as specified in requirements)

### Key Video Timeline
- **0-2 seconds**: T-shirt showcase
- **2-4 seconds**: Jeans display
- **4-6 seconds**: Fashion model with complete outfit
- **6-8 seconds**: EQUILA brand business card

## Configuration

### Environment Variables
Create a `.env` file in the project root:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Admin Panel
Access the Django admin at `http://127.0.0.1:8000/admin/`
- Login with your superuser credentials
- Manage products, categories, brands, and orders
- Create and manage user accounts

## Features in Detail

### Video Storytelling
The homepage features an innovative scroll-based video experience:
- **Canvas Rendering**: Custom Three.js implementation for smooth video playback
- **Frame Extraction**: Optimized frame-by-frame rendering
- **Scroll Synchronization**: Video progress linked to page scroll
- **Text Overlays**: Dynamic text appears at specific timestamps

### Product Management
- **Categories**: Men, Women, Kids with gender-based filtering
- **Brands**: Premium brands (Adidas, Skechers, Bacabucci, Gucci)
- **Variants**: Size (XS-3XL) and color options
- **Pricing**: Regular and premium pricing with discount calculations

### Shopping Experience
- **Product Discovery**: Advanced filtering and search
- **Quick View**: Modal-based product previews
- **Cart Management**: Real-time cart updates with AJAX
- **Wishlist**: Save favorite items for later

### User Features
- **Authentication**: Secure login and registration
- **Profile Management**: Personal information and preferences
- **Order History**: Track past purchases
- **Reviews**: Rate and review products

## Customization

### Styling
- Edit `static/css/style.css` for custom styles
- Uses Bootstrap 5 with custom enhancements
- CSS variables for easy theme customization

### JavaScript
- Main functionality in `static/js/main.js`
- Three.js video handling in homepage template
- GSAP animations for smooth transitions

### Templates
- Base template: `templates/base.html`
- App-specific templates in respective directories
- Django template tags for dynamic content

## Deployment

### Production Considerations
- Set `DEBUG=False` in production
- Configure proper database (PostgreSQL recommended)
- Set up static file serving (AWS S3, CDN)
- Configure email settings for notifications
- Set up proper CORS and security headers

### Environment Setup
```bash
# Production dependencies
pip install gunicorn psycopg2-binary

# Environment variables
export DEBUG=False
export SECRET_KEY=your-production-secret
export DATABASE_URL=your-database-url
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
- Check the Django documentation
- Review the code comments
- Create an issue in the repository

## License

This project is for demonstration purposes. Please ensure you have proper licenses for all assets and dependencies.

---

**EQUILA Fashion** - Elevating Style Through Technology
