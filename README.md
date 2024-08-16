# Poultry Management Website

A comprehensive web application designed to manage poultry records, including tracking bills, dead birds, and other related metrics. Built using Django and Bootstrap, this project provides an intuitive interface for monitoring poultry health, managing finances, and analyzing data.

## Features

- **User Authentication**: Secure login and user management.
- **Poultry Tracking**: Manage and view details about different poultry.
- **Bill Management**: Submit and track bills related to poultry, including expenses for feed, medicine, and more.
- **Dead Bird Tracking**: Record and analyze information about dead birds.
- **Real-time Data**: View updated totals and statistics.
- **Responsive Design**: User-friendly interface using Bootstrap.

## Technologies Used

- **Backend**: Django
- **Frontend**: HTML, CSS, Bootstrap
- **Database**: SQLite 
- **Deployment**: [poultry.pythonanywhere.com ](https://poultry.pythonanywhere.com/)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/kushal1o1/PMS.git
   cd PMS 
   ```
2. **Create and Activate a Virtual Environment**: 
```bash
   python -m venv venv source venv/bin/activate # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a Superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```
7. **Access the Application**:
   Open your browser and go to `http://127.0.0.1:8000/` to view the application.
## Configuration

- **Settings**: Modify `settings.py` for database configuration, static files, and other settings.
- **Media Files**: Ensure `MEDIA_URL` and `MEDIA_ROOT` are configured to serve media files.

## Admin Interface

- **Access Admin Panel**: Navigate to `http://127.0.0.1:8000/admin/` to manage poultry, bills, and dead bird records.

- **Models**:
  - **Poultry**: Manage poultry records.
  - **BillPost**: Track and manage bills.
  - **Total**: View and manage totals for each poultry.
  - **DeadInfo**: Record and analyze dead birds.
