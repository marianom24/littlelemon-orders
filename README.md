
# :lemon: LittleLemon API 

Online food ordering system.
Menus with the possibility of ordering, filtering and searching items, distributed in pages.
Authentication and authorisation through user roles.




## :wrench: Tech Stack

- Django 4.2.14
- Django REST Framework 3.15.2
- djoser 2.2.3 for authentication 
- django-filter 24.3 for filtering and sorting


## :running:  Run Locally

Activate enviroment 

```bash
  pipenv shell
```

Install dependencies
```bash
  pipenv install
```

Run the server
```bash
  python manage.py runserver
```
## :star: Common endpoints

#### Get all menu items

```http
  GET /api/menu-items
```

| Method | Endpoint     | Description                |
| :-------- | :------- | :------------------------- |
| GET | `menu-items` | Return all menu items |

#### Get a menu item
```http
  GET /api/menu-items/${id}
```

| Method | Endpoint     | Description                |
| :-------- | :------- | :------------------------- |
| GET | `menu-items/${id}` | Return the items with that ID |

#### Get all categories

```http
  GET /api/categories
```

| Method | Endpoint     | Description                |
| :-------- | :------- | :------------------------- |
| GET | `categories` | Return all menu categories |

#### Get cart

```http
  GET /api/cart
```

| Method | Endpoint     | Description                |
| :-------- | :------- | :------------------------- |
| GET | `cart` | Return all items in the current user's cart|

#### Create order

```http
  POST /api/order
```

| Method | Endpoint     | Description                |
| :-------- | :------- | :------------------------- |
| POST | `order` | Gets all the cart's items and put in an order|


## :passport_control: Authentication
Usual endpoints

### Create user

```http
  POST /auth/users
```

Example request

```bash
  {
  "username": "someuser",
  "email": "some@user.com",
  "password": "somepass"
  }
```

| Method | Endpoint     | Description                |
| :-------- | :------- | :------------------------- |
| POST | `order` | Gets all the cart's items and put in an order|

Example response

```bash
  {
  "username": "someuser",
  "email": "some@user.com",
  }
```

### Get auth token

```http
  POST /auth/token/login
```

Example request

```bash
  {
  "username": "someuser",
  "password": "somepass"
   }
```

| Method | Endpoint     | Description                |
| :-------- | :------- | :------------------------- |
| POST | `auth/token/login` |Return a token when post login credentials|

Example response

```bash
  {
  "auth_token": "e898d4c71476ed4963b35d40deb5eef1502cb5ed"
  }
```
