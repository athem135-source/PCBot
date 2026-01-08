# Feedback Directory

## Purpose
Stores user feedback submissions organized by rating.

## Directory Structure

### `1_star/` - Poor Experience
Feedback from users who rated their experience 1 star.

### `2_star/` - Below Average
Feedback from users who rated their experience 2 stars.

### `3_star/` - Average
Feedback from users who rated their experience 3 stars.

### `4_star/` - Good Experience (if exists)
Feedback from users who rated their experience 4 stars.

### `5_star/` - Excellent Experience (if exists)
Feedback from users who rated their experience 5 stars.

## File Format

Each feedback file is named:
```
YYYYMMDD_HHMMSS_Username.txt
```

Example: `20251031_113636_Guest.txt`

## Usage

Feedback is automatically collected when users:
1. Submit a rating in the widget interface
2. Provide optional comments
3. Click submit

Files are created automatically by the Flask backend (`widget_api.py`).

## Analysis

Review feedback files to:
- Identify pain points and issues
- Track user satisfaction trends
- Improve accuracy and user experience
- Validate system performance
